from .models import Messages
from django.db.models import Q

def get_msgs_count(request):
    if request.user.is_authenticated:
        msgs = Messages.objects.filter(Q(for_all=True) | Q(user=request.user))
        unread_count = msgs.filter(viewed=False).count()
    else:
        unread_count = 0
    context = {
        'unread_count': unread_count
    }
    return context