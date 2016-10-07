from django.contrib import admin

# Register your models here.
from vicki.models import UserDetail, QuestionAnswer, Prediction


class UserDetailAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'target_image', 'start_time', 'end_time')


class PredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'predicted_image', 'time')

class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'bot_answer', 'question_time', 'bot_answer_time')


admin.site.register(UserDetail, UserDetailAdmin)
admin.site.register(Prediction, PredictionAdmin)
admin.site.register(QuestionAnswer, QuestionAnswerAdmin)
