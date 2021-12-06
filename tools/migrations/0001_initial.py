# Generated by Django 3.0.14 on 2021-12-07 15:55

import core.fields
import datetime
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExtractModel',
            fields=[
                ('validity_from', core.fields.DateTimeField(db_column='ValidityFrom', default=datetime.datetime.now)),
                ('validity_to', core.fields.DateTimeField(blank=True, db_column='ValidityTo', null=True)),
                ('legacy_id', models.IntegerField(blank=True, db_column='LegacyID', null=True)),
                ('id', models.AutoField(db_column='ExtractID', primary_key=True, serialize=False)),
                ('uuid', models.CharField(db_column='ExtractUUID', default=uuid.uuid4, max_length=36, unique=True)),
                ('type', models.SmallIntegerField(db_column='ExtractType', default=0)),
                ('direction', models.SmallIntegerField(db_column='ExtractDirection', default=0)),
                ('sequence', models.IntegerField(db_column='ExtractSequence', default=0)),
                ('date', models.DateTimeField(db_column='ExtractDate', default=datetime.datetime.now)),
                ('filename', models.CharField(db_column='ExtractFileName', max_length=255)),
                ('folder', models.CharField(db_column='ExtractFolder', max_length=255)),
                ('app_version', models.DecimalField(db_column='AppVersionBackend', decimal_places=2, default=0, max_digits=3)),
                ('audit_user_id', models.IntegerField(db_column='AuditUserID')),
            ],
            options={
                'db_table': 'tblExtracts',
                'managed': False,
            },
        ),
    ]
