from django.db import models
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth.models import User

# User Profile Model - extends Django's built-in User model
class UserProfile(models.Model):
    """
    Extended user profile to store additional user information.
    Links to Django's built-in User model via OneToOneField.
    
    Fields:
    - user: OneToOneField to Django User model
    - phone: User's contact number
    - address: User's residential address
    - city: User's city
    - profile_picture: User's profile photo
    - bio: Short bio/description
    - created_at: Account creation timestamp
    - updated_at: Last profile update timestamp
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Profile"

    class Meta:
        db_table = 'user_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


# User Expense Account Model
class UserExpenseAccount(models.Model):
    """
    Track user's financial data including balance, expenses, and savings target.
    Links to Django User model to associate expense accounts with registered users.
    
    Fields:
    - user: ForeignKey to Django User model
    - total_amount: Total amount added to account
    - current_balance: Current available balance (total - expenses)
    - target_amount: User's savings goal for the month
    - created_at: Account creation date
    - updated_at: Last update date
    
    Methods:
    - __str__: Returns user info with current balance
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='expense_account')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    target_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Balance: {self.current_balance}"

    class Meta:
        db_table = 'user_expense_account'
        verbose_name = 'User Expense Account'
        verbose_name_plural = 'User Expense Accounts'


class Transaction(models.Model):
    """
    Track all financial transactions (expenses and additions) for each user.
    
    Transaction Types:
    - 'expense': Money spent/deducted
    - 'addition': Money added/income
    
    Fields:
    - user_account: ForeignKey to UserExpenseAccount
    - transaction_type: Type of transaction (expense or addition)
    - amount: Transaction amount
    - description: Description of the transaction
    - created_at: Transaction timestamp
    
    Ordering:
    - Ordered by created_at in descending order (newest first)
    """
    TRANSACTION_TYPE = [
        ('expense', 'Expense'),
        ('addition', 'Addition'),
    ]
    
    user_account = models.ForeignKey(UserExpenseAccount, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user_account.user.username} - {self.transaction_type}: {self.amount}"

    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
