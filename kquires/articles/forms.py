from django import forms
from .models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'attachment', 'category', 'short_description', 'brief_description', 'user', 'created_at']