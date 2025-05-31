from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission to only allow administrators.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsManager(permissions.BasePermission):
    """
    Permission to only allow managers and administrators.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
                request.user.is_admin or request.user.is_manager
        )


class IsCook(permissions.BasePermission):
    """
    Permission to only allow cooks, managers, and administrators.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
                request.user.is_admin or request.user.is_manager or request.user.is_cook
        )


class ReadOnly(permissions.BasePermission):
    """
    Permission to only allow read-only access.
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS