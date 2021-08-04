from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from pipeline.models import KerasModel, PixelsData, Prediction, TrainingData


class NamedGuardedModelAdmin(GuardedModelAdmin):
    search_fields = ["name", "description"]


class TrainingDataAdmin(NamedGuardedModelAdmin):
    list_filter = ["batchjob_parse__status"]


class PixelsDataAdmin(NamedGuardedModelAdmin):
    list_filter = ["batchjob_collect_pixels__status", "batchjob_create_catalog__status"]


class KerasModelAdmin(NamedGuardedModelAdmin):
    list_filter = ["batchjob_train__status"]


class PredictionAdmin(NamedGuardedModelAdmin):
    list_filter = ["batchjob_predict__status", "batchjob_create_catalog__status"]


admin.site.register(TrainingData, TrainingDataAdmin)
admin.site.register(PixelsData, PixelsDataAdmin)
admin.site.register(KerasModel, KerasModelAdmin)
admin.site.register(Prediction, PredictionAdmin)
