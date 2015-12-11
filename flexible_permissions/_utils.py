from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q

import operator

"""
Unique values for differentiating between
not filtering and constraining to isnull
"""


class ANY(object):
    pass


class NULL(object):
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


def get_model_class(value):
    if isinstance(value, ContentType):
        model_class = value.model_class()
    elif isinstance(value, models.Model):
        model_class = value.__class__
    elif isinstance(value, models.QuerySet):
        model_class = value.model
    elif issubclass(value, models.Model):
        model_class = value
    elif issubclass(value, models.BaseManager):
        model_class = value.model
    else:
        raise TypeError("Invalid value passed: %s" % value)

    return model_class


def get_model_name(value):
    return get_model_class(value)._meta.verbose_name.replace(' ', '_')

"""
Generic query building functions
"""


def get_key(key, prefix=None, suffix=None):
    prefix = "%s__" % prefix if prefix is not None else ''
    suffix = "__%s" % suffix if suffix is not None else ''

    return "%s%s%s" % (prefix, key, suffix)


def filter_isnull(key, prefix=None):
    # Gotta add id to avoid reverse relation errors
    if key != 'role':
        key += '_id'

    # Return just a null check
    return Q(**{get_key(key, prefix, 'isnull'): True})


def is_value(value):
    return value not in [NULL, ANY]


def normalize_value(value, fn=ensure_plural, *args, **kwargs):
    return fn(value, *args, **kwargs) if is_value(value) else value


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


def validate_roles_with_targets(roles, targets):
    if not is_value(roles) or not is_value(targets):
        return

    for target in normalize_value(targets):
        target_name = get_model_name(target)

        for role in normalize_value(roles):
            role_name = role.split(".")[0]
            if role_name != target_name:
                raise ValueError("Role %s is invalid for %s" % (
                    role_name,
                    target_name
                ))


def get_single_crud_kwargs(role, agent, target):
    """
    Gets a dict for filtering Permissions by Role, Agent, and Target.
    All arguments are optional, but must be explicitly provided.
    """
    kwargs = {}

    if role is NULL:
        kwargs['role__isnull'] = True
    elif is_value(role):
        kwargs['role'] = role

    if agent is NULL:
        kwargs['agent_id__isnull'] = True
    elif is_value(agent):
        kwargs.update({
            'agent_type': ContentType.objects.get_for_model(agent),
            'agent_id': agent.id
        })

    if target is NULL:
        kwargs['target_id__isnull'] = True
    elif is_value(target):
        kwargs.update({
            'target_type': ContentType.objects.get_for_model(target),
            'target_id': target.id
        })

    return kwargs


def get_multi_crud_query(role=NULL, agent=NULL, target=NULL):
    """
    Gets a query object for the given role, agent, and target. Any of the
    three may be plural; a generic_in will be used.
    """
    query = Q()

    if role is NULL:
        query = query & Q(role__isnull=True)
    elif is_value(role):
        query = query & Q(role__in=ensure_plural(role))

    if agent is NULL:
        query = query & Q(agent_id__isnull=True)
    elif is_value(agent):
        query = query & generic_in('agent', ensure_plural(agent))

    if target is NULL:
        query = query & Q(target_id__isnull=True)
    elif is_value(target):
        query = query & generic_in('target', ensure_plural(target))

    return query
