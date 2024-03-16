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


# TODO: Add a new permission class that will allow only users who are not in the delivery group to access the endpoint.

# class IsNotDelivery(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return not request.user.groups.filter(name='Delivery-crew').exists()


class IsOrderOwnerOrStaff(permissions.BasePermission):
    """Custom permission to only allow owners of an order to see it, or staff under certain conditions."""

    def has_object_permission(self, request, view, obj):
        # Allow order owners to view
        if obj.user == request.user:
            return True
        # Allow Managers and Delivery Crew special permissions
        return request.user.groups.filter(name__in=['Manager', 'Delivery-crew']).exists()
