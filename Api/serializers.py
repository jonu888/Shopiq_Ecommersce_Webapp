from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        
        
class AddToCartSerializer(serializers.Serializer):
    
    cart_item= serializers.IntegerField()
    quantity = serializers.IntegerField()
    
   
        