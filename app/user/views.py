"""
views for the user api.
"""
from rest_framework import generics

from user.serializers import UserSerializer


# handle http post request , for create objects
class CreatUserView(generics.CreateAPIView):
    """create a new user in the system."""
    serializer_class = UserSerializer
