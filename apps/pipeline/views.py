from pipeline.models import KerasModel, PixelsData, TrainingData
from pipeline.permissions import TesseloBaseObjectPermissions
from pipeline.serializers import (
    KerasModelSerializer,
    PixelsDataSerializer,
    TrainingDataSerializer,
)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_guardian import filters


class TesseloApiViewSet(viewsets.ModelViewSet):
    permission_classes = (
        IsAuthenticated,
        TesseloBaseObjectPermissions,
    )
    filter_backends = (filters.ObjectPermissionsFilter,)


class TrainingDataViewSet(TesseloApiViewSet):
    """
    My Awesome title.
    """

    queryset = TrainingData.objects.all().order_by("pk")
    serializer_class = TrainingDataSerializer


class PixelsDataViewSet(TesseloApiViewSet):
    queryset = PixelsData.objects.all().order_by("pk")
    serializer_class = PixelsDataSerializer


class KerasModelViewSet(TesseloApiViewSet):
    queryset = KerasModel.objects.all().order_by("pk")
    serializer_class = KerasModelSerializer
