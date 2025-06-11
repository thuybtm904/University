"""
URL configuration for university_project project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('university_app.urls')),  # Include URLs from our app
]

# Configure error handlers
handler404 = 'university_project.error_handlers.handler404'
handler500 = 'university_project.error_handlers.handler500'
