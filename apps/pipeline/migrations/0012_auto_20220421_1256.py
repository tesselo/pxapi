# Generated by Django 3.1.13 on 2022-04-21 12:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("batch", "0006_auto_20210818_1420"),
        ("pipeline", "0011_auto_20210818_1420"),
    ]

    operations = [
        migrations.AddField(
            model_name="prediction",
            name="batchjob_merge_predictions",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="prediction_merge",
                to="batch.batchjob",
            ),
        ),
        migrations.AlterField(
            model_name="prediction",
            name="batchjob_predict",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="prediction_run",
                to="batch.batchjob",
            ),
        ),
    ]
