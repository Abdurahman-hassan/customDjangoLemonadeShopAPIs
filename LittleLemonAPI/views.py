from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from LittleLemonAPI.permissions import IsManagerUser, IsDelivery, IsOrderOwnerOrStaff
from LittleLemonAPI.serializers import (
    UserMembershipSerializer,
    MenuItemSerializer,
    CartSerializer,
    OrderSerializer
)
from LittleLemonAPI.utils import get_group_users, add_user_to_group, remove_user_from_group
from .models import MenuItem, Cart, Order, OrderItem


class ManagerViewSet(viewsets.ModelViewSet):
    serializer_class = UserMembershipSerializer
    permission_classes = [IsAuthenticated, IsManagerUser]

    def get_queryset(self):
        return get_group_users('Manager')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        add_user_to_group(username, 'Manager')
        return Response({"status": f"User {username} added to the Manager group"}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        remove_user_from_group(user_id, 'Manager')
        return Response({"status": f"User with ID {user_id} removed from the Manager group"}, status=status.HTTP_200_OK)


class DeliveryUsersListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = UserMembershipSerializer
    permission_classes = [IsAuthenticated, IsManagerUser]

    def get_queryset(self):
        return get_group_users('Delivery-crew')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        add_user_to_group(username, 'Delivery-crew')
        return Response({"status": f"User {username} added to the Delivery-crew group"}, status=status.HTTP_201_CREATED)


class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserMembershipSerializer
    permission_classes = [IsAuthenticated, IsManagerUser]
    lookup_field = 'id'

    def get_queryset(self):
        # This method is intended to filter users, but for removing a user from a group,
        # it does not need to be modified. It's here for completeness of the APIView.
        return super().get_queryset().filter(groups__name='Delivery-crew')

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()  # DRF method to fetch the object based on URL parameters
        remove_user_from_group(user.id, 'Delivery-crew')
        # Return a response indicating the user was successfully removed from the group
        return Response({"status": f"User {user.username} removed from the Delivery-crew group"},
                        status=status.HTTP_200_OK)


class MenuItemList(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsManagerUser, ]
        else:
            self.permission_classes = [permissions.AllowAny, ]
        return super(MenuItemList, self).get_permissions()


class MenuItemDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsManagerUser, ]
        else:
            self.permission_classes = [permissions.AllowAny, ]
        return super(MenuItemDetail, self).get_permissions()


class CartListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartDestroyAPIView(generics.DestroyAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        self.get_queryset().delete()
        return Response({"status": "Cart deleted"}, status=status.HTTP_200_OK)


class OrderListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if IsManagerUser().has_permission(self.request, None):
            return Order.objects.all()
        elif IsDelivery().has_permission(self.request, None):
            return Order.objects.filter(delivery_crew=self.request.user)
        else:
            return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        cart_items = Cart.objects.filter(user=self.request.user)
        order = serializer.save(user=self.request.user)
        # for item in cart_items:
        #     OrderItem.objects.create(order=order, menu_item=item.menu_items, quantity=item.quantity,
        #                              unit_price=item.unit_price, price=item.price)
        order_items = [OrderItem(order=order, menu_item=item.menu_items,
                                 quantity=item.quantity,
                                 unit_price=item.unit_price,
                                 price=item.price) for item in cart_items]
        OrderItem.objects.bulk_create(order_items)
        cart_items.delete()


class OrderDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'orderId'

    def get_queryset(self):
        if IsManagerUser().has_permission(self.request, self):
            return Order.objects.all()
        elif IsDelivery().has_permission(self.request, self):
            return Order.objects.filter(delivery_crew=self.request.user)
        else:
            return Order.objects.filter(user=self.request.user)

    def get_permissions(self):
        """
        Dynamically assign permissions based on request method.
        """
        if self.request.method == 'GET':
            self.permission_classes = [IsAuthenticated, IsOrderOwnerOrStaff]
        elif self.request.method == 'PATCH':
            self.permission_classes = [IsAuthenticated, IsManagerUser | IsDelivery]
        elif self.request.method in ['DELETE', 'PUT']:
            self.permission_classes = [IsAuthenticated, IsManagerUser]
        return super(OrderDetailAPIView, self).get_permissions()

    def get_object(self):
        """Retrieve and return the order for the current authenticated user."""
        # obj = super().get_object()
        # Check if the user has the right permissions to access the order
        # if not IsOrderOwnerOrStaff().has_object_permission(self.request, self, obj):
        #     return Response({"detail": "No Order matches the given query."}, status=status.HTTP_404_NOT_FOUND)
        # return obj

        try:
            obj = super().get_object()
            # Check if the user has the right permissions to access the order
            self.check_object_permissions(self.request, obj)
            return obj
        except Http404:
            # You can raise a Http404 with a custom message like this
            raise Http404("No Order matches the given query.")

    def update(self, request, *args, **kwargs):
        """
        Overridden to restrict field updates based on user role.
        """
        if IsDelivery().has_permission(request, self):
            # Limit delivery crew to updating only the status field
            if set(request.data.keys()) - {'status'}:
                return Response({"detail": "You do not have permission to change fields other than 'status'."},
                                status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
