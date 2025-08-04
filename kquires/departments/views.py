from django.views.generic import CreateView, DeleteView , UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Department
from .forms import DepartmentForm
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from ..users.models import User
from django.shortcuts import get_object_or_404

class UserDepartmentDelete(LoginRequiredMixin, DeleteView):
    model = Department
    success_url = reverse_lazy('categories:list')

    def get_object(self, queryset=None):
        return get_object_or_404(Department, id=self.kwargs.get('id'))
    
    def delete(self, request, *args, **kwargs):
        department_ids = request.POST.getlist('departments')
     
        user =  User.objects.get(id=self.request.user.id) 
        user.log('deleted', f"Department successfully deleted.")
        messages.success(request, "Department successfully deleted.")
        return super().delete(request, *args, **kwargs)
    
class DepartmentCreateOrUpdateView(LoginRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'categories/list.html'
    success_url = reverse_lazy('categories:list')
    

    def form_invalid(self, form):
        # Handling invalid form submission
        return super().form_invalid(form)

    def form_valid(self, form):
        # Save the form and return the response
        response = super().form_valid(form)
        # Add a success message
        action = 'added' if self.object.pk is None else 'updated'  # Assuming action depends on whether the object is new or updated
        messages.success(self.request, f"Deparment successfully {action}.")
        # Redirect to the current URL after successful form submission
        return super().form_valid(form)
class UserDepartmentCreateOrUpdateView(LoginRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'users/list.html'
    success_url = reverse_lazy('users:list')  # Keep this for consistent redirects

    def form_valid(self, form):
        department_id = self.request.POST.get('id')
        department_name = form.cleaned_data.get('name')

        if department_id:  # Update process
            try:
                department = Department.objects.get(pk=department_id)

                if department_name != department.name and Department.objects.filter(name=department_name).exists():
                    messages.error(self.request, "A department with this name already exists.")
                    return self.form_invalid(form)

                for field, value in form.cleaned_data.items():
                    setattr(department, field, value)
                department.save()
                messages.success(self.request, "Department successfully updated.")

            except Department.DoesNotExist:
                messages.error(self.request, "The department does not exist.")
                return self.form_invalid(form)

        else:  # Create process
            if Department.objects.filter(name=department_name).exists():
                messages.error(self.request, "A department with this name already exists.")
                return self.form_invalid(form)

            self.object = form.save()
            messages.success(self.request, "Department successfully added.")

        # ALWAYS redirect to success_url after a successful operation
        return redirect(self.success_url)  # This is the key change!
    
