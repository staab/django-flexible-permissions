from flexible_permissions._utils import (
    get_model_class,
    ensure_plural,
    is_value,
    invert,
)

_relation_registry = {}


def register_relation(cls, paths):
    _relation_registry[cls] = paths


def get_relation_paths(cls):
    """
    Return paths registered for the given class or any of its subclasses
    """

    results = {}
    [
        results.update(paths)
        for registered_cls, paths in _relation_registry.iteritems()
        if cls == registered_cls or issubclass(cls, registered_cls)
    ]

    return results


def _get_model_class(target):
    if not is_value(target):
        return None

    model_classes = list(set(map(get_model_class, ensure_plural(target))))

    if len(model_classes) > 1:
        raise ValueError("Heterogenous targets not allowed.")

    return model_classes[0]


def get_related_paths_by_role(model_class, roles):
    """
    Select what paths to used based on what roles were passed.
    The first part of the role should be the key for the path
    to the object associated with that role.
    """
    role_prefixes = [
        role.split(".")[0]
        for role in filter(invert(is_value), ensure_plural(roles))
    ]

    return [
        path for key, path in get_relation_paths(model_class).items()
        if key in role_prefixes
    ]


def get_related_prefixes(combine, perms_name, roles, origin, relation):
    """
    Gets prefixes for inferring relations from the origin to the relation
    """
    prefixes = []

    # If the origin has a relation to Permission, add the perms_name in
    if perms_name in _get_model_class(origin)._meta.get_all_field_names():
        prefixes.append(perms_name)

    # Add all prefixes based on roles relevant for the relation
    for path in get_related_paths_by_role(_get_model_class(relation), roles):
        prefixes.append(combine('__', perms_name, path))

    return set(prefixes)
