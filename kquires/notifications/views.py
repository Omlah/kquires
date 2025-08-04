from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.shortcuts import render

 
@login_required
def get_notifications(request):

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()  # Count unread ones

    data = []
    for n in notifications:
        data.append({
            'message': n.message,
            'id': n.id,
            'is_read': n.is_read,
            'user_name': n.user.name,
            'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    return JsonResponse({'notifications': data, 'unread_count': unread_count})


@csrf_exempt
@login_required
def mark_notifications_as_read(request):
    if not request.user.is_admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if request.method == "POST":
        Notification.objects.filter(is_read=False).update(is_read=True)
        unread_count = Notification.objects.filter(is_read=False).count()
        return JsonResponse({'status': 'success', 'unread_count': unread_count})

    return JsonResponse({'status': 'failed'}, status=400)


@csrf_exempt
@login_required
def clear_all_notifications(request):
    if request.method == "POST":
        Notification.objects.filter(user=request.user).delete()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failed'}, status=400)

@csrf_exempt
@login_required
def view_all_notifications(request):
    if request.method == "GET":
        notifications = Notification.objects.filter(user=request.user)
        return render(request, 'notifications/view.html', {'notifications': notifications})

    return JsonResponse({'status': 'failed'}, status=400)
