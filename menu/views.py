# menu/views.py
import os, json
from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from restaurants.models import Restaurant
from .models import MenuItem
from menu.serializers import MenuItemSerializer
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import os, json
from decimal import Decimal, InvalidOperation
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from restaurants.models import Restaurant
from .models import MenuItem
from .serializers import MenuItemSerializer
from rest_framework import viewsets

# menu/views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from rest_framework.response import Response

from .models import MenuItem
from .serializers import MenuItemSerializer
from restaurants.models import Restaurant
from django.views.generic import TemplateView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication  # optional




class ApiDemoView(TemplateView):
    template_name = "api_demo.html"

class MenuItemViewSet(viewsets.ModelViewSet):
    """
    Replaces the old MenuItemAPI FBV.

    - Only authenticated users can access
    - All actions are scoped to the restaurant owned by the current user
    - On create, restaurant FK is automatically attached
    """
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]  # 👈 add this

    def _get_restaurant(self):
        """Return the restaurant linked to this user, or raise 400 like before."""
        user = self.request.user
        restaurant = Restaurant.objects.filter(owner=user).first()
        if not restaurant:
            # Equivalent to: Response({"detail": ...}, status=400)
            raise ValidationError({"detail": "This user is not linked to any restaurant."})
        return restaurant

    def get_queryset(self):
        """
        Limit all operations (list/retrieve/update/delete) to
        menu items belonging to the current user's restaurant.
        """
        restaurant = self._get_restaurant()
        return MenuItem.objects.filter(restaurant=restaurant)

    def perform_create(self, serializer):
        """
        Attach the restaurant FK automatically when creating.
        Same as: serializer.save(restaurant=restaurant)
        in your FBV.
        """
        restaurant = self._get_restaurant()
        serializer.save(restaurant=restaurant)



from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import MenuItem
from restaurants.models import Restaurant
from django.db.models import Exists
# from menu_search import main

class RestaurantMenuViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MenuItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        restaurant_id = self.kwargs.get("restaurant_id")

        # If restaurant doesn't exist, return empty queryset
        if not Restaurant.objects.filter(id=restaurant_id).exists():
            return MenuItem.objects.none()

        return MenuItem.objects.filter(
            restaurant_id=restaurant_id,
            available=True,   # optional
        )
    


    

