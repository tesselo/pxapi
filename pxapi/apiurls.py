from django.urls import include, path
from pipeline.views import (
    KerasModelViewSet,
    PixelsDataViewSet,
    PredictionViewSet,
    TrainingDataViewSet,
)
from rest_framework import routers
from wmts.views import tilesview, wmtsview

router = routers.DefaultRouter(trailing_slash=False)

router.register("trainingdata", TrainingDataViewSet)
router.register("pixelsdata", PixelsDataViewSet)
router.register("kerasmodel", KerasModelViewSet)
router.register("prediction", PredictionViewSet)

apiurlpatterns = [
    path("", include(router.urls)),
    path("wmts", wmtsview),
    path(
        "tiles/<int:z>/<int:x>/<int:y>.png",
        tilesview,
    ),
    path(
        "tiles/<str:platform>/<int:z>/<int:x>/<int:y>.png",
        tilesview,
    ),
]
