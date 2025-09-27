from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MoodEntry, Pet
from django.utils import timezone

@receiver(post_save, sender=MoodEntry)
def mood_saved(sender, instance, created, **kwargs):
    if not created:
        return
    pet, _ = Pet.objects.get_or_create(user=instance.user)
    # grant EXP proportional to mood value (so positive check-ins feel rewarding)
    pet.exp += max(1, instance.value // 10)  # e.g., mood 80 -> +8 exp
    pet.recalc_from_recent_moods()
