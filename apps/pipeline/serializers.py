from batch.serializers import BatchJobSerializer
from pipeline.models import KerasModel, PixelsData, TrainingData
from rest_framework import serializers
from rest_framework_guardian.serializers import ObjectPermissionsAssignmentMixin


class TesseloBaseSerializer(
    ObjectPermissionsAssignmentMixin, serializers.ModelSerializer
):
    def get_permissions_map(self, created):
        # Get user.
        current_user = self.context["request"].user
        # Get model name for permissions map.
        model_key = self.Meta.model.__name__.lower()
        # Construct map.
        return {
            "view_{}".format(model_key): [current_user],
            "add_{}".format(model_key): [current_user],
            "change_{}".format(model_key): [current_user],
            "delete_{}".format(model_key): [current_user],
        }


class TrainingDataSerializer(TesseloBaseSerializer):

    batchjob_parse = BatchJobSerializer(read_only=True)

    class Meta:
        model = TrainingData
        fields = "__all__"
        read_only_fields = ["batchjob_parse"]
        depth = 1


class PixelsDataSerializer(TesseloBaseSerializer):

    batchjob_collect_pixels = BatchJobSerializer(read_only=True)
    batchjob_create_catalog = BatchJobSerializer(read_only=True)

    class Meta:
        model = PixelsData
        fields = "__all__"
        read_only_fields = [
            "batchjob_collect_pixels",
            "batchjob_create_catalog",
            "config_file",
        ]


class KerasModelSerializer(TesseloBaseSerializer):

    batchjob_train = BatchJobSerializer(read_only=True)

    class Meta:
        model = KerasModel
        fields = "__all__"
