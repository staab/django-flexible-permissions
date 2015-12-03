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


def get_related_target_prefixes(queryset, perms_name, *roles):
    paths = get_relation_paths(queryset.model)
    prefixes = []

    if perms_name in queryset.model._meta.get_all_field_names():
        prefixes.append(perms_name)

    for role in roles:
        role_prefix = role.split(".")[0]

        # Add in the path to the related object, plus perm
        if role_prefix in paths:
            if not isinstance(paths[role_prefix], list):
                paths[role_prefix] = [paths[role_prefix]]
            for path in paths[role_prefix]:
                prefixes.append(path + '__' + perms_name)

    return set(prefixes)


def get_related_agent_prefixes(queryset, perms_name, *roles):
    prefixes = []

    if perms_name in queryset.model._meta.get_all_field_names():
        prefixes.append(perms_name)

    return set(prefixes)
