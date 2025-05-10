from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from PRODUCTS.models import CartModel,CartItemModel,ProductModel
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import UserSerializer, AddToCartSerializer
from django.contrib.auth.models import User
from rest_framework.views import APIView



class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user=User.objects.create_user(**serializer.data)
            CartModel.objects.create(user=user)
            
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    
class AddToCart(APIView):    
    
    permission_classes=[IsAuthenticated]
   
    def post(self,request):
        serializer=AddToCartSerializer(data=request.data)
        if serializer.is_valid():
            cart_item=serializer.validated_data['cart_item']
            quantity=serializer.validated_data['quantity']
            
            cart=CartModel.objects.get(user=request.user)
            product=ProductModel.objects.get(id=cart_item)
            cart_item_model=CartItemModel.objects.create(cart=cart,cart_item=product,quantity=quantity)
            
            
            
            return Response({"message":"Item added to cart"},status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

    