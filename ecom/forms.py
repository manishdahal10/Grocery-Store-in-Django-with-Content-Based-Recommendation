from django import forms
from django.contrib.auth.models import User
from . import models
from .models import Customer
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError

class CustomerUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput(), 
        }
        help_texts = {
            'username': '',
            
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise ValidationError("Username already exists.")
        return username

    def save(self, commit=True, user=None):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')

        if password:  # Only update the password if the user has entered one
            user.set_password(password)
        else:
           
            user.password = self.instance.password

        if commit:
            user.save()

            
            if password:
                user = authenticate(username=user.username, password=password)
                if user is not None:
                    login(user)

        return user
    
    
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['address', 'mobile', 'profile_pic']

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if len(mobile) != 10 or not mobile.isdigit():
            raise forms.ValidationError("Mobile number must be 10 digits")
        return mobile

    

    def clean_profile_pic(self):
        profile_pic = self.cleaned_data.get('profile_pic')

    # Only validate the content type if there's a new file uploaded
        if profile_pic and hasattr(profile_pic, 'content_type'):
            if not profile_pic.content_type.startswith('image/'):
               raise forms.ValidationError("File must be a valid image")
        elif not profile_pic:
               raise forms.ValidationError("Profile picture is required")

        return profile_pic



class ProductForm(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = ['name', 'price', 'description', 'product_image', 'class_id', 'category']


#address of shipment
class AddressForm(forms.Form):
    Email = forms.EmailField()
    Mobile= forms.IntegerField()
    Address = forms.CharField(max_length=500)



#for updating status of order
class OrderForm(forms.ModelForm):
    class Meta:
        model=models.Orders
        fields=['status']


