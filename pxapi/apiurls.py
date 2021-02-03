from django.conf.urls import include, url
from rest_framework import routers

from pipeline.views import KerasModelViewSet, PixelsDataViewSet, TrainingDataViewSet

router = routers.DefaultRouter()

router.register(r"trainingdata", TrainingDataViewSet)
router.register(r"pixelsdata", PixelsDataViewSet)
router.register(r"kerasmodel", KerasModelViewSet)

apiurlpatterns = [
    url(r"^", include(router.urls)),
]
