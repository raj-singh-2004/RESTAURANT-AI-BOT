# menu/admin.py
from django.contrib import admin
from .models import MenuItem


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("id","name", "restaurant", "price", "available", "category")
    list_filter = ("available", "restaurant")
    search_fields = ("name", "description", "restaurant__name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("restaurant", "-category")

    # ---------- queryset scoping ----------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user

        # superuser / superadmin: see all menu items
        if user.is_superuser or getattr(user, "is_superadmin", False):
            return qs

        # restaurant admin: only items for their restaurant(s)
        if getattr(user, "is_restaurant_admin", False):
            return qs.filter(restaurant__owner=user)

        # others: nothing
        return qs.none()

    # ---------- view permission ----------
    def has_view_permission(self, request, obj=None):
        user = request.user

        if user.is_superuser or getattr(user, "is_superadmin", False):
            return True

        if not getattr(user, "is_restaurant_admin", False):
            return False

        if obj is None:
            # changelist view; rows already filtered in get_queryset
            return True

        # Only view items belonging to their own restaurant(s)
        return obj.restaurant.owner_id == user.id

    # ---------- change permission ----------
    def has_change_permission(self, request, obj=None):
        user = request.user

        if user.is_superuser or getattr(user, "is_superadmin", False):
            return True

        if not getattr(user, "is_restaurant_admin", False):
            return False

        if obj is None:
            # allow list page; individual rows checked below
            return True

        return obj.restaurant.owner_id == user.id
    
    # ---------- add permission ----------
    def has_add_permission(self, request):
        user = request.user
        # Usually: superadmins + restaurant admins can add menu items
        if user.is_superuser or getattr(user, "is_superadmin", False):
            return True
        if getattr(user, "is_restaurant_admin", False):
            return True
        return False
    
    # ---------- delete permission ----------
    def has_delete_permission(self, request, obj=None):
        # Same rule as change_permission
        return self.has_change_permission(request, obj)
    
