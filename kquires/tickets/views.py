from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, View
from .models import Ticket
from .forms import TicketForm
from django.urls import reverse_lazy
# from ..categories.models import Category
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ..users.models import User
from django.http import HttpRequest
from django.http import HttpResponseRedirect

# Create your views here.
class TicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'tickets/list.html'
    context_object_name = 'tickets'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user

        # Redirect to the dashboard home page
        if not user.is_admin:
            return redirect('dashboard:index')  # Redirect to home page (dashboard/index.html)

        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Ticket.objects.all().order_by('-updated_at')

    def get_paginate_by(self, queryset: HttpRequest):
        page_size = self.request.GET.get('page_size', 10)
        try:
            return int(page_size)
        except ValueError:
            return 10


class MyTicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'tickets/my_list.html'
    context_object_name = 'tickets'
    paginate_by = 10

    def get_queryset(self):
        return Ticket.objects.all().order_by('-updated_at')

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["categories"] =  Category.objects.all()
    #     return context
    



class TicketCreateOrUpdateView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/my_list.html'  # Adjusted to a more appropriate template name
    success_url = reverse_lazy('tickets:my_list')

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["categories"] = Category.objects.all()
    #     ticket_id = self.request.GET.get('id')
    #     if ticket_id:
    #         context["ticket"] = get_object_or_404(Ticket, id=ticket_id)
    #     return context


    def post(self, request, *args, **kwargs):
        ticket_id = request.POST.get('id')  # Check if an ID is provided
        if ticket_id:  # If ID exists, update the existing ticket
            ticket = get_object_or_404(Ticket, id=ticket_id)
            form = self.form_class(request.POST, instance=ticket)
            action = "updated"
        else:  # Otherwise, create a new ticket
            form = self.form_class(request.POST)
            action = "created"

        if form.is_valid():
            ticket = form.save(commit=False)
            if not ticket_id:  # Only set user for new tickets
                ticket.user = request.user
            ticket.save()
            user =  User.objects.get(id=self.request.user.id)
            user.log(action, f"Ticket successfully {action}.")
            messages.success(request, f"Ticket successfully {action}.")
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


def ticket_detail_api(request, id):
    ticket = Ticket.objects.get(id=id)
    return JsonResponse({
        'id': ticket.id,
        'title': ticket.title,
        # 'category': ticket.category.name,  # Assuming category has a name attribute
        'description': ticket.description,
    })


class TicketStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        ticket = get_object_or_404(Ticket, id=self.kwargs.get('id'))
        status = request.POST.get('status')
        if status:
            ticket.status = status
            ticket.save()

            # Log the status change (assuming User has a log method)
            user = request.user
            user.log("updated", f"Ticket status successfully updated.")

            messages.success(request, f"Ticket status successfully updated.")
        else:
            messages.error(request, "No status provided.")

        return HttpResponseRedirect(reverse_lazy('tickets:list'))

    def get(self, request, *args, **kwargs):
        # This is optional, if you want to show the current status or other details
        ticket = get_object_or_404(Ticket, id=self.kwargs.get('id'))
        return self.render_to_response({'ticket': ticket})
