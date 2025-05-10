
from django.urls import path, include
from .views import UserRegistrationView

from Api.views import AddToCart


from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView


urlpatterns = [
    
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('token/',TokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('token/refresh/',TokenRefreshView.as_view(),name='token_refresh'),
    
    
    path('add_to_cart/',AddToCart.as_view(),name='add_to_cart'),
]

