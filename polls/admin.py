from django.contrib import admin
from .models import Question, Choice

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text", "author", "is_public", "is_approved"]}),
        ("Date information", {"fields": ["start_date", "end_date"], "classes": ["collapse"]}),
    ]
    inlines = [ChoiceInline]
    list_display = ["question_text", "author", "is_approved", "start_date", "is_active", "is_finished"]
    list_filter = ["is_approved", "is_public", "start_date"]
    search_fields = ["question_text"]
    actions = ['make_approved']

    @admin.action(description="Seçili anketleri onayla")
    def make_approved(self, request, queryset):
        queryset.update(is_approved=True)

admin.site.register(Question, QuestionAdmin)
