from django.contrib import admin
from .models import Messages, Category, Article, Content, Comment

@admin.register(Messages)
class MessagesAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'for_all', 'user', 'title', 'published'
    )

    list_display_links = (
        'id', 'title'
    )

    list_filter = (
        'for_all', 'user'
    )

    search_fields = (
        'title', 'user'
    )

    list_editable = (
        'for_all', 'published', 'user'
    )

    list_per_page = 50
    list_max_show_all = 150

    class Media:
        css = {
            'all': ('admin/css/hide_related_buttons.css',)
        }

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title'
    )
    list_display_links = (
        'id',
    )
    list_editable = (
        'title', 
    )
    list_per_page = 50
    list_max_show_all = 150

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'category', 'title', 'author', 'important', 'published'
    )
    list_display_links = (
        'id',
    )
    list_editable = (
        'category', 'title', 'author', 'important', 'published'
    )
    list_filter = (
        'category', 'important', 'published', 'author'
    )
    search_fields = (
        'title', 'intro'
    )
    list_per_page = 50
    list_max_show_all = 150

    class Media:
        css = {
            'all': ('admin/css/hide_related_buttons.css',)
        }

admin.site.register(Content)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'author', 'article', 'text'
    )
    list_display_links = (
        'id', 'text'
    )
    list_filter = (
        'author', 'article'
    )
    list_per_page = 50
    list_max_show_all = 150
    class Media:
        css = {
            'all': ('admin/css/hide_related_buttons.css',)
        }