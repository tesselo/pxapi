from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from pipeline.models import KerasModel, PixelsData, Prediction, TrainingData


class NamedGuardedModelAdmin(GuardedModelAdmin):
    search_fields = ["name", "description"]
    list_display = ["name", "status"]
    change_form_template = "change_form.html"

    status_key = None

    def status(self, obj):
        """
        Obtain the status from a related batchjob object.

        The status_key property is the name of the ForeignKey field linking to
        the batch job object.
        """
        # Ensure key was set.
        if not self.status_key:
            raise NotImplementedError("Status key needs to be specified.")
        # Get related batch job using the key string.
        batchjob = getattr(obj, self.status_key, None)
        # If the batchjob object exists, use its status for display. Otherwise
        # return unknown.
        if batchjob:
            return batchjob.status.title()
        else:
            return "Unknown"


class TrainingDataAdmin(NamedGuardedModelAdmin):
    list_filter = ["batchjob_parse__status"]
    status_key = "batchjob_parse"


class PixelsDataAdmin(NamedGuardedModelAdmin):
    list_filter = ["batchjob_collect_pixels__status", "batchjob_create_catalog__status"]
    status_key = "batchjob_create_catalog"


class KerasModelAdmin(NamedGuardedModelAdmin):
    list_filter = ["batchjob_train__status"]
    change_form_template = "change_form_kerasmodel.html"
    status_key = "batchjob_train"


class PredictionAdmin(NamedGuardedModelAdmin):
    list_filter = ["batchjob_predict__status", "batchjob_create_catalog__status"]
    status_key = "batchjob_create_catalog"


admin.site.register(TrainingData, TrainingDataAdmin)
admin.site.register(PixelsData, PixelsDataAdmin)
admin.site.register(KerasModel, KerasModelAdmin)
admin.site.register(Prediction, PredictionAdmin)
