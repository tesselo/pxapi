import uuid

from django.db import models


class NamedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=250, default="")
    description = models.TextField(default="")

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


def trainingdata_upload_to(instance, filename):
    return f"trainingdata/{instance.pk}/{filename}"


class TrainingData(NamedModel):
    zipfile = models.FileField(upload_to=trainingdata_upload_to)


class PixelsData(NamedModel):
    config = models.JSONField(default=dict)
    trainingdata = models.ForeignKey(TrainingData, on_delete=models.PROTECT)


def kerasmodel_upload_to(instance, filename):
    return f"kerasmodel/{instance.pk}/{filename}"


class KerasModel(NamedModel):
    definition = models.JSONField(default=dict, blank=True)
    model = models.FileField(upload_to=kerasmodel_upload_to, null=True, editable=False)
