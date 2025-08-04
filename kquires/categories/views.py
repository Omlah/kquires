from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DeleteView, View
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from .models import Category
from .forms import CategoryForm
from django.urls import reverse_lazy
from django.http import HttpResponse
import csv
from ..departments.models import Department
from ..users.models import User
from django.db.models import Q
from django.http import HttpRequest

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'categories/list.html'
    context_object_name = 'categories'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        
        # Redirect to the dashboard home page
        if user.is_employee or user.is_manager:
            return redirect('dashboard:index')  # Redirect to home page (dashboard/index.html)
        
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        categories = Category.objects.filter(type="Main").order_by('-updated_at')
        if query:
            categories = categories.filter(Q(name__icontains=query))

        return categories

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["parent_category"] = Category.objects.filter(type='Main')
        context["departments"] = Department.objects.all()
        return context

    def get_paginate_by(self, queryset: HttpRequest):
        page_size = self.request.GET.get('page_size', 10)
        try:
            return int(page_size)
        except ValueError:
            return 10

    def render_to_response(self, context, **response_kwargs):
        request = self.request
        if request.headers.get("HX-Request") == "true":
            return render(request, "categories/partials/table.html", context)
        return super().render_to_response(context, **response_kwargs)

class CategoryCreateOrUpdateView(LoginRequiredMixin, View):
    template_name = 'categories/list.html'
    success_url = reverse_lazy('categories:list')

    def get(self, request, *args, **kwargs):
        category_id = request.GET.get('id')
        category = None
        if category_id:
            category = get_object_or_404(Category, id=category_id)

        form = CategoryForm(instance=category)
        return render(request, self.template_name, {
            'form': form,
            'category': category
        })

    def post(self, request, *args, **kwargs):
        category_id = request.POST.get('id')
        category = None
        if category_id:
            category = get_object_or_404(Category, id=category_id)
            form = CategoryForm(request.POST, request.FILES, instance=category)
            if not request.FILES.get("logo"):
                form.instance.logo = category.logo
            action = "updated"
        else:
            form = CategoryForm(request.POST, request.FILES)
            action = "created"

        if form.is_valid():
            category = form.save(commit=False)
            if not category_id:
                category.user = request.user
            if not category.comment:
                category.comment = ''  # Provide a default value if comment is not provided
            category.save()
            form.save_m2m()  # Save Many-to-Many relationships

            user = User.objects.get(id=self.request.user.id)
            user.log(action, f"Category successfully {action}.")
            messages.success(request, f"Category successfully {action}.")
            return redirect(self.success_url)
        else:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        error_messages.append(error)
                    else:
                        error_messages.append(f"{form.fields[field].label}: {error}")

            error_message = "\n".join(error_messages)
            messages.error(self.request, error_message)
            return render(request, self.template_name, {
                'form': form,
                'category': category
            })

def category_detail_api(request, id):
    category = Category.objects.get(id=id)
    departments = list(category.departments.values('id', 'name')) if category.departments.exists() else []
    parent_category = category.parent_category.name if category.parent_category else None
    return JsonResponse({
        'id': category.id,
        'departments': departments,
        'type': category.type,
        'name': category.name,
        'parent_category': parent_category,
    })

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('categories:list')

    def get_object(self, queryset=None):
        return get_object_or_404(Category, id=self.kwargs.get('id'))

    def delete(self, request, *args, **kwargs):
        user = User.objects.get(id=self.request.user.id)
        user.log('deleted', f"Category successfully deleted.")
        messages.success(request, "Category successfully deleted.")
        return super().delete(request, *args, **kwargs)

class CategoryStatusView(LoginRequiredMixin, View):
    success_url = reverse_lazy('categories:list')

    def post(self, request, *args, **kwargs):
        category = get_object_or_404(Category, id=self.kwargs.get('id'))
        new_status = request.POST.get('status')

        if not new_status:
            messages.error(request, "Status is required.")
            return JsonResponse({'error': 'Status is required.'}, status=400)

        category.status = new_status
        category.save()

        user = User.objects.get(id=self.request.user.id)
        user.log('updated', f"Category status updated to '{new_status}'.")
        messages.success(request, f"Category status updated to '{new_status}'.")
        return redirect(self.success_url)

class CategoryVisibilityView(LoginRequiredMixin, View):
    success_url = reverse_lazy('categories:list')

    def post(self, request, *args, **kwargs):
        category = get_object_or_404(Category, id=self.kwargs.get('id'))
        new_visibility = request.POST.get('visibility')

        if new_visibility not in ['True', 'False']:
            messages.error(request, "Invalid visibility value.")
            return JsonResponse({'error': 'Invalid visibility value.'}, status=400)

        category.visibility = new_visibility == 'True'
        category.save()

        status_text = "visible" if category.visibility else "hidden"
        user = User.objects.get(id=self.request.user.id)
        user.log('updated', f"Category status updated to {status_text}.")
        messages.success(request, f"Category status updated to {status_text}.")
        return redirect(self.success_url)

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="activities.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'No.of Articles', 'Status', 'Created At'])

    categories = Category.objects.all()
    for category in categories:
        writer.writerow([category.id, category.name, category.articles.count(), category.status, category.created_at])

    return response
