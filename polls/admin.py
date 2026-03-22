from django.contrib import admin
from .models import Question, Choice

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text", "author", "is_public"]}),
        ("Date information", {"fields": ["start_date", "end_date"], "classes": ["collapse"]}),
    ]
    inlines = [ChoiceInline]
    list_display = ["question_text", "start_date", "end_date", "is_active", "is_finished"]
    list_filter = ["start_date", "is_public"]
    search_fields = ["question_text"]

admin.site.register(Question, QuestionAdmin)
