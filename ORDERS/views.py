from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib import messages
from decimal import Decimal, ROUND_HALF_UP
from django.http import JsonResponse

from PRODUCTS.models import ProductModel, CartItemModel, CartModel
from ORDERS.models import Ordermodel, OrderItemmodel,Order_Summarymodel
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from user_application.models import User
from PRODUCTS.models import ReviewModel
from PRODUCTS.forms import ReviewForm



class OrderView(View):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            messages.error(request, "Please login to place an order.")
            return redirect('login')
        
        try:
            # Get product and user's default address
            product = ProductModel.objects.get(id=pk)
            
            # Calculate price details
            item_price = product.price
            original_price = (item_price * Decimal('1.1')).quantize(Decimal('0.00'), ROUND_HALF_UP)
            delivery_charges = Decimal('0') if item_price >= 500 else Decimal('40')
            packaging_fee = Decimal('59')
            
            # Calculate savings
            item_savings = (original_price - item_price).quantize(Decimal('0.00'), ROUND_HALF_UP)
            delivery_savings = Decimal('40') if delivery_charges == 0 else Decimal('0')
            total_savings = (item_savings + delivery_savings).quantize(Decimal('0.00'), ROUND_HALF_UP)

            total_payable = (item_price + delivery_charges + packaging_fee).quantize(Decimal('0.00'), ROUND_HALF_UP)

            context = {
                'product': product,
                'price_details': {
                    'item_price': item_price.quantize(Decimal('0.00'), ROUND_HALF_UP),
                    'original_price': original_price,
                    'delivery_charges': delivery_charges,
                    'packaging_fee': packaging_fee,
                    'total_payable': total_payable,
                    'savings': total_savings
                }
            }
            return render(request, 'orderone.html', context)
        except ProductModel.DoesNotExist:
            messages.error(request, "Product not found!")
            return redirect('productlist')
        except Exception as e:
            print(f"Error in OrderView get: {str(e)}")
            messages.error(request, "Error loading order page. Please try again.")
            return redirect('productlist')

    def post(self, request, pk):
        try:
            with transaction.atomic():
                # Get product and quantity
                product = ProductModel.objects.get(id=pk)
                quantity = int(request.POST.get('quantity', 1))
                
                # Calculate total amount
                item_price = (product.price * quantity).quantize(Decimal('0.00'), ROUND_HALF_UP)
                delivery_charges = Decimal('0') if item_price >= 500 else Decimal('40')
                packaging_fee = Decimal('59')
                total_amount = (item_price + delivery_charges + packaging_fee).quantize(Decimal('0.00'), ROUND_HALF_UP)

                # Calculate savings
                original_price = ((product.price * Decimal('1.1')) * quantity).quantize(Decimal('0.00'), ROUND_HALF_UP)
                item_savings = (original_price - item_price).quantize(Decimal('0.00'), ROUND_HALF_UP)
                delivery_savings = Decimal('40') if delivery_charges == 0 else Decimal('0')
                total_savings = (item_savings + delivery_savings).quantize(Decimal('0.00'), ROUND_HALF_UP)

                # Create order
                order = Ordermodel.objects.get(user=request.user)
                
                # Create order item
                OrderItemmodel.objects.create(
                    order_id=order,
                    item=product,
                    quantity=quantity
                )
                
                messages.success(request, "Order placed successfully!")
                return redirect('place_order')

        except ProductModel.DoesNotExist:
            messages.error(request, "Product not found!")
            return redirect('productlist')
        except ValueError:
            messages.error(request, "Invalid quantity specified!")
            return redirect('productdetail', pk=pk)
        except Exception as e:
            print(f"Error in OrderView post: {str(e)}")
            messages.error(request, "Error placing order. Please try again.")
            return redirect('productdetail', pk=pk)

class CartOrderView(View):
    def get(self, request, pk):
        try:
            # Get user's cart and items
            cart = CartModel.objects.get(user=pk)
            cart_items = CartItemModel.objects.filter(cart=cart)

            if not cart_items.exists():
                messages.warning(request, "Your cart is empty!")
                return redirect('cartlist')

            # Calculate price details
            subtotal = Decimal('0')
            original_subtotal = Decimal('0')
            
            # Calculate prices for each item
            for item in cart_items:
                # Calculate current price
                item_price = item.cart_item.price * item.quantity
                subtotal += item_price
                
                # Calculate original price (10% more than current price)
                original_price = (item.cart_item.price * Decimal('1.1')).quantize(Decimal('0.00'), ROUND_HALF_UP)
                original_total = original_price * item.quantity
                original_subtotal += original_total
                
                # Add original price to item for template
                item.original_price = original_price
            
            # Round all calculations
            subtotal = subtotal.quantize(Decimal('0.00'), ROUND_HALF_UP)
            original_subtotal = original_subtotal.quantize(Decimal('0.00'), ROUND_HALF_UP)
            
            # Calculate delivery charges (free for orders ≥ ₹500)
            delivery_charges = Decimal('0') if subtotal >= 500 else Decimal('40')
            
            # Fixed charges
            packaging_fee = Decimal('59')
            
            # Calculate total and savings
            total_payable = (subtotal + delivery_charges + packaging_fee).quantize(Decimal('0.00'), ROUND_HALF_UP)
            item_savings = (original_subtotal - subtotal).quantize(Decimal('0.00'), ROUND_HALF_UP)
            delivery_savings = Decimal('40') if delivery_charges == 0 else Decimal('0')
            total_savings = (item_savings + delivery_savings).quantize(Decimal('0.00'), ROUND_HALF_UP)

            context = {
                'cart': cart_items,
                'price_details': {
                    'item_price': subtotal,
                    'original_price': original_subtotal,
                    'delivery_charges': delivery_charges,
                    'packaging_fee': packaging_fee,
                    'total_payable': total_payable,
                    'savings': total_savings
                }
            }
            return render(request, 'cartorder.html', context)
        except Exception as e:
            print(f"Error in CartOrderView get: {str(e)}")
            messages.error(request, "Error loading checkout page. Please try again.")
            return redirect('cartlist')

    def post(self, request, pk):
        try:
            with transaction.atomic():
                # Verify user's cart exists and has items
                cart = CartModel.objects.get(user=pk)
                cart_items = CartItemModel.objects.filter(cart=cart)
                
                if not cart_items.exists():
                    messages.error(request, "Your cart is empty!")
                    return redirect('cartlist')

                # Calculate final amounts
                subtotal = Decimal('0')
                for item in cart_items:
                    subtotal += item.cart_item.price * item.quantity
                
                subtotal = subtotal.quantize(Decimal('0.00'), ROUND_HALF_UP)
                delivery_charges = Decimal('0') if subtotal >= 500 else Decimal('40')
                packaging_fee = Decimal('59')
                total_amount = (subtotal + delivery_charges + packaging_fee).quantize(Decimal('0.00'), ROUND_HALF_UP)

                # Create new order
                order = Ordermodel.objects.get(user=pk)
                
                # Create order items
                for cart_item in cart_items:
                    OrderItemmodel.objects.create(
                        order_id=order,
                        item=cart_item.cart_item,
                        quantity=cart_item.quantity,
                    )
                
                # Clear the cart
                cart_items.delete()
                
                cart.save()

                messages.success(request, "Order placed successfully!")
                return redirect('place_order')

        except CartModel.DoesNotExist:
            messages.error(request, "Cart not found!")
            return redirect('cartlist')
        except Exception as e:
            print(f"Error in CartOrderView post: {str(e)}")
            messages.error(request, "Error placing order. Please try again.")
            return redirect('cartlist')
        
        
        
        
        
        

        
        
        
        
import razorpay        
class PlaceOrderView(View):
    def get(self,request):
        
        client=razorpay.Client(auth=("rzp_test_BSeqIL8YH41MJu","vsfhgArF8VJEYoQOdSQqWtBl"))
        
        order=Ordermodel.objects.get(user=request.user)
        order_item=OrderItemmodel.objects.filter(order_id=order,status="pending")
        
        
        amount=sum(item.item.price * item.quantity for item in order_item)
        total_amount=amount+59 if amount>=500 else amount+40+59
        
        # Convert total_amount to paise (multiply by 100) and convert to integer
        amount_in_paise = int(total_amount * 100)
        
        payment=client.order.create({'amount': amount_in_paise,'currency':'INR'})
        
        
        
        
        
        print(payment)
        
        # save payment details to the  model Order_Summarymodel
        if payment:
            summary=Order_Summarymodel.objects.create(
                user=request.user,
                order_id=payment.get("id"),
                total_amount=float(payment.get("amount")),
                
            )
            
        context={
            "summary":summary,
            "items":order_item,
            "razor_key_id":"rzp_test_BSeqIL8YH41MJu",
            "order_id":payment.get("id"),
            "total_amount":float(payment.get("amount")),
            
        }     
        return render(request,"payment.html",context)
    
    
    
    
    


@method_decorator(csrf_exempt, name='dispatch')
class SuccessView(View):
    def post(self,request):
        print("payment success")
        user=User.objects.get(id=request.user.id)
        payment=request.POST.get("razorpay_payment_id")
       
        
        if payment:
            summary=Order_Summarymodel.objects.filter(user=user,payment_status=False)
            for item in summary:
                item.payment_status=True
                item.save()
            
            order=Ordermodel.objects.get(user=user)
            order_item=OrderItemmodel.objects.filter(order_id=order,status="pending")
            for item in order_item:
                item.status="completed"
                item.save()
                
            messages.success(request,"Payment successful")
            
            completed_order=Ordermodel.objects.get(user=user)
            completed_order_item=OrderItemmodel.objects.filter(order_id=completed_order,status="completed")
            
            
            for i in completed_order_item:
                item=ProductModel.objects.get(id=i.item.id)
                item.stock-=i.quantity
                item.save()
                
            return render(request,"payment_success.html",{"order_id":completed_order.id,"total_amount":completed_order.total_amount,"payment_id":payment})
            
            
            
        
        
        
        else:
            messages.error(request,"Payment failed")
            return redirect("Home")
        
        

    
    
    
    
    




class OrdersView(View):
    def get(self, request):
        try:
            if not request.user.is_authenticated:
                messages.error(request, "Please login to view your orders.")
                return redirect('login')
            
            # Get all orders for the user
            orders = Ordermodel.objects.filter(user=request.user)
            
            # Get all order items for these orders
            order_items = OrderItemmodel.objects.filter(order_id__in=orders)
            
            # Get existing reviews for these order items
            reviews = ReviewModel.objects.filter(user=request.user, order__in=order_items)
            reviewed_order_ids = [review.order.id for review in reviews]
            
            context = {
                'orders': orders,
                'order_items': order_items,
                'reviewed_order_ids': reviewed_order_ids,
                'reviews': reviews
            }
            
            return render(request, "orderlist.html", context)
            
        except Exception as e:
            print(f"Error in OrdersView: {str(e)}")
            messages.error(request, "Error loading orders. Please try again.")
            return redirect('profile')
        
        
        
class ReviewListView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.error(request, "Please login to view your reviews.")
            return redirect('login')
        
        reviews = ReviewModel.objects.filter(user=request.user).order_by('-posted_date')
        return render(request, "review_list.html", {"reviews": reviews})


class AddReviewView(View):
    def get(self, request, order_item_id):
        try:
            if not request.user.is_authenticated:
                messages.error(request, "Please login to add a review.")
                return redirect('login')
            
            order_item = get_object_or_404(OrderItemmodel, id=order_item_id, order_id__user=request.user)
            
            # Check if review already exists
            existing_review = ReviewModel.objects.filter(user=request.user, order=order_item).first()
            
            if existing_review:
                form = ReviewForm(instance=existing_review)
                is_edit = True
            else:
                form = ReviewForm()
                is_edit = False
            
            context = {
                'form': form,
                'order_item': order_item,
                'is_edit': is_edit
            }
            return render(request, 'add_review.html', context)
            
        except Exception as e:
            print(f"Error in AddReviewView GET: {str(e)}")
            messages.error(request, "Error loading review form. Please try again.")
            return redirect('orders')

    def post(self, request, order_item_id):
        try:
            if not request.user.is_authenticated:
                messages.error(request, "Please login to add a review.")
                return redirect('login')
            
            order_item = get_object_or_404(OrderItemmodel, id=order_item_id, order_id__user=request.user)
            existing_review = ReviewModel.objects.filter(user=request.user, order=order_item).first()
            
            form = ReviewForm(request.POST, instance=existing_review)
            
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.order = order_item
                review.product = order_item.item
                review.save()
                
                messages.success(request, "Review submitted successfully!")
                return redirect('orders')
            
            context = {
                'form': form,
                'order_item': order_item,
                'is_edit': bool(existing_review)
            }
            return render(request, 'add_review.html', context)
            
        except Exception as e:
            print(f"Error in AddReviewView POST: {str(e)}")
            messages.error(request, "Error submitting review. Please try again.")
            return redirect('orders')


class EditReviewView(View):
    def get(self, request, review_id):
        try:
            if not request.user.is_authenticated:
                messages.error(request, "Please login to edit your review.")
                return redirect('login')
            
            review = get_object_or_404(ReviewModel, id=review_id, user=request.user)
            form = ReviewForm(instance=review)
            
            context = {
                'form': form,
                'order_item': review.order,
                'is_edit': True
            }
            return render(request, 'add_review.html', context)
            
        except Exception as e:
            print(f"Error in EditReviewView GET: {str(e)}")
            messages.error(request, "Error loading review form. Please try again.")
            return redirect('review_list')

    def post(self, request, review_id):
        try:
            if not request.user.is_authenticated:
                messages.error(request, "Please login to edit your review.")
                return redirect('login')
            
            review = get_object_or_404(ReviewModel, id=review_id, user=request.user)
            form = ReviewForm(request.POST, instance=review)
            
            if form.is_valid():
                form.save()
                messages.success(request, "Review updated successfully!")
                return redirect('review_list')
            
            context = {
                'form': form,
                'order_item': review.order,
                'is_edit': True
            }
            return render(request, 'add_review.html', context)
            
        except Exception as e:
            print(f"Error in EditReviewView POST: {str(e)}")
            messages.error(request, "Error updating review. Please try again.")
            return redirect('review_list')


class DeleteReviewView(View):
    def post(self, request, review_id):
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'login_required'
            })
        
        try:
            review = get_object_or_404(ReviewModel, id=review_id, user=request.user)
            review.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Review deleted successfully'
            })
            
        except Exception as e:
            print(f"Error deleting review: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })





        
    
    
    
    
    

    
    
   
   
    
        
            
            
            
        
    
    
    

    
 
        
        
        
       
    







