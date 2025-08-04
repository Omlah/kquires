from django import forms
from .models import MessageAlert

class MessageAlertForm(forms.ModelForm):
    class Meta:
        model = MessageAlert
        fields = ['message', 'created_at']