from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import re

class RegistrationForm(forms.Form):
    uname = forms.CharField(
        max_length=30, 
        required=True, 
        label="Username", 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    pwd = forms.CharField(
        max_length=50, 
        required=True, 
        label="Password", 
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    cpwd = forms.CharField(
        max_length=50, 
        required=True, 
        label="Confirm Password", 
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    fname = forms.CharField(
        max_length=50, 
        required=True, 
        label="First Name", 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    lname = forms.CharField(
        max_length=50, 
        required=True, 
        label="Last Name", 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    email = forms.EmailField(
        required=True, 
        label="Email", 
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    contact = forms.CharField(
        max_length=10, 
        required=True, 
        label="Contact", 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    address = forms.CharField(
        max_length=100, 
        required=True, 
        label="Address", 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    image = forms.ImageField(required=True)
    user_type = forms.ChoiceField(
        choices=[('service_man', 'Service Man'), ('customer', 'Customer')],
        required=True,
        widget=forms.RadioSelect,
    )
    latitude = forms.FloatField(widget=forms.HiddenInput())
    longitude = forms.FloatField(widget=forms.HiddenInput())

    # Custom Validation for Username
    def clean_uname(self):
        uname = self.cleaned_data.get('uname')
        if User.objects.filter(username=uname).exists():
            raise ValidationError('Username already exists!')
        if not re.match('^[a-zA-Z0-9]+$', uname):
            raise ValidationError('Username can only contain alphanumeric characters.')
        return uname

    # Custom Validation for Email
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email already exists!')
        return email

    # Custom Validation for Passwords
    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get("pwd")
        cpwd = cleaned_data.get("cpwd")

        if pwd and cpwd and pwd != cpwd:
            raise ValidationError("Passwords do not match!")

        # Check for password complexity
        if pwd and not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$%^&+=]).{8,}$', pwd):
            raise ValidationError("Password must be at least 8 characters long and contain an uppercase letter, a lowercase letter, a number, and a special character.")

        return cleaned_data

    # Custom Validation for Contact Number (10-digit)
    def clean_contact(self):
        contact = self.cleaned_data.get('contact')
        if not re.match(r'^\d{10}$', contact):
            raise ValidationError('Contact number must be exactly 10 digits.')
        return contact

    # Ensure latitude and longitude are present
    def clean_latitude(self):
        latitude = self.cleaned_data.get('latitude')
        if latitude is None:
            raise ValidationError('Latitude is required!')
        return latitude

    def clean_longitude(self):
        longitude = self.cleaned_data.get('longitude')
        if longitude is None:
            raise ValidationError('Longitude is required!')
        return longitude
