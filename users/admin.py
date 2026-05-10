from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name'
    )
    list_display_links = (
        'id', 'username'
    )
    search_fields = (
        'username', 'email', 'first_name', 'last_name'
    )
    list_per_page = 50
    list_max_show_all = 150
    class Media:
        css = {
            'all': ('admin/css/hide_related_buttons.css',)
        }