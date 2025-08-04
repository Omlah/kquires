from django import forms
from .models import Category
from ..departments.models import Department

class CategoryForm(forms.ModelForm):
    departments = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all(),
        widget=forms.SelectMultiple,
        required=False,  # Adjust as needed
        label="Departments"
    )

    class Meta:
        model = Category
        fields = ['name', 'type', 'departments', 'subcategory', 'parent_category', 'logo', 'comment']  # Include the comment field
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'departments': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        category_type = cleaned_data.get('type')
        parent_category = cleaned_data.get('parent_category')

        if category_type == 'Main' and parent_category is not None:
            raise forms.ValidationError("Main categories cannot have a parent category.")
        elif category_type == 'Sub' and parent_category is None:
            raise forms.ValidationError("Subcategories must have a parent category.")

        return cleaned_data



