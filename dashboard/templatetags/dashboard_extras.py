from django import template
import os

register = template.Library()

@register.filter
def endswith(value, arg):
    """
    Checks if a string ends with the specified suffix.
    Usage: {{ value|endswith:".pdf" }}
    """
    return value.endswith(arg)

@register.filter
def get_item(dictionary, key):
    """
    Gets an item from a dictionary using the key.
    Usage: {{ dictionary|get_item:key }}
    """
    return dictionary.get(key)

@register.filter
def file_extension(value):
    """
    Returns the file extension of a file path.
    Usage: {{ value|file_extension }}
    """
    return os.path.splitext(value)[1].lower()[1:]

@register.filter
def is_image(value):
    """
    Checks if a file extension is an image format.
    Usage: {{ value|is_image }}
    """
    ext = file_extension(value)
    return ext in ['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp']

@register.filter
def is_pdf(value):
    """
    Checks if a file extension is PDF.
    Usage: {{ value|is_pdf }}
    """
    ext = file_extension(value)
    return ext == 'pdf'

@register.filter
def is_document(value):
    """
    Checks if a file extension is a document format.
    Usage: {{ value|is_document }}
    """
    ext = file_extension(value)
    return ext in ['doc', 'docx', 'txt', 'pdf', 'xls', 'xlsx', 'ppt', 'pptx']

@register.filter
def get_icon_class(value):
    """
    Returns the appropriate Font Awesome icon class for a file type.
    Usage: {{ value|get_icon_class }}
    """
    ext = file_extension(value)
    
    if is_image(value):
        return 'fa-file-image'
    elif is_pdf(value):
        return 'fa-file-pdf'
    elif ext in ['doc', 'docx']:
        return 'fa-file-word'
    elif ext in ['xls', 'xlsx']:
        return 'fa-file-excel'
    elif ext in ['ppt', 'pptx']:
        return 'fa-file-powerpoint'
    elif ext in ['zip', 'rar', '7z']:
        return 'fa-file-archive'
    elif ext in ['mp3', 'wav', 'ogg']:
        return 'fa-file-audio'
    elif ext in ['mp4', 'avi', 'mov', 'wmv']:
        return 'fa-file-video'
    elif ext == 'txt':
        return 'fa-file-alt'
    else:
        return 'fa-file'

@register.simple_tag
def get_unread_notifications_count(user):
    """
    Returns the count of unread notifications for a user.
    Usage: {% get_unread_notifications_count user as count %}
    """
    if user.is_authenticated:
        return user.notifications.filter(read=False).count()
    return 0

@register.simple_tag
def get_notifications(user, limit=None):
    """
    Returns the notifications for a user, optionally limited to a specific number.
    Usage: {% get_notifications user limit=5 as notifications %}
    """
    if user.is_authenticated:
        notifications = user.notifications.all().order_by('-created_at')
        if limit:
            notifications = notifications[:limit]
        return notifications
    return []

@register.filter
def timesince_short(value):
    """
    Returns a shorter version of Django's timesince filter.
    Usage: {{ value|timesince_short }}
    """
    if not value:
        return ''
    
    from django.utils import timezone
    from datetime import timedelta
    
    now = timezone.now()
    diff = now - value
    
    if diff < timedelta(minutes=1):
        return 'ahora'
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f'{minutes}m'
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f'{hours}h'
    elif diff < timedelta(days=7):
        days = diff.days
        return f'{days}d'
    elif diff < timedelta(days=30):
        weeks = int(diff.days / 7)
        return f'{weeks}sem'
    elif diff < timedelta(days=365):
        months = int(diff.days / 30)
        return f'{months}mes'
    else:
        years = int(diff.days / 365)
        return f'{years}año'
