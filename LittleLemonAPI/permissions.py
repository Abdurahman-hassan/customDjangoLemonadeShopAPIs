from rest_framework import permissions

""" This is a permission class that we can use to limit the access to the API. """


class IsManagerUser(permissions.BasePermission):
    """
    Custom permission to only allow users in the manager group to access the endpoint.
    """

    def has_permission(self, request, view):
        # Check if the user is in the manager group
        return request.user.groups.filter(name='Manager').exists()


class IsDelivery(permissions.BasePermission):
    """
    Custom permission to only allow users in the delivery group to access the endpoint.
    """

    def has_permission(self, request, view):
        # Check if the user is in the delivery group
        return request.user.groups.filter(name='Delivery-crew').exists()
