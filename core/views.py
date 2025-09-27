from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import MoodForm, SignUpForm
from .models import Pet, MoodEntry
from django.http import JsonResponse
from django.contrib.auth import login
from django.views.decorators.http import require_POST
import json


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # create pet
            Pet.objects.create(user=user)
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def dashboard(request):
    pet, _ = Pet.objects.get_or_create(user=request.user)
    form = MoodForm()
    # load last 14 mood entries
    recent = request.user.moods.order_by('-created_at')[:14]

    moods = MoodEntry.objects.filter(user=request.user).order_by("created_at")
    mood_dates = [m.created_at.strftime("%Y-%m-%d") for m in moods]
    mood_values = [m.value for m in moods]

    context = {
        'pet': pet, 'form': form, 'recent': recent,
        "mood_dates": json.dumps(mood_dates),
        "mood_values": json.dumps(mood_values),
    }
    return render(request, "dashboard.html", context)


@login_required
@require_POST
def submit_mood(request):
    form = MoodForm(request.POST)
    if form.is_valid():
        mood = form.save(commit=False)
        mood.user = request.user
        mood.save()
        pet = request.user.pet

        #get last 14 moods
        moods = MoodEntry.objects.filter(user=request.user).order_by('-created_at')[:14]
        mood_dates = [m.created_at.strftime("%Y-%m-%d") for m in reversed(moods)]
        mood_values = [m.value for m in reversed(moods)]
        data = {
            'success': True,
            'pet': pet.as_dict(),
            'mood_dates': mood_dates,
            'mood_values': mood_values,
        }
        return JsonResponse(data)
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
def pet_json(request):
    pet = request.user.pet
    return JsonResponse(pet.as_dict())
