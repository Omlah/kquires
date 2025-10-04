from django.shortcuts import render, redirect
from django.views.generic import ListView
from ..articles.models import Article
from ..categories.models import Category
from ..message_alerts.models import MessageAlert
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model  # Import the User model or your custom user model
from ..departments.models import Department  # Import the Department model
from django.contrib.auth import logout

# Create your views here.
class DashboardIndexView(LoginRequiredMixin, ListView):
    model = Article
    context_object_name = 'articles'
    template_name = 'dashboard/index.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_superuser and request.user.status != 'True':
                logout(request)
                return redirect('/accounts/login/')
        else:
            return redirect('/accounts/login/')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        query = Article.objects.filter( status='approved')
        return query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter( status='approved', type='Main')
        context["most_recent_articles"] = Article.objects.filter( status='approved').order_by("-created_at")[:5]
        context["most_visited_articles"] = Article.objects.filter( status='approved').order_by("-click_count")[:5]
        if self.request.user.is_admin:
            context["inactive_users"] = User.objects.exclude(status='True')
        else:
            context["inactive_users"] = []

        try:
            context["alert"] = MessageAlert.objects.filter(visibility=1).latest('created_at')
        except ObjectDoesNotExist:
            context["alert"] = None
        return context



class DashboardHomeView(LoginRequiredMixin, ListView):
    model = Article
    context_object_name = 'articles'
    template_name = 'dashboard/home.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user

        # Redirect employees or managers to the dashboard home page
        if user.is_employee or user.is_manager:
            return redirect('dashboard:index')  # Redirect to home page (dashboard/index.html)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        user = self.request.user

        if user.is_manager:
            return redirect('dashboard:index')


        context = super().get_context_data(**kwargs)
        context['total_articles'] = Article.objects.count()
        context['pending_articles'] = Article.objects.filter(status="pending").count()
        context['approved_articles'] = Article.objects.filter(status="approved").count()
        context['rejected_articles'] = Article.objects.filter(status="rejected").count()
        context['departments'] = Department.objects.all()
        context['categories'] = Category.objects.all()
        context["parent_category"] = Category.objects.filter(status='approved', type='Main')


        return context

User = get_user_model()  # Get the User model or your custom user model

class DashboardStatisticsView(LoginRequiredMixin, ListView):
    model = Article
    context_object_name = 'articles'
    template_name = 'dashboard/statistics.html'


    def dispatch(self, request, *args, **kwargs):
        user = self.request.user

        # Redirectnto the dashboard home page
        if not user.is_admin and not user.is_manager:
            return redirect('dashboard:index')  # Redirect to home page (dashboard/index.html)

        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        user = self.request.user

        if user.is_manager:
            return redirect('dashboard:index')

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['total_articles'] = Article.objects.count()
        context['rejected_articles'] = Article.objects.filter(status="rejected").count()
        context['total_contributors'] = Article.objects.values('user').distinct().count()  # Add this line to include total contributors
        context["total_users"] = User.objects.count()
        context['new_articles'] = Article.objects.order_by('-created_at')[:5] # Get the 5 most recent articles
        return context


