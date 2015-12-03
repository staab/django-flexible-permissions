# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0003_auto_20151014_1541'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='agent_type',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to='contenttypes.ContentType', null=True),
        ),
        migrations.AlterField(
            model_name='permission',
            name='target_type',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, to='contenttypes.ContentType'),
        ),
    ]
