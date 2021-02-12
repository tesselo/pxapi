from botocore.exceptions import NoCredentialsError
from pipeline.models import KerasModel, PixelsData, TrainingData
from pipeline.permissions import TesseloBaseObjectPermissions
from pipeline.serializers import (
    KerasModelSerializer,
    PixelsDataSerializer,
    TrainingDataSerializer,
)
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_guardian import filters


class TesseloApiViewSet(viewsets.ModelViewSet):
    permission_classes = (
        IsAuthenticated,
        TesseloBaseObjectPermissions,
    )
    filter_backends = (filters.ObjectPermissionsFilter,)

    _job_field_names = []

    @action(detail=True, methods=["post"])
    def refresh(self, request, pk):
        """
        Update batch job status.
        """
        # Get parent object.
        obj = self.get_object()
        messages = []
        for field in self._job_field_names:
            # Get job object.
            job = getattr(obj, field)
            # Make sanity checks.
            if not job:
                msg = {"job_field": field, "error": "No job object found."}
            elif not job.job_id:
                msg = {"job_field": field, "error": "No job id found."}
            else:
                try:
                    # Update job status.
                    job.update()
                    msg = {
                        "job_id": job.job_id,
                        "success": 'Updated batch job. New status is "{}".'.format(
                            job.status
                        ),
                    }
                except NoCredentialsError:
                    msg = {
                        "job_id": job.job_id,
                        "error": "Could not retrieve job details - no credentials found.",
                    }
            messages.append(msg)
        # Send job update messages.
        return Response(messages)

    @action(detail=True, methods=["get"])
    def logs(self, request, pk):
        """
        Obtain job log.
        """
        obj = self.get_object()
        messages = []
        for field in self._job_field_names:
            # Get job object.
            job = getattr(obj, field)
            # Make sanity checks.
            if not job:
                msg = {"job_field": field, "error": "No job object found."}
            elif not job.job_id:
                msg = {"job_field": field, "error": "No job id found."}
            else:
                # Get job log.
                msg = job.get_log()
            messages.append(msg)
        # Send job logs.
        return Response(messages)


class TrainingDataViewSet(TesseloApiViewSet):
    """
    Manage training data layers.
    """

    _job_field_names = ["batchjob_parse"]

    queryset = TrainingData.objects.all().order_by("pk")
    serializer_class = TrainingDataSerializer


class PixelsDataViewSet(TesseloApiViewSet):
    """
    Manage satellite image pixels collections.
    """

    _job_field_names = ["batchjob_collect_pixels", "batchjob_create_catalog"]

    queryset = PixelsData.objects.all().order_by("pk")
    serializer_class = PixelsDataSerializer


class KerasModelViewSet(TesseloApiViewSet):

    _job_field_names = ["batchjob_train"]

    queryset = KerasModel.objects.all().order_by("pk")
    serializer_class = KerasModelSerializer
