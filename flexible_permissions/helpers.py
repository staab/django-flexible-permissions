from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.db.models import Q

from permissions.utils import OMIT, NULL, generic_in, normalize_value
from permissions.models import Permission


def _get_single_crud_kwargs(role, agent, target):
    kwargs = {'role': role}

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


def _get_multi_crud_query(role, agent, target):
    query = Q(role__in=normalize_value(role))

    if agent is NULL:
        query = query & Q(agent_id__isnull=True)
    elif agent is not OMIT:
        query = query & generic_in('agent', normalize_value(agent))

    if target is NULL:
        query = query & Q(taret_id__isnull=True)
    elif target is not OMIT:
        query = query & generic_in('target', normalize_value(target))

    return query

"""
Get
"""


def get_perms(role, agent=OMIT, target=OMIT):
    query = _get_multi_crud_query(role, agent, target)
    return Permission.objects.filter(query)


"""
Create
"""


def add_perm(role, agent=NULL, target=NULL):
    kwargs = _get_single_crud_kwargs(role, agent, target)

    # If it already exists, this is a duplicate, so ignore it.
    return Permission.objects.get_or_create(**kwargs)[0]


"""
Delete
"""


def remove_perm(role, agent=NULL, target=NULL):
    kwargs = _get_single_crud_kwargs(role, agent, target)
    Permission.objects.filter(**kwargs).delete()


"""
Update
"""


def assign_role(role, agent, target):
    # Remove role from any other agent that might have it
    remove_perm(role, agent=OMIT, target=target)
    add_perm(role, agent, target)
