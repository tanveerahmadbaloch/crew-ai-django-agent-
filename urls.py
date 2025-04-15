from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from crewai_app import views as crewai_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('crewai_app.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='crewai_app/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('accounts/signup/', crewai_views.signup, name='signup'),
]
