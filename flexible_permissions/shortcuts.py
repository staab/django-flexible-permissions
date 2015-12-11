# Include ANY and NULL as part of the public api
from flexible_permissions._utils import (
    ANY,
    NULL,
    validate_roles_with_targets,
    get_multi_crud_query,
    get_single_crud_kwargs,
)
from flexible_permissions.models import Permission

"""
Get
"""


def get_perms(*args, **kwargs):
    """
    Gets all Permissions matching the query.
    Accepts role, agent, and target kwargs.
    """
    return Permission.objects.filter(get_multi_crud_query(*args, **kwargs))


"""
Create
"""


def add_perm(role, agent, target):
    """
    Adds a single Permission matching the arguments.
    Accepts role, agent, and target kwargs.
    If the Permission already exists, it will retrieve it instead.
    """
    # Make sure we're not adding bad data
    validate_roles_with_targets(role, target)

    # If it already exists, this is a duplicate, so ignore it.
    query_kwargs = get_single_crud_kwargs(role, agent, target)
    return Permission.objects.get_or_create(**query_kwargs)[0]


"""
Delete
"""


def remove_perm(*args, **kwargs):
    """
    Removes all Permissions matching the arguments.
    Accepts role, agent, and target kwargs.
    """
    query_kwargs = get_single_crud_kwargs(*args, **kwargs)
    Permission.objects.filter(**query_kwargs).delete()


"""
Update
"""


def assign_role(role, agent, target):
    """
    Removes role for target from all other agents and assigns it to the
    given agent.
    """
    remove_perm(role, ANY, target)
    add_perm(role, agent, target)
