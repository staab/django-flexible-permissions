Flexible Permissions is a Django app that combines object-level table permissions with model relations to avoid normalization of data while providing an extremely flexible, declarative permissions model.

# Installation

Add "flexible_permissions" to INSTALLED_APPS:

```
    INSTALLED_APPS = (
        ...
        'flexible_permissions',
    )
```

Run `python manage.py migrate` to create the models.

# Configuration
