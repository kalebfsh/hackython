from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg
from datetime import timedelta
from django.core.validators import MinValueValidator, MaxValueValidator

class Pet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pet')
    name = models.CharField(max_length=30, default='Tama')
    exp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    happiness = models.FloatField(default=50.0)  # 0-100
    appearance = models.CharField(max_length=20, default='baby_happy')  # 'baby','teen','adult'
    last_updated = models.DateTimeField(auto_now=True)
    hunger = models.FloatField(default=100.0)  # 0-100 (0 = starving, 100 = full)
    last_hunger_update = models.DateTimeField(default=timezone.now)

    def update_hunger(self):
        """
        Decrease hunger based on time elapsed since last update.
        Example: lose 1 point per hour.
        """
        now = timezone.now()
        elapsed = (now - self.last_hunger_update).total_seconds() / 1200.0  # hours
        if elapsed > 0:
            loss = elapsed * 1.0  # 1 hunger per hour
            self.hunger = max(0.0, self.hunger - loss)
            self.last_hunger_update = now
            self.save(update_fields=['hunger', 'last_hunger_update'])

    def feed(self, amount=20):
        """Feed the pet to restore hunger."""
        self.update_hunger()
        self.hunger = min(100, self.hunger + amount)
        # Optionally boost happiness slightly:
        self.happiness = min(100.0, self.happiness + amount * 0.2)
        self.save(update_fields=['hunger', 'happiness'])



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

        """Return the correct image filename based on age_stage and happiness"""
        stage = self.appearance  # baby / teen / adult
        if self.happiness >= 50:
            mood = "happy"
        else:
            mood = "sad"
        self.appearance = f"{stage}_{mood}"
        self.save()


          # e.g., 'baby_happy.png'

    def as_dict(self):
        self.update_hunger()  # keep hunger fresh
        return {
            'name': self.name,
            'exp': self.exp,
            'level': self.level,
            'happiness': self.happiness,
            'appearance': self.appearance,
            'hunger': self.hunger,
            'last_updated': self.last_updated.isoformat(),
        }



class MoodEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moods')
    value = models.IntegerField()  # 0-100
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.value} ({self.created_at.date()})'
