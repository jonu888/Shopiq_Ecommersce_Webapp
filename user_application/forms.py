from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ('username','email', 'password','first_name','last_name')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    
class UserLoginForm(forms.Form):
    class Meta:
        model = User
        fields = ('username','password')
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    
    
class ForgotForm(forms.Form):
    username=forms.CharField(max_length=100)
    
    
class OtpForm(forms.Form):
    otp=forms.CharField(max_length=10)    
    
class ResetPasswordForm(forms.Form):
    new_password=forms.CharField(max_length=100)
    confirm_password=forms.CharField(max_length=100)
    
        
    
       
    

