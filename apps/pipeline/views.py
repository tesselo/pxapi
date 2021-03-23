import json

from batch.const import BATCH_JOB_FINAL_STATUSES
from django.conf import settings
from drf_spectacular.utils import extend_schema, inline_serializer
from pipeline.exceptions import UpdateBeforeFinishedExeption
from pipeline.models import KerasModel, PixelsData, Prediction, TrainingData
from pipeline.permissions import TesseloBaseObjectPermissions
from pipeline.serializers import (
    KerasModelSerializer,
    PixelsDataSerializer,
    PredictionSerializer,
    TrainingDataSerializer,
)
from pixels.stac import stac_s3_read_method
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_guardian import filters


class TesseloApiViewSet(viewsets.ModelViewSet):
    permission_classes = (
        IsAuthenticated,
        TesseloBaseObjectPermissions,
    )
    filter_backends = (filters.ObjectPermissionsFilter, SearchFilter)
    search_fields = ("name",)

    _job_field_names = []

    def _jobs_are_finished(self, obj):
        """
        Check if all jobs are in finished state.
        """
        finished = []
        for field in self._job_field_names:
            # Get job object.
            job = getattr(obj, field)
            # Update job status if necessary.
            if job.status not in BATCH_JOB_FINAL_STATUSES:
                job.update()
            # Check if job is in final status.
            finished.append(job.status in BATCH_JOB_FINAL_STATUSES)
        # Check if all jobs have finished.
        return all(finished)

    def update(self, request, pk, *args, **kwargs):
        """
        Only allow updates if the existing jobs have failed or succeeded.
        """
        obj = self.get_object()
        # Ensure all jobs have finished before triggering update.
        if not self._jobs_are_finished(obj):
            raise UpdateBeforeFinishedExeption()

        return super().update(request, pk, *args, **kwargs)

    @extend_schema(
        responses=inline_serializer(
            name="Logs",
            fields={
                "job_field": serializers.CharField(),
                "message": serializers.CharField(),
                "events": serializers.JSONField(),
            },
        ),
    )
    @action(detail=True, methods=["get"])
    def logs(self, request, pk):
        """
        Obtain batch job logs.
        """
        obj = self.get_object()
        messages = []
        for field in self._job_field_names:
            # Get job object through job field.
            job = getattr(obj, field)
            # Prepare base message.
            msg = {"job_field": field}
            # Make sanity checks.
            if not job:
                msg.update({"message": "No job object found.", "events": {}})
            elif not job.job_id:
                msg.update({"message": "No job ID found.", "events": {}})
            else:
                # Get job log.
                msg.update(
                    {
                        "message": "Job log retrieved successfully.",
                        "events": job.get_log(),
                    }
                )
            messages.append(msg)
        # Send job logs.
        return Response(messages)


class TrainingDataViewSet(TesseloApiViewSet):
    """
    Manage training data layers.
    """

    _job_field_names = ["batchjob_parse"]

    queryset = TrainingData.objects.all().order_by("name")
    serializer_class = TrainingDataSerializer

    @extend_schema(
        responses=inline_serializer(
            name="Catalog",
            fields={
                "message": serializers.CharField(),
                "stac_catalog": serializers.JSONField(),
            },
        ),
    )
    @action(detail=True, methods=["get"])
    def catalog(self, request, pk, format=None):
        """
        Access STAC catalog.
        """
        # Get object.
        obj = self.get_object()
        # Set data to default None.
        data = None
        # If bucket name was specified, use it to get data.
        if hasattr(settings, "AWS_S3_BUCKET_NAME"):
            data = json.loads(stac_s3_read_method(obj.catalog_uri))
        # Choose message.
        msg = "No catalog found." if data is None else "Found STAC catalog."
        # Return data.
        return Response({"message": msg, "stac_catalog": data})


class PixelsDataViewSet(TesseloApiViewSet):
    """
    Manage satellite image pixels collections.
    """

    _job_field_names = ["batchjob_collect_pixels", "batchjob_create_catalog"]

    queryset = PixelsData.objects.all().order_by("name")
    serializer_class = PixelsDataSerializer


class KerasModelViewSet(TesseloApiViewSet):

    _job_field_names = ["batchjob_train"]

    queryset = KerasModel.objects.all().order_by("name")
    serializer_class = KerasModelSerializer

    @extend_schema(
        responses=inline_serializer(
            name="Catalog",
            fields={
                "message": serializers.CharField(),
                "history": serializers.JSONField(),
            },
        ),
    )
    @action(detail=True, methods=["get"])
    def history(self, request, pk, format=None):
        """
        Access STAC catalog.
        """
        # Set data to default None.
        data = None
        # If bucket name was specified, use it to get data.
        if hasattr(settings, "AWS_S3_BUCKET_NAME"):
            uri = f"s3://{settings.AWS_S3_BUCKET_NAME}/kerasmodel/{pk}/history.json"
            data = json.loads(stac_s3_read_method(uri))
        # Choose message.
        msg = "No history found." if data is None else "Found history."
        # Return data.
        return Response({"message": msg, "history": data})


class PredictionViewSet(TesseloApiViewSet):
    """
    Manage model predictions.
    """

    _job_field_names = ["batchjob_predict", "batchjob_create_catalog"]

    queryset = Prediction.objects.all().order_by("name")
    serializer_class = PredictionSerializer
