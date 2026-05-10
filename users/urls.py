from django.urls import path, include
from .views import *

urlpatterns = [
    path('registration/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/set-master-password/', MasterPasswordView.as_view(), name='set-master-password'),
    path('user/master-password/confirm/', MasterPasswordConfirmView.as_view(), name='master-password-confirm'),
    path('user/update-master-password/', UpdateMasterPassword.as_view(), name='update-master-password'),
    path('user/enter-master-password/', EnterMasterPasswordView.as_view(), name='enter-master-password'),

    path(
        "google_sso/", include("django_google_sso.urls", namespace="django_google_sso")
    ),
    path("google_sso/check/", GoogleSSOCheck.as_view(), name='google-sso-check'),
    path('captcha/', include('captcha.urls')),

]