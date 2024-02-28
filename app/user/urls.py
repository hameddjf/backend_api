"""
url mappings for the user api.
"""

from django.urls import path

from .views import CreatUserView, CreateTokenView, ManageUserView

app_name = 'user'
urlpatterns = [
    path('create/', CreatUserView.as_view(), name='create_page'),
    path('token/', CreateTokenView.as_view(), name='token_page'),
    path('me/', ManageUserView.as_view(), name='me_page'),


]
