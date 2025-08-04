from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DeleteView, View
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from .models import MessageAlert
from .forms import MessageAlertForm
from django.urls import reverse_lazy
from ..users.models import User

# Create your views here.
class MessageAlertListView(LoginRequiredMixin, ListView):
    model = MessageAlert
    template_name = 'message_alerts/list.html'
    context_object_name = 'message_alerts'
    paginate_by = 10


    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        
        # Redirect  to the dashboard home page
        if not user.is_admin:
            return redirect('dashboard:index')  # Redirect to home page (dashboard/index.html)
        
        return super().dispatch(request, *args, **kwargs)
    def get_queryset(self):
        return MessageAlert.objects.all().order_by('-updated_at')



class MessageAlertCreateOrUpdateView(LoginRequiredMixin, CreateView):
    model = MessageAlert
    form_class = MessageAlertForm
    template_name = 'message_alerts/list.html'  # Adjusted to a more appropriate template name
    success_url = reverse_lazy('message_alerts:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        message_alert_id = self.request.GET.get('id')
        if message_alert_id:
            context["message_alert"] = get_object_or_404(MessageAlert, id=message_alert_id)
        return context
    
    


    def post(self, request, *args, **kwargs):
        message_alert_id = request.POST.get('id')  # Check if an ID is provided
        if message_alert_id:  # If ID exists, update the existing MessageAlert
            message_alert = get_object_or_404(MessageAlert, id=message_alert_id)
            form = self.form_class(request.POST, instance=message_alert)
            action = "updated"
        else:  # Otherwise, create a new MessageAlert
            form = self.form_class(request.POST)
            action = "created"

        if form.is_valid():
            message_alert = form.save(commit=False)
            if not message_alert_id:
                message_alert.user = request.user
            message_alert.save()
            user =  User.objects.get(id=self.request.user.id)
            user.log(action, f"Message successfully {action}.")
            messages.success(request, f"Message successfully {action}.")
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        # Collect and display detailed error messages
        error_messages = []

        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    error_messages.append(error)
                else:
                    error_messages.append(f"{form.fields[field].label}: {error}")

        error_message = "\n".join(error_messages)
        messages.error(self.request, error_message)
        return self.render_to_response(self.get_context_data(form=form))

def message_alert_detail_api(request, id):
    message_alert = MessageAlert.objects.get(id=id)
    return JsonResponse({
        'id': message_alert.id,
        'message': message_alert.message,
    })

class MessageAlertDeleteView(LoginRequiredMixin, DeleteView):
    model = MessageAlert
    success_url = reverse_lazy('categories:list')

    def get_object(self, queryset=None):
        return get_object_or_404(MessageAlert, id=self.kwargs.get('id'))

    def delete(self, request, *args, **kwargs):
        # Add success message
        user =  User.objects.get(id=self.request.user.id)
        user.log('deleted', f"MessageAlert successfully deleted.")
        messages.success(request, "Message successfully deleted.")
        return super().delete(request, *args, **kwargs)

class MessageAlertVisibilityView(LoginRequiredMixin, View):
    success_url = reverse_lazy('message_alerts:list')
    def post(self, request, *args, **kwargs):
        message_alert = get_object_or_404(MessageAlert, id=self.kwargs.get('id'))
        new_visibility = request.POST.get('visibility')

        if new_visibility not in ['True', 'False']:
            messages.error(request, "Invalid visibility value.")
            return JsonResponse({'error': 'Invalid visibility value.'}, status=400)
        if new_visibility == 'True':
            MessageAlert.objects.exclude(id=message_alert.id).update(visibility=False)
        message_alert.visibility = new_visibility == 'True'
        message_alert.save()

        # Add a success message
        status_text = "visible" if message_alert.visibility else "hidden"
        user =  User.objects.get(id=self.request.user.id)
        user.log('updated', f"MessageAlert status updated to {status_text}.")
        messages.success(request, f"MessageAlert is now {status_text}.")
        return redirect(self.success_url)
