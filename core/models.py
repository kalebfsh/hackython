from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg
from datetime import timedelta

class Pet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pet')
    name = models.CharField(max_length=30, default='Tama')
    exp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    happiness = models.FloatField(default=50.0)  # 0-100
    appearance = models.CharField(max_length=20, default='baby')  # 'baby','teen','adult'
    last_updated = models.DateTimeField(auto_now=True)

    def recalc_from_recent_moods(self):
        """Recalculate happiness and level based on last 7 days of moods."""
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        avg = self.user.moods.filter(created_at__gte=week_ago).aggregate(avg=Avg('value'))['avg']
        if avg is None:
            # fallback to current happiness
            avg = self.happiness
        self.happiness = float(avg)
        # simple EXP rule: higher mood adds more exp; average mood/10 per mood entry will be added elsewhere
        # Level by exp thresholds:
        self.level = 1 + (self.exp // 100)
        # appearance rules (tweak as you like)
        if self.level >= 6:
            self.appearance = 'adult'
        elif self.level >= 3:
            self.appearance = 'teen'
        else:
            self.appearance = 'baby'
        self.save()

    def as_dict(self):
        return {
            'name': self.name,
            'exp': self.exp,
            'level': self.level,
            'happiness': self.happiness,
            'appearance': self.appearance,
            'last_updated': self.last_updated.isoformat(),
        }

class MoodEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moods')
    value = models.IntegerField()  # 0-100
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.value} ({self.created_at.date()})'
