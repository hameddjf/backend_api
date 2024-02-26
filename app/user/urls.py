"""
url mappings for the user api.
"""

from django.urls import path

from .views import CreatUserView

app_name = 'user'
urlpatterns = [
    path('create/', CreatUserView.as_view(), name='create_page')
]
