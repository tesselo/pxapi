# Generated by Django 3.1.6 on 2021-02-11 17:59

from django.db import migrations, models
import django.db.models.deletion
import pipeline.models


class Migration(migrations.Migration):

    dependencies = [
        ("batch", "0003_auto_20210206_1443"),
        ("pipeline", "0004_auto_20210207_2230"),
    ]

    operations = [
        migrations.RenameField(
            model_name="kerasmodel",
            old_name="definition",
            new_name="model_configuration",
        ),
        migrations.RemoveField(
            model_name="kerasmodel",
            name="model_h5",
        ),
        migrations.RemoveField(
            model_name="kerasmodel",
            name="model_json",
        ),
        migrations.AddField(
            model_name="kerasmodel",
            name="batchjob_train",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="batch.batchjob",
            ),
        ),
        migrations.AddField(
            model_name="kerasmodel",
            name="model_compile_arguments",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="kerasmodel",
            name="model_compile_arguments_file",
            field=models.FileField(
                editable=False,
                null=True,
                upload_to=pipeline.models.model_compile_arguments_file_upload_to,
            ),
        ),
        migrations.AddField(
            model_name="kerasmodel",
            name="model_configuration_file",
            field=models.FileField(
                editable=False,
                null=True,
                upload_to=pipeline.models.model_configuration_file_upload_to,
            ),
        ),
        migrations.AddField(
            model_name="kerasmodel",
            name="model_fit_arguments",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="kerasmodel",
            name="model_fit_arguments_file",
            field=models.FileField(
                editable=False,
                null=True,
                upload_to=pipeline.models.model_fit_arguments_file_upload_to,
            ),
        ),
    ]
