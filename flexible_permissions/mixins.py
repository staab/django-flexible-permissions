from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Model

from flexible_permissions.models import Permission
from flexible_permissions.query import (
    PermTargetQuerySet,
    PermAgentQuerySet,
)


class PermTarget(Model):
    target_perms = GenericRelation(
        Permission,
        object_id_field='target_id',
        content_type_field='target_type'
    )

    objects = PermTargetQuerySet.as_manager()

    class Meta:
        abstract = True


class PermAgent(Model):
    agent_perms = GenericRelation(
        Permission,
        object_id_field='agent_id',
        content_type_field='agent_type'
    )

    objects = PermAgentQuerySet.as_manager()

    class Meta:
        abstract = True
