from django import forms
from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile


class SignUpForm(UserCreationForm):
    """
    Extended user registration form.
    
    Features:
    - Username validation (unique)
    - Email validation (unique)
    - Password strength requirements
    - Password confirmation
    - First name and last name
    
    Fields:
    - first_name: User's first name
    - last_name: User's last name
    - email: User's email address
    - username: Unique username
    - password1: Password
    - password2: Password confirmation
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style password and username fields
        self.fields['username'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })

    def clean_email(self):
        """
        Validate that email is unique.
        Raises validation error if email already exists.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered!')
        return email

    def clean_username(self):
        """
        Validate that username is unique and not taken.
        """
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken!')
        return username


class LoginForm(AuthenticationForm):
    """
    Custom login form with styled Bootstrap inputs.
    
    Fields:
    - username: User's username
    - password: User's password
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )


class UserProfileForm(forms.ModelForm):
    """
    Form to edit user profile information.
    
    Allows users to update their personal information
    like phone, address, city, and bio.
    """
    class Meta:
        model = UserProfile
        fields = ('phone', 'address', 'city', 'bio')
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your city'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us about yourself',
                'rows': 4
            })
        }


class ExpenseForm(forms.Form):
    """
    Form to add expense amount.
    
    Fields:
    - expense_amount: Amount to deduct as expense
    - description: Description of the expense (optional)
    """
    expense_amount = forms.DecimalField(
        label='Expense Amount',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter expense amount',
            'step': '0.01',
            'min': '0'
        })
    )
    description = forms.CharField(
        label='Description',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Grocery, Transport (optional)'
        })
    )


class AddAmountForm(forms.Form):
    """
    Form to add balance amount.
    
    Fields:
    - add_amount: Amount to add to balance
    """
    add_amount = forms.DecimalField(
        label='Add Amount',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter amount to add',
            'step': '0.01',
            'min': '0'
        })
    )


class TargetAmountForm(forms.Form):
    """
    Form to set target savings amount.
    
    Fields:
    - target_amount: Monthly savings goal amount
    """
    target_amount = forms.DecimalField(
        label='Target Savings Amount',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter target savings amount',
            'step': '0.01',
            'min': '0'
        })
    )
