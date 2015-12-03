from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Q, QuerySet, Model

from itertools import chain
import pydash

from flexible_permissions.agents import normalize_agent
from flexible_permissions.models import Permission
from flexible_permissions.relations import (
    get_related_target_prefixes,
    get_related_agent_prefixes,
)
from flexible_permissions.roles import actions_to_roles
from flexible_permissions.utils import (
    OMIT,
    NULL,
    normalize_value,
    generic_in
)


def get_key(key, prefix=None, suffix=None):
    prefix = "%s__" % prefix if prefix is not None else ''
    suffix = "__%s" % suffix if suffix is not None else ''

    return "%s%s%s" % (prefix, key, suffix)


def filter_isnull(key, prefix):
    # Gotta add id to avoid reverse relation errors
    if key != 'role':
        key += '_id'

    # Return just a null check
    return Q(**{get_key(key, prefix, 'isnull'): True})


def define_filter(key):
    def decorator(fn):
        def wrapped(queryset, value=OMIT, prefix=None):
            if value is OMIT:
                return Q()

            # If value isn't OMIT, but it's empty, it's NULL. We're done.
            if value == [] or value is NULL:
                return filter_isnull(key, prefix)

            # The fn should return a Q object.
            return fn(queryset, **{key: value, 'prefix': prefix})

        return wrapped

    return decorator


class PermProxyQuerySet(QuerySet):

    """
    Query Building stuff
    """

    def _get_filter(self, key, value):
        value = normalize_value(value)

        # If we didn't have any values, return an empty query
        if len(value) == 0:
            return Q()

        return generic_in(key, value)

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

    def _get_query(self, role=OMIT, agent=OMIT, target=OMIT, prefix=None):
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

    def _query_perms(
        self,
        roles,
        get_related_prefixes,
        perms_name,
        force_separate,
        agent=OMIT,
        target=OMIT
    ):
        """
        This is an abstraction used by subclasses to query permissions.

        Roles will be normalized to a list of roles.

        force_separate is an optimization. If you know you are going
        to have multiple left joins, this will speed things up.

        Either agent or target can be provided. It's assumed that the
        queryset to be retrieved is the thing not provided.
        """
        # Normalize roles
        roles = normalize_value(roles)

        # Get all possible related queries we're doing
        related_prefixes = get_related_prefixes(self, perms_name, *roles)

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


class PermProxyTargetQuerySet(PermProxyQuerySet):
    """
    This is a queryset class that exposes methods to get a related target
    via the permissions table. The methods should be read as
    "Get a target for an agent with role x."
    """
    def _get_action_prefix(self):
        return self.model._meta.verbose_name.replace(' ', '_')

    def _prefix_actions(self, values):
        """
        Prepend this model's name as prefix. This enforces more correct
        configuration when registering role/action mappings.
        """
        result = []
        for value in normalize_value(values):
            assert "." not in value, (
                "Prefixes are inferred. Register this with its own actions."
            )

            result.append("%s.%s" % (self._get_action_prefix(), value))

        return result

    def for_role(
        self,
        roles=OMIT,
        agent=OMIT,
        infer_agents=True,
        force_separate=False
    ):
        """
        This filters permission targets by the given agent.

        infer_agents is an optimization. If you know you don't need the
        authority of any related agents, set it to false.
        """
        # Get any derivative agents
        agent = normalize_agent(agent, infer_agents=infer_agents)

        # If we have any superusers, they get to use anything they want
        supr = pydash.find(
            agent,
            lambda agent: getattr(agent, 'is_superuser', None)
        )

        if supr:
            return self.all()

        return self._query_perms(
            roles=roles,
            get_related_prefixes=get_related_target_prefixes,
            perms_name='target_perms',
            force_separate=force_separate,
            agent=agent
        )

    def for_action(self, actions=OMIT, *args, **kwargs):
        roles = actions_to_roles(self._prefix_actions(actions))
        return self.for_role(roles, *args, **kwargs)


class PermProxyAgentQuerySet(PermProxyQuerySet):
    """
    This is a queryset class that exposes methods to get a related agent
    via the permissions table. The methods should be read as
    "Get an agent with role x and target y."
    """
    def with_role(self, roles=OMIT, target=OMIT, force_separate=False):
        """
        This filters permission agents by the given target.
        """
        return self._query_perms(
            roles=roles,
            get_related_prefixes=get_related_agent_prefixes,
            perms_name='agent_perms',
            force_separate=force_separate,
            target=target
        )

    def with_action(self, actions=OMIT, *args, **kwargs):
        return self.with_role(actions_to_roles(actions), *args, **kwargs)


class PermProxyTarget(Model):
    target_perms = GenericRelation(
        Permission,
        object_id_field='target_id',
        content_type_field='target_type'
    )

    objects = PermProxyTargetQuerySet.as_manager()

    class Meta:
        abstract = True


class PermProxyAgent(Model):
    agent_perms = GenericRelation(
        Permission,
        object_id_field='agent_id',
        content_type_field='agent_type'
    )

    objects = PermProxyAgentQuerySet.as_manager()

    class Meta:
        abstract = True
