from django import forms
from .models import Notification

class NotifcationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['message', 'created_at']