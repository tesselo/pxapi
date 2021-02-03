import uuid

from batch.models import BatchJob
from django.db import models


class NamedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=250, default="")
    description = models.TextField(default="")

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


def training_data_zip_upload_to(instance, filename):
    return f"pixelsdata/{instance.pk}/data.zip"


class TrainingData(NamedModel):
    zipfile = models.FileField(upload_to=training_data_zip_upload_to)
    batchjob = models.ForeignKey(
        BatchJob, blank=True, null=True, editable=False, on_delete=models.PROTECT
    )


def pixels_data_json_upload_to(instance, filename):
    return f"pixelsdata/{instance.pk}/config.json"


class PixelsData(NamedModel):
    config = models.JSONField(default=dict)
    trainingdata = models.ForeignKey(TrainingData, on_delete=models.PROTECT)
    config_file = models.FileField(
        upload_to=pixels_data_json_upload_to, null=True, editable=False
    )


def keras_model_json_upload_to(instance, filename):
    return f"kerasmodel/{instance.pk}/model.json"


def keras_model_h5_upload_to(instance, filename):
    return f"kerasmodel/{instance.pk}/model.h5"


class KerasModel(NamedModel):
    definition = models.JSONField(default=dict, blank=True)
    model_h5 = models.FileField(
        upload_to=keras_model_h5_upload_to, null=True, editable=False
    )
    model_json = models.FileField(
        upload_to=keras_model_json_upload_to, null=True, editable=False
    )
    batchjob = models.ForeignKey(
        BatchJob, blank=True, null=True, editable=False, on_delete=models.PROTECT
    )
