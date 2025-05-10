from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, DetailView, View
from django.shortcuts import redirect
from PRODUCTS.models import Categorymodel, ProductModel, ReviewModel, CartModel, CartItemModel
from django.views import View
from django.http import JsonResponse
from django.db.models import Q
from decimal import Decimal

from PRODUCTS.forms import AddProductForm, ReviewForm, Cartform
from django.urls import reverse_lazy

from user_application.models import User

from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from random import sample





        
        
        
def user_login(fn): 
    def wrap(request,**kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            return fn(request,**kwargs)
    return wrap
           
        










class Addcategory(CreateView):
    model=Categorymodel
    
    template_name='addcategory.html'
    
    fields='__all__'
    
    success_url=reverse_lazy('register')


class Updatecategory(UpdateView):
     model=Categorymodel
    
     template_name='update_category.html'
    
     fields='__all__'
    
     success_url=reverse_lazy('register')
     
     
class AddProductView(CreateView):
    model = ProductModel
    template_name="addproduct.html"
    
    fields=['name','description','price','stock','category','image']
    
    success_url=reverse_lazy('register')

    
class UpdateProductView(UpdateView):
    model = ProductModel
    template_name="updateproduct.html"
    
    fields=['name','description','price','stock','category','image']
    
    success_url=reverse_lazy('register')  
    
    
class Deleteproductview(DeleteView):
    model=ProductModel
    template_name='confirm_delete.html'
    success_url=reverse_lazy('register')      


class CategoryListview(ListView):
    model=Categorymodel
    
    template_name='categorylist.html'
    
    context_object_name='data'
    
    success_url=reverse_lazy('register')
    
    
class ProductListView(View):
    def get(self, request, *args, **kwargs):
        categories = Categorymodel.objects.all()
        selected_categories = request.GET.getlist('category')
        search_query = request.GET.get('search', '')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        sort = request.GET.get('sort')

        # Initialize queryset with all products
        products = ProductModel.objects.all()

        # Apply search filter if exists
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Apply category filter if selected and not 'all'
        if selected_categories and 'all' not in selected_categories:
            products = products.filter(category__id__in=selected_categories)

        # Apply price filters if they exist
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

        # Apply sorting
        if sort == 'price_low':
            products = products.order_by('price')
        elif sort == 'price_high':
            products = products.order_by('-price')

        context = {
            'data': products,
            'categories': categories,
            'selected_categories': selected_categories,
            'search_query': search_query
        }
        return render(request, 'productlist.html', context)
    
    
      
    
    
class ProductDetailsView(DetailView):
    """Display detailed information about a specific product"""
    model = ProductModel
    template_name = 'productdetail.html'  
    context_object_name = 'data'
    
    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            
            # Calculate original and discounted prices
            product = self.object
            discount_percentage = 10  # 10% discount
            original_price = product.price * (100 + discount_percentage) / 100
            context['original_price'] = original_price
            context['discount_percentage'] = discount_percentage
            
            # Check if product is in cart
            if self.request.user.is_authenticated:
                try:
                    cart = CartModel.objects.get(user=self.request.user)
                    in_cart = CartItemModel.objects.filter(cart=cart, cart_item=self.object).exists()
                    context['in_cart'] = in_cart
                except CartModel.DoesNotExist:
                    context['in_cart'] = False
            else:
                context['in_cart'] = False
            
            return context
        except Exception as e:
            print(f"Error in ProductDetailsView: {e}")
            context['error_message'] = 'Unable to load product details'
            return context


class CategoryDetailView(DetailView):
    """Display detailed information about a specific category"""
    model=Categorymodel
    
    template_name='category_detail.html'
    
    context_object_name='data'
    
    succes_url=reverse_lazy('register')
    
    

        
    
    
    
    
    
    
    
    
# review





  
    
    
    
@method_decorator(user_login,name='dispatch')  
class Add_to_cart(View):
    """Add a product to user's cart"""
    def get(self, request, **kwargs):
        try:
            id = kwargs.get('pk')
            item = ProductModel.objects.get(id=id)
            
            if item.stock > 0:
                cart = CartModel.objects.get(user=request.user)
                # Check if item already exists in cart
                cart_item, created = CartItemModel.objects.get_or_create(cart=cart, cart_item=item)
                if not created:
                    # Item already exists in cart
                    pass
        
            # Redirect back to the product detail page
            return redirect('productdetail', pk=id)    # Make sure 'product_detail' is your URL name for product details
        except Exception as e:
            print(f"Error in Add_to_cart: {e}")
            return redirect('productdetail', pk=id)   
                  
                  
@method_decorator(user_login,name='dispatch')                 
class CartListView(View):
    """Display user's cart with items and total calculations"""
    def get(self, request):
        try:
            cart = CartModel.objects.get(user=request.user)
            cart_items = CartItemModel.objects.filter(cart=cart)
            
            # Calculate subtotals and total
            for item in cart_items:
                item.subtotal = item.quantity * item.cart_item.price
                # Calculate savings (assuming 10% discount)
                item.original_price = item.cart_item.price * Decimal('1.1')  # Convert 1.1 to Decimal
                item.savings = (item.original_price - item.cart_item.price) * item.quantity
            
            subtotal = sum(item.subtotal for item in cart_items)
            total_savings = sum(item.savings for item in cart_items)
            
            # Add delivery fee if subtotal is less than 500
            free_delivery_threshold = Decimal('500')
            delivery_fee = Decimal('40') if subtotal < free_delivery_threshold else Decimal('0')
            
            # Calculate remaining amount for free delivery
            remaining_for_free_delivery = free_delivery_threshold - subtotal if subtotal < free_delivery_threshold else Decimal('0')
            
            # Calculate final total
            total = subtotal + delivery_fee
            
            secure_packaging = Decimal('59')  # Secure packaging fee
            total += secure_packaging
            
            context = {
                'cart_items': cart_items,
                'subtotal': subtotal,
                'delivery_fee': delivery_fee,
                'secure_packaging': secure_packaging,
                'total_savings': total_savings,
                'total': total,
                'free_delivery_threshold': free_delivery_threshold,
                'remaining_for_free_delivery': remaining_for_free_delivery,
            }
            return render(request, 'cartlist.html', context)
        except CartModel.DoesNotExist:
            print("Cart does not exist for user")
            return render(request, 'cartlist.html', {'error_message': 'Your cart is empty'})
        except Exception as e:
            print(f"Error in CartListView: {e}")
            return render(request, 'cartlist.html', {'error_message': 'Unable to load cart'})
     
     
     
   

@method_decorator(user_login,name='dispatch')
class Increament_QuantityView(View):
    """Increase quantity of cart item"""
    def get(self, request, **kwargs):
        try:
            id = kwargs.get('pk')
            cartdata = CartModel.objects.get(user=request.user)
            item = CartItemModel.objects.get(id=id, cart=cartdata)
            if item.cart_item.stock > item.quantity:  # Ensure stock is available
                item.quantity += 1
                item.save()  
            subtotal = item.quantity * item.cart_item.price
            total = sum(i.quantity * i.cart_item.price for i in CartItemModel.objects.filter(cart=cartdata))
            return JsonResponse({'success': True, 'quantity': item.quantity, 'subtotal': subtotal, 'total': total})
        except Exception as e:
            print(f"Error in Increament_QuantityView: {e}")
            return JsonResponse({'success': False, 'error': 'Unable to update quantity'})
       
       
     
                 
    
@method_decorator(user_login,name='dispatch')        
class Decrement_QuantityView(View):
    """Decrease quantity of cart item"""
    def get(self, request, **kwargs):
        try:
            id = kwargs.get('pk')
            cartdata = CartModel.objects.get(user=request.user)
            item = CartItemModel.objects.get(id=id, cart=cartdata)
            if item.quantity > 1:  # Ensure quantity doesn't go below 1
                item.quantity -= 1
                item.save()
            
            subtotal = item.quantity * item.cart_item.price if item.quantity > 0 else 0
            total = sum(i.quantity * i.cart_item.price for i in CartItemModel.objects.filter(cart=cartdata))
            return JsonResponse({'success': True, 'quantity': item.quantity if item.quantity > 0 else 0, 'subtotal': subtotal, 'total': total})
        except Exception as e:
            print(f"Error in Decrement_QuantityView: {e}")
            return JsonResponse({'success': False, 'error': 'Unable to update quantity'})
    
    
@method_decorator(user_login,name='dispatch')    
class CartItemDeleteView(View):
    """Delete item from cart"""
    def get(self, request, **kwargs):
        try:
            id = kwargs.get('pk')
            cart=CartModel.objects.get(user=request.user)
            item = CartItemModel.objects.get(id=id, cart=cart)
            if item:
             item.delete()
             return redirect('cartlist') 
            else :
             return redirect('login')    
        except Exception as e:
            print(f"Error in CartItemDeleteView: {e}")
            return redirect('cartlist')    
     
     
class UserLogoutView(View):
    """Handle user logout"""
    def get(self,request):
        try:
            logout(request)
            return redirect('login')    
        except Exception as e:
            print(f"Error in UserLogoutView: {e}")
            return redirect('login')    
    







class Homeview(View):
    """Display homepage with random categories and their products"""
    def get(self, request):
        try:
            # Get random top offer products
            all_products = ProductModel.objects.all()
            top_offers = sample(list(all_products), min(8, len(all_products)))
            
            # Calculate original prices for top offers (10% higher)
            for product in top_offers:
                product.original_price = float(product.price) * 1.1

            # Get exactly 3 random categories
            categories = list(Categorymodel.objects.all())
            if len(categories) > 3:
                random_categories = sample(categories, 3)
            else:
                random_categories = categories

            category_data = []

            # Get 5 random products for each category
            for category in random_categories:
                products = list(ProductModel.objects.filter(category=category))
                if products:
                    if len(products) > 5:
                        selected_products = sample(products, 5)
                    else:
                        selected_products = products
                        
                    # Calculate original prices for category products
                    for product in selected_products:
                        product.original_price = float(product.price) * 1.1
                        
                    category_data.append({
                        'category': category,
                        'category_id': category.id,
                        'products': selected_products
                    })

            context = {
                'category_data': category_data,
                'top_offers': top_offers
            }
            return render(request, 'home.html', context)
        except Exception as e:
            print(f"Error in Homeview: {e}")
            return render(request, 'home.html', {'error_message': 'Unable to load homepage content'})










