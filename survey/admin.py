from django.contrib import admin
from .models import Answer, Question, LikeOrDislike


class QuestionAdmin(admin.ModelAdmin):
    pass


class AnswerAdmin(admin.ModelAdmin):
    pass


class LikeOrDislikeAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'like_or_dislike',
        'question',
    )


admin.site.register(Question, QuestionAdmin)
admin.site.register(LikeOrDislike, LikeOrDislikeAdmin)
admin.site.register(Answer, AnswerAdmin)