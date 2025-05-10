"""
URL configuration for ECOMMERCE project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from user_application.views import *
from PRODUCTS.views import *
from django.conf import settings
from django.conf.urls.static import static
from ORDERS.views import *
from django.views.decorators.csrf import csrf_exempt




def shopiq(request):
    return redirect('login')


urlpatterns = [
    
    
    # admin
    path('admin/', admin.site.urls),
    
    path('',shopiq),
    
    
    
    # user
    path('SHOPIQ/',UserLoginView.as_view(),name='login'),
    
    path('user_application/register/', UserRegistrationView.as_view(), name='register'),
   
    path('user_application/logout/', UserLogoutView.as_view(), name='logout'),
    
    path('user_application/profile/', ProfileView.as_view(), name='profile'),
    
    path('Forgotpassword/',Forget_password.as_view(),name='password_reset'),
    path('OTP_verify/',OtpVerify.as_view(),name="OTP"),
    path('Password/',ResetPassword.as_view(),name='reset'),
    
    
    # product
    path('PRODUCTS/addcategory/',Addcategory.as_view(),name='addcategory'),
    path('PRODUCTS/updatecategory/<int:pk>/',Updatecategory.as_view(),name='updatecategory'),
    
    path('PRODUCTS/addproduct/',AddProductView.as_view(),name="addproduct"),
    path('PRODUCTS/updateproduct/<int:pk>/',UpdateProductView.as_view(),name="updateproduct"),
    path('PRODUCTS/deleteproduct/<int:pk>/',Deleteproductview.as_view(),name="deleteproduct"),
    
    path('PRODUCTS/categorylist/',CategoryListview.as_view(),name="categorylist"),
    path('PRODUCTS/productlist/', ProductListView.as_view(), name="productlist"),
    
    path('PRODUCTS/productdetail/<int:pk>/',ProductDetailsView.as_view(),name="productdetail"),
    path('PRODUCTS/categorydetail/<int:pk>/',CategoryDetailView.as_view(),name="categorydetail"),
    
    
    
    
    
    
    # cart
    path('PRODUCTS/addto_cart/<int:pk>/',Add_to_cart.as_view(),name="add_cart"),
    
    
    path('PRODUCTS/cartlist/',CartListView.as_view(),name="cartlist"),
    path('PRODUCTS/cartincrement/<int:pk>/',Increament_QuantityView.as_view(),name="cart_increment"),
    path('PRODUCTS/cartdecrement/<int:pk>/',Decrement_QuantityView.as_view(),name="cart_decrement"),
    path('PRODUCTS/cartdelete/<int:pk>/',CartItemDeleteView.as_view(),name="cart_delete"),
    
    
    
    
    
    
    
    # home
    path('PRODUCTS/Home/',Homeview.as_view(),name="Home"),
    
    
    
    
    
    # order
    path('ORDERS/orderone/<int:pk>/',OrderView.as_view(),name="orderone"),  
    path('ORDERS/cartorder/<int:pk>/',CartOrderView.as_view(),name="cartorder"),
    path('ORDERS/place_order/',PlaceOrderView.as_view(),name="place_order"),
    path('ORDERS/orders/',OrdersView.as_view(),name="orders"),
   
    
    
    # payment
   
    path('ORDERS/success/',SuccessView.as_view(),name="success"),
    
    
    # wishlist
    
    
    path('add-to-wishlist/<int:pk>/', AddToWishlistView.as_view(), name='add_to_wishlist'),
    path('remove-from-wishlist/<int:pk>/', RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
    
    
    #review
    path('ORDERS/review_list/',ReviewListView.as_view(),name="review_list"),
    path('ORDERS/add_review/<int:order_item_id>/',AddReviewView.as_view(),name="add_review"),
    path('ORDERS/edit_review/<int:review_id>/',EditReviewView.as_view(),name='edit_review'),
    path('ORDERS/delete_review/<int:review_id>/',DeleteReviewView.as_view(),name='delete_review'),
    
    
    
    
    path('api/', include('Api.urls')),
    
    
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
