from .models import Notification


def notification_context(request):
    """Inject unread notifications count and list into every template."""
    if request.user.is_authenticated:
        notifications = request.user.notifications.filter(is_read=False).order_by('-created_at')[:5]
        return {
            'notifications':       notifications,
            'unread_count':        request.user.notifications.filter(is_read=False).count(),
            'user_role':           request.user.role,
        }
    return {'notifications': [], 'unread_count': 0, 'user_role': None}
