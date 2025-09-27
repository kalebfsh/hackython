from django import forms
from .models import MoodEntry
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class MoodForm(forms.ModelForm):
    class Meta:
        model = MoodEntry
        fields = ['value', 'note']
        widgets = {
            'value': forms.NumberInput(attrs={'type': 'range', 'min':0,'max':100}),
            'note': forms.Textarea(attrs={'rows':2, 'placeholder': 'optional note...'}),
        }

class PetRenameForm(forms.Form):
    name = forms.CharField(max_length=30)

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if not name:
            raise forms.ValidationError('Name cannot be empty.')
        return name

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username','password1','password2')
