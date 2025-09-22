from django import forms
from .models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'attachment', 'category', 'subcategory', 'short_description', 'brief_description', 'user', 'created_at']
        widgets = {
            'category': forms.Select(attrs={'required': True}),
            'subcategory': forms.Select(attrs={'required': False}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make category field required
        self.fields['category'].required = True
        self.fields['category'].empty_label = "Select a category"
    
    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError("Please select a category.")
        return category
