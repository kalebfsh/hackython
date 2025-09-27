from django.contrib import admin
from .models import Pet, MoodEntry

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'level', 'happiness', 'exp')

@admin.register(MoodEntry)
class MoodAdmin(admin.ModelAdmin):
    list_display = ('user', 'value', 'created_at')
    list_filter = ('created_at',)
