from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from LittleLemonAPI.permissions import IsManagerUser
from LittleLemonAPI.serializers import UserMembershipSerializer
from LittleLemonAPI.utils import get_group_users, add_user_to_group, remove_user_from_group


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
