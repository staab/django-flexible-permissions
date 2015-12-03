from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

import operator

"""
Unique values for differentiating between
not filtering and constraining to isnull
"""


class NOFILTER(object):
    pass


class ISNULL(object):
    pass


"""
Basic utility functions
"""


def is_plural(value):
    """
    Whether a value is an iterable, excluding dicts.
    """
    return hasattr(value, '__iter__') and not isinstance(value, dict)


def identity(value):
    """
    Just yer regular old identity function
    """
    return value


def ensure_plural(value, remove_nones=True):
    """
    If value is singular, wraps it in an array.
    If None is in value and remove_nones is True, None is filtered out.
    """
    if not is_plural(value):
        value = [value]

    if remove_nones:
        value = filter(identity, value)

    return value


"""
Generic query building functions
"""


def generic_in(key, items):
    """
    Creates a the equivalent of an __in query for the given items.
    Items may be heterogeneous, but they must be Django models.
    """
    clauses = [
        Q(**{
            "%s_id" % key: item.id,
            "%s_type" % key: ContentType.objects.get_for_model(item),
        })
        for item in items
    ]

    # Match nothing for base query
    return reduce(operator.or_, clauses, Q(**{'id__isnull': True}))


def get_single_crud_kwargs(role, agent, target):
    """
    Gets a dict for filtering Permissions by Role, Agent, and Target.
    All arguments are optional, but must be explicitly provided.
    """
    kwargs = {}

    if role:
        kwargs['role'] = role

    if agent:
        kwargs.update({
            'agent_type': ContentType.objects.get_for_model(agent),
            'agent_id': agent.id
        })

    if target:
        kwargs.update({
            'target_type': ContentType.objects.get_for_model(target),
            'target_id': target.id
        })

    return kwargs


def get_multi_crud_query(role=ISNULL, agent=ISNULL, target=ISNULL):
    """
    Gets a query object for the given role, agent, and target. Any of the
    three may be plural; a generic_in will be used.
    """
    query = Q()

    if role is ISNULL:
        query = query & Q(role__isnull=True)
    elif role is not NOFILTER:
        query = query & Q(role__in=ensure_plural(role))

    if agent is ISNULL:
        query = query & Q(agent_id__isnull=True)
    elif agent is not NOFILTER:
        query = query & generic_in('agent', ensure_plural(agent))

    if target is ISNULL:
        query = query & Q(target_id__isnull=True)
    elif target is not NOFILTER:
        query = query & generic_in('target', ensure_plural(target))

    return query
