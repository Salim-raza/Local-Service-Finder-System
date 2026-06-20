from rest_framework.permissions import BasePermission
from .models import*

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.role == "ADMIN"
    
class IsAdminORServiceProvider(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.role == "admin" or "SERVICE_PROVIDER"
    
class IsServiceProvider(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return getattr(user, "role", None) == "SERVICE_PROVIDER"
    
class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return getattr(user, "role", None) == "CUSTOMER"