from django.db.models import Q, QuerySet

from itertools import chain

from flexible_permissions.agents import normalize_agent
from flexible_permissions.relations import (
    get_related_target_prefixes,
    get_related_agent_prefixes,
)
from flexible_permissions.roles import actions_to_roles
from flexible_permissions._utils import (
    ANY,
    NULL,
    ensure_plural,
    generic_in,
    get_key,
    filter_isnull,
    is_value,
    normalize_value,
    get_model_name,
    validate_roles_with_targets,
)


def define_filter(key):
    def decorator(fn):
        def wrapped(queryset, value=ANY, prefix=None):
            if value is ANY:
                return Q()

            if value is NULL:
                return filter_isnull(key, prefix)

            # The fn should return a Q object.
            return fn(queryset, **{key: value, 'prefix': prefix})

        return wrapped

    return decorator


class PermQuerySet(QuerySet):

    """
    Query Building stuff
    """

    def _get_filter(self, key, value):
        return generic_in(key, ensure_plural(value))

    @define_filter('role')
    def _get_role_query(self, role, prefix):
        return Q(**{get_key('role', prefix, 'in'): role})

    @define_filter('agent')
    def _get_agent_query(self, agent, prefix):
        # Always add in isnull
        return (
            filter_isnull('agent', prefix) |
            self._get_filter(get_key('agent', prefix), agent)
        )

    @define_filter('target')
    def _get_target_query(self, target, prefix):
        return self._get_filter(get_key('target', prefix), target)

    def _get_query(
        self,
        role=ANY,
        agent=ANY,
        target=ANY,
        prefix=None
    ):
        """
        This constructs a query for the filter on permissions.
        """
        return (
            self._get_role_query(role, prefix) &
            self._get_agent_query(agent, prefix) &
            self._get_target_query(target, prefix)
        )

    """
    Query execution
    """

    def _query_separate(self, queries):
        """
        Combining too many queries can cause horrendous LEFT JOINS
        and we end up scanning millions of rows. Instead, query each
        separately as ids, then query again to get all objects
        """

        # Reset ordering to avoid extra joins
        queryset = self.order_by('pk')

        ids = []
        for query in queries:
            ids.append(queryset.filter(query).values_list('id', flat=True))

        # Keep the ordering here since this is the result
        return self.filter(id__in=set(chain(*ids)))

    def _query_together(self, queries):
        """
        This queries everything all at once. This is safe if we're joining
        tables in only a couple different directions.
        """
        return reduce(
            lambda queryset, query: queryset | self.filter(query),
            queries,
            self.none()
        )

    def _query_perms(self,
        roles,
        get_related_prefixes,
        perms_name,
        force_separate,
        agent=ANY,
        target=ANY
    ):
        """
        This is an abstraction used by subclasses to query permissions.

        Roles will be normalized to a list of roles.

        force_separate is an optimization. If you know you are going
        to have multiple left joins, this will speed things up.

        Either agent or target can be provided. It's assumed that the
        queryset to be retrieved is the thing not provided.
        """
        # Normalize inputs
        roles = normalize_value(roles)
        agent = normalize_value(agent)
        target = normalize_value(target)

        # Get all possible related queries we're doing
        related_prefixes = (
            get_related_prefixes(self, perms_name, *roles)
            if is_value(roles) else
            [perms_name]
        )

        # Create a query for each related prefix
        queries = [
            self._get_query(roles, agent, target, prefix=prefix)
            for prefix in related_prefixes
        ]

        # Aggregate the queries. Query together if we don't have any
        # divergent left joins.
        query_together = (
            not force_separate and
            len(related_prefixes) <= 1 and
            perms_name in related_prefixes
        )

        if query_together:
            results = self._query_together(queries)
        else:
            results = self._query_separate(queries)

        return results


class PermTargetQuerySet(PermQuerySet):
    """
    This is a queryset class that exposes methods to get a related target
    via the permissions table. The methods should be read as
    "Get a target for an agent with role x."
    """
    def _prefix_actions(self, actions):
        """
        Prepend this model's name as prefix. This enforces more correct
        configuration when registering role/action mappings.
        """
        if not is_value(actions):
            return actions

        result = []
        for action in ensure_plural(actions):
            if "." in action:
                raise ValueError(
                    "Prefixes are inferred. Register this with its own "
                    "actions."
                )

            result.append("%s.%s" % (get_model_name(self.model), action))

        return result

    def for_role(
        self,
        roles=ANY,
        agent=ANY,
        infer_agents=True,
        force_separate=False
    ):
        """
        This filters permission targets by the given agent.

        infer_agents is an optimization. If you know you don't need the
        authority of any related agents, set it to false.
        """
        return self._query_perms(
            roles=roles,
            get_related_prefixes=get_related_target_prefixes,
            perms_name='target_perms',
            force_separate=force_separate,
            agent=normalize_value(
                agent,
                normalize_agent,
                infer_agents=infer_agents
            )
        )

    def for_action(self, actions=ANY, *args, **kwargs):
        roles = actions_to_roles(self._prefix_actions(actions))
        return self.for_role(roles, *args, **kwargs)


class PermAgentQuerySet(PermQuerySet):
    """
    This is a queryset class that exposes methods to get a related agent
    via the permissions table. The methods should be read as
    "Get an agent with role x and target y."
    """
    def _validate_actions(self, actions):
        if not is_value(actions):
            return actions

        actions = normalize_value(actions)

        if [action for action in actions if "." not in action]:
            raise ValueError("Prefixes are required since target is optional.")

        return actions

    def with_role(self, roles=ANY, target=ANY, force_separate=False):
        """
        This filters permission agents by the given target.
        """
        validate_roles_with_targets(roles, target)

        return self._query_perms(
            roles=roles,
            get_related_prefixes=get_related_agent_prefixes,
            perms_name='agent_perms',
            force_separate=force_separate,
            target=target
        )

    def with_action(self, actions=ANY, *args, **kwargs):
        roles = actions_to_roles(self._validate_actions(actions))
        return self.with_role(roles, *args, **kwargs)
