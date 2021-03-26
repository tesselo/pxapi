from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from pipeline.models import KerasModel, PixelsData, Prediction, TrainingData

admin.site.register(TrainingData, GuardedModelAdmin)
admin.site.register(PixelsData, GuardedModelAdmin)
admin.site.register(KerasModel, GuardedModelAdmin)
admin.site.register(Prediction, GuardedModelAdmin)
