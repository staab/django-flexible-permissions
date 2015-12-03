# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def datamigration(apps, schema_editor):
    Permission = apps.get_model('permissions', 'Permission')
    permissions = Permission.objects.filter(role='plan.settings_manager')

    for permission in permissions:
        Permission.objects.get_or_create(
            role='plan.workflow_manager',
            agent_id=permission.agent_id,
            agent_type=permission.agent_type,
            target_id=permission.target_id,
            target_type=permission.target_type
        )


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0002_auto_20151014_1541'),
    ]

    operations = [
        migrations.RunPython(datamigration)
    ]
