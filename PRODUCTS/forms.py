from django import forms
from PRODUCTS.models import ProductModel,ReviewModel,CartModel



class AddProductForm(forms.ModelForm):
    
    class Meta:
        model=ProductModel
        
        fields=['name','description','price','stock','category','image']
        
        
class ReviewForm(forms.ModelForm):
    
    class Meta:
        model=ReviewModel
        
        fields=['rating','comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience with this product...'})
        }
        

class Cartform(forms.ModelForm):
    
    class Meta:
        model=CartModel
        
        fields='__all__'        
    