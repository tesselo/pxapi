# Generated by Django 3.1.6 on 2021-03-03 09:00

import uuid

import django.db.models.deletion
import pipeline.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("batch", "0003_auto_20210206_1443"),
        ("pipeline", "0007_auto_20210223_1706"),
    ]

    operations = [
        migrations.CreateModel(
            name="Prediction",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Short name of the object.", max_length=250
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Detailed description of the object.",
                    ),
                ),
                ("generator_arguments", models.JSONField(blank=True, default=dict)),
                (
                    "generator_arguments_file",
                    models.FileField(
                        editable=False,
                        null=True,
                        upload_to=pipeline.models.training_generator_arguments_file_upload_to,
                    ),
                ),
                (
                    "batchjob_create_catalog",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="prediction_catalog",
                        to="batch.batchjob",
                    ),
                ),
                (
                    "batchjob_predict",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="batch.batchjob",
                    ),
                ),
                (
                    "kerasmodel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="pipeline.kerasmodel",
                    ),
                ),
                (
                    "pixelsdata",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="pipeline.pixelsdata",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
