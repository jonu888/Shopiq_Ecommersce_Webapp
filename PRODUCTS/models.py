from django.db import models

from django.contrib.auth.models import User


# Create your models here.
class Categorymodel(models.Model):

    name=models.CharField(max_length=100)

    description=models.TextField()
    
    
    def __str__(self):
        return self.name



class ProductModel(models.Model):

    name = models.CharField(max_length=100)

    description=models.TextField()

    price=models.DecimalField(max_digits=10,decimal_places=2)

    stock= models.PositiveIntegerField()

    category=models.ForeignKey(Categorymodel,on_delete=models.CASCADE)

    image= models.ImageField(upload_to='product_image')

    created_at = models.DateField(auto_now_add=True)
    
    
    def __str__(self):
        return self.name
    
    
class ReviewModel(models.Model):
    product=models.ForeignKey(ProductModel,on_delete=models.CASCADE,related_name="reviews",null=True,blank=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="reviews_user",null=True,blank=True)
    
    rating=models.IntegerField(default=0,choices=[(i,i) for i in range(1,6)])
    
    comment=models.TextField()
    
    posted_date=models.DateField(auto_now=True)
    
    order=models.ForeignKey('ORDERS.OrderItemmodel',on_delete=models.CASCADE,related_name="reviews_order",null=True,blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    
    
    
    
class CartModel(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    created_date=models.DateField(auto_now_add=True)
    
    
    @property
    def total_price(self):
        return sum(i.cart_item.price*i.quantity for i in self.cartitemmodel_set.all())
        
    
    
class CartItemModel(models.Model):
    cart=models.ForeignKey(CartModel,on_delete=models.CASCADE)
    
    cart_item=models.ForeignKey(ProductModel,on_delete=models.CASCADE)
    
    quantity=models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return self.cart_item.name  
    
    
        
    
    
                
    
   
    
    
    
    