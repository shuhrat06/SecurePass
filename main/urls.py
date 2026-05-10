from django.urls import path
from .views import *

urlpatterns = [
    path('',main_view, name='home'),
    path('home/', UserHomeView.as_view(), name='user-home'),
    path('passwords/<int:id>/', PasswordInfoView.as_view(), name='password-info'),
    path('password/generator/', PasswordGeneratorView.as_view(), name='password-generator'),
    path('password/checker/', PasswordCheckerView.as_view(), name='password-checker'),
    path('account/', UserInfoViev.as_view(), name='user-account'),
    path('messages/', UserMessagesView.as_view(), name='user-messages'),
    path('articles/', ArticlesView.as_view(), name='articles'),
    path('articles/<slug:slug>/', ArticleContentView.as_view(), name='article-content')
]