from django.shortcuts import render,redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Log
import openpyxl
from django.http import HttpResponse, HttpRequest
from .models import Log


class LogsListView(LoginRequiredMixin, ListView):
    model = Log
    context_object_name = 'logs'
    template_name = 'logs/list.html'
    paginate_by = 10
    ordering = ['-timestamp']

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        
        # Redirect to the dashboard home page
        if not user.is_admin:
            return redirect('dashboard:index')  # Redirect to home page (dashboard/index.html)
        
        return super().dispatch(request, *args, **kwargs)

    def get_paginate_by(self, queryset: HttpRequest):
        page_size = self.request.GET.get('page_size', 10)
        try:
            return int(page_size)
        except ValueError:
            return 10




def export_activity_log_excel(request):
    # Create an in-memory workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Activity Logs"

    # Define column headers
    ws.append(["Date/Time", "Username", "Action", "Action Description"])

    # Fetch logs from the database
    logs = Log.objects.all().order_by('-timestamp')


    # Loop through logs and append to the worksheet
    for log in logs:
        ws.append([
            log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            log.user.name if log.user else "Unknown User",
            log.action,
            log.details,
        ])

    # Set the HTTP response headers
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=activity_logs.xlsx'

    # Save the workbook to the response
    wb.save(response)

    return response
