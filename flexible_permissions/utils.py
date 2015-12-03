from django.contrib.contenttypes.models import ContentType
from django.db import models

import operator

"""
Private helper functions
"""

# Differentiate between not filtering and constraining to isnull
OMIT = None
NULL = False


def is_plural(value):
    return hasattr(value, '__iter__')


def normalize_value(value):
    if value is OMIT:
        return []
    elif not is_plural(value):
        value = [value]

    return value


def generic_in(key, data):
    clauses = [
        models.Q(**{
            "%s_id" % key: item.id,
            "%s_type" % key: ContentType.objects.get_for_model(item),
        })
        for item in data
    ]

    # Match nothing for base query
    base_query = models.Q(**{'id__isnull': True})
    return reduce(operator.or_, clauses, base_query)
