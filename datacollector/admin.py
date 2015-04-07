from datacollector.models import *
from django.contrib import admin

#class ChoiceInline(admin.StackedInline):
#    model = TaskChoice
#    extra = 3

#class TaskFieldAdmin(admin.ModelAdmin):
#    inlines = [ChoiceInline]

# Helper classes
admin.site.register(Education_Level)
admin.site.register(Gender)
admin.site.register(Country)
admin.site.register(Country_Province)
admin.site.register(Dementia_Type)
admin.site.register(Ethnicity)
admin.site.register(Language)
admin.site.register(Language_Level)
admin.site.register(Field_Type)
admin.site.register(Field_Data_Type)
admin.site.register(Value_Difficulty)

# Task classes
admin.site.register(Task)
admin.site.register(Task_Field)
admin.site.register(Task_Field_Value)
admin.site.register(Task_Field_Data_Attribute)

# Subject classes
admin.site.register(Subject)
