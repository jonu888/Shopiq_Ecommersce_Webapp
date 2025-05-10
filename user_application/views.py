from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.generic import View
from .forms import UserRegistrationForm, UserLoginForm,ForgotForm,OtpForm,ResetPasswordForm
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.models import User
from PRODUCTS.models import ProductModel,Categorymodel
from .models import UserProfile,WishlistModel
from ORDERS.models import Ordermodel,OrderItemmodel
from PRODUCTS.models import CartModel,CartItemModel

import random

class UserRegistrationView(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request,'register_user.html', {'form': form})
    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user=User.objects.create_user(**form.cleaned_data)
            CartModel.objects.create(user=user)
            Ordermodel.objects.create(user=user)
            
            sub='Welcome mail'
            name=form.cleaned_data.get("first_name")+" "+form.cleaned_data.get("last_name")
            email='jo.sanu888@gmail.com'
            Recipient_list=[form.cleaned_data.get('email')]
            msg=f"hi..{name}.welcome to my application"
            
            send_mail(sub,msg,email,Recipient_list,fail_silently=True)
            print("good")
            return render(request, 'welcome_login.html')
        else:
            print('bad')
            form = UserRegistrationForm()
            return render(request, 'register_user.html', {'form': form})


class UserLoginView(View):
    def get(self, request):
        form = UserLoginForm()
        return render(request, 'welcome_login.html', {'form': form})   
    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                print("User logged in successfully")
                return redirect('Home')
            else:
                print("User not found")
                form = UserLoginForm()
                return render(request, 'welcome_login.html', {'form': form})   
            
            
            
            
            
            
            
            
class Forget_password(View):
    def get(self,request):
        form=ForgotForm
        return render(request,'forget_password.html',{'form':form})
    def post(self,request):
        name=request.POST.get('username')
        user=User.objects.get(username=name)
        
        if user:
            sub='Password reset'
            otp=random.randint(1000,9999)
            msg=f'OTP for reset password OTP={otp}'
            
            
            request.session['username']=name
            
            request.session['otp']=otp
            
            send_mail(sub,msg,'jo.sanu888@gmail.com',[user.email],fail_silently=True)
            return redirect('OTP')
        else:
            return render(request,'forget_password.html',{'error':'user not found'})
        


class OtpVerify(View):
    def get(self,request):
        form=OtpForm
        
        return render(request,'Otp_verify.html',{'form':form})
    def post(self,request):
        new_otp=request.POST['otp']
        old_otp=request.session['otp']
        
        if str(new_otp)==str(old_otp):
            print('matched')
            return redirect("reset") 
              
class ResetPassword(View):
    def get(self,request):
        form=ResetPasswordForm
        return render(request,'reset_password.html',{'form':form})
    
    def post(self,request):
        n_pass=request.POST['new_password']
        o_pass=request.POST['confirm_password']
        
        if n_pass == o_pass:
            
            name=request.session['username']
            user=User.objects.get(username=name)
            
            user.set_password(n_pass)
            
            user.save()
            
            send_mail(subject="success",message="password reset succesfully",from_email='jo.sanu888@gmail.com',recipient_list=[user.email],fail_silently=True)
            
            return redirect('login')
            
            
class ProfileView(View):
    def get(self, request):
        try:
            if not request.user.is_authenticated:
                return redirect('login')
            
            user = User.objects.get(username=request.user)
            show_wishlist = request.GET.get('show_wishlist', False)
            
            # Get user's wishlist items
            wishlist_items = WishlistModel.objects.filter(user=user)
            wishlist_count = wishlist_items.count()
            
            # Get or create user profile
            user_profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'phone': user.username,
                    'address_line1': '',
                    'address_line2': '',
                    'city': '',
                    'state': '',
                    'pincode': ''
                }
            )
            
            try:
                orders = Ordermodel.objects.filter(user=user)
            except Ordermodel.DoesNotExist:
                orders = None
            
            try:
                cart_count = CartItemModel.objects.filter(cart__user=user).count()
            except CartItemModel.DoesNotExist:
                cart_count = 0
            
            context = {
                'user': user,
                'profile': user_profile,
                'orders': orders,
                'cart_count': cart_count,
                'show_wishlist': show_wishlist,
                'wishlist_items': wishlist_items if show_wishlist else None,
                'wishlist_count': wishlist_count
            }
            return render(request, 'profile.html', context)
        except Exception as e:
            print(f"Error in ProfileView get: {str(e)}")
            messages.error(request, "Error loading profile page. Please try again.")
            return redirect('Home')
    
    def post(self, request):
        try:
            if not request.user.is_authenticated:
                return redirect('login')
            
            user = request.user
            # Basic user info
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            gender = request.POST.get('gender', '')

            # Address info
            address_line1 = request.POST.get('address_line1', '').strip()
            address_line2 = request.POST.get('address_line2', '').strip()
            city = request.POST.get('city', '').strip()
            state = request.POST.get('state', '').strip()
            pincode = request.POST.get('pincode', '').strip()

            # Validate input data
            if not first_name or not last_name:
                messages.error(request, "First name and last name are required!")
                return redirect('profile')

            if not email:
                messages.error(request, "Email is required!")
                return redirect('profile')

            if not phone:
                messages.error(request, "Phone number is required!")
                return redirect('profile')

            # Update user information
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()

            # Update or create user profile
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.phone = phone
            user_profile.address_line1 = address_line1
            user_profile.address_line2 = address_line2
            user_profile.city = city
            user_profile.state = state
            user_profile.pincode = pincode
            user_profile.gender = gender
            user_profile.save()

            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
            
        except Exception as e:
            print(f"Error in ProfileView post: {str(e)}")
            messages.error(request, "Error updating profile. Please try again.")
            return redirect('profile')
        
        


class AddToWishlistView(View):
    def post(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'login_required'
            })
        
        try:
            product = get_object_or_404(ProductModel, id=pk)
            # Check if item already exists in wishlist
            wishlist_item = WishlistModel.objects.filter(
                user=request.user,
                product=product
            ).first()
            
            if wishlist_item:
                # If item exists, remove it (toggle behavior)
                wishlist_item.delete()
                return JsonResponse({
                    'success': True,
                    'message': 'Removed from your Wishlist'
                })
            
            # Create new wishlist item
            WishlistModel.objects.create(
                user=request.user,
                product=product
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Added to your Wishlist'
            })
            
        except Exception as e:
            print(f"Error managing wishlist: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'server_error'
            })
            
    # Keep the get method for backward compatibility
    def get(self, request, pk):
        return self.post(request, pk)

class RemoveFromWishlistView(View):
    def post(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'login_required'
            })
        
        try:
            wishlist_item = get_object_or_404(WishlistModel, id=pk, user=request.user)
            wishlist_item.delete()
            
            # Get updated wishlist count
            new_count = WishlistModel.objects.filter(user=request.user).count()
            
            return JsonResponse({
                'success': True,
                'wishlist_count': new_count,
                'message': 'Item removed from wishlist successfully'
            })
            
        except Exception as e:
            print(f"Error removing from wishlist: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })








