from django.db import models
from user_application.models import User

from PRODUCTS.models import ProductModel






class Ordermodel(models.Model):  
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    
    created_at=models.DateTimeField(auto_now_add=True)
    





class OrderItemmodel(models.Model):
    order_id=models.ForeignKey(Ordermodel,on_delete=models.CASCADE)
    
    item=models.ForeignKey(ProductModel,on_delete=models.CASCADE)
    
    quantity=models.PositiveIntegerField(default=1)      
    
    status=models.CharField(max_length=100,choices=[('pending','pending'),('completed','completed'),('canceled','canceled')],default='pending')
    
    
class Order_Summarymodel(models.Model):
    
   
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    
    order_id=models.CharField(max_length=100)
    
    payment_status=models.BooleanField(default=False)
    
    payment_id=models.CharField(max_length=100,null=True,blank=True)
    
    total_amount=models.FloatField(default=0)
    
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    
    
    
   