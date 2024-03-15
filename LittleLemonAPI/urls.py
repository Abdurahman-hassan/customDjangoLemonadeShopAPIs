from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from LittleLemonAPI.views import (DeliveryUsersListCreateAPIView,
                                  UserDetailAPIView,
                                  ManagerViewSet,
                                  MenuItemList,
                                  MenuItemDetail
                                  )

router = DefaultRouter()
router.register(r'groups/manager/users', ManagerViewSet, basename='manager-users')

urlpatterns = [
    path('api/', include(router.urls)),

    path('groups/delivery-crew/users', DeliveryUsersListCreateAPIView.as_view(), name='delivery-crew-users'),

    path('groups/delivery-crew/users/<int:id>', UserDetailAPIView.as_view(), name='delivery_crew_user_detail'),

    path('menu-items', MenuItemList.as_view(), name='menu-items'),
    path('menu-items/<int:id>', MenuItemDetail.as_view(), name='menu-item-detail'),

    path('api-token-auth', obtain_auth_token, name='api_token_auth'),
    path('__debug__/', include('debug_toolbar.urls')),

]
urlpatterns += router.urls
