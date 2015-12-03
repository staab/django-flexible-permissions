# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(max_length=255)),
                ('agent_id', models.PositiveIntegerField(null=True, blank=True)),
                ('target_id', models.PositiveIntegerField()),
                ('agent_type', models.ForeignKey(related_name='+', on_delete=models.deletion.PROTECT, blank=True, to='contenttypes.ContentType', null=True)),
                ('target_type', models.ForeignKey(related_name='+', on_delete=models.deletion.PROTECT, to='contenttypes.ContentType')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='permission',
            unique_together=set([('role', 'agent_type', 'agent_id', 'target_type', 'target_id')]),
        ),
    ]
