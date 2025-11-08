# Quick Start Guide - Smart Finance Manager

## 🚀 Get Started in 5 Minutes

### Step 1: Setup Virtual Environment
```bash
cd c:\Users\Saikumar\Desktop\vsc\django\mini
python -m venv env
env\Scripts\activate
```

### Step 2: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Create Admin Account (Optional)
```bash
python manage.py createsuperuser
```

### Step 4: Start Server
```bash
python manage.py runserver
```

### Step 5: Access Application
- **Frontend**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

---

## 📋 User Flow

### New User Registration
1. Navigate to `/signup/`
2. Fill registration form with:
   - First Name
   - Last Name
   - Email (unique)
   - Username (unique)
   - Password (8+ chars, letters & numbers)
3. Click "Create Account"
4. System automatically creates:
   - User account
   - UserProfile
   - UserExpenseAccount (empty)
5. Redirected to login page

### User Login
1. Navigate to `/login/`
2. Enter username and password
3. Click "Login"
4. Redirected to dashboard homepage

### Dashboard Features
- ➕ **Add Amount**: Increase balance
- ➖ **Add Expense**: Decrease balance
- 🎯 **Set Target**: Set monthly savings goal
- 📊 **Analytics Chart**: Visual breakdown of finances
- 📝 **Recent Transactions**: Last 5 transactions
- 💳 **Current Balance**: Your available balance

### Transaction Management
- **View All Transactions**: Click "Transactions" in navbar
- **Delete Transaction**: Click delete button (reverses effect)
- **Filter by Type**: Expense or Addition

---

## 🔐 Authentication

### Default Admin Credentials
When you run `python manage.py createsuperuser`:
- Username: (your choice)
- Password: (your choice)

### Login Credentials (Example User)
After signup:
- Username: `testuser`
- Password: `Test123!`

---

## 📊 Database Tables

### Auto-Created Tables
```
- auth_user (Django's User model)
- home_userprofile (Linked to User)
- home_userexpenseaccount (Linked to User)
- home_transaction (Financial transactions)
```

### Key Relationships
```
User (1) ←→ (1) UserProfile
User (1) ←→ (1) UserExpenseAccount
UserExpenseAccount (1) ←→ (Many) Transaction
```

---

## 🛠️ Common Commands

### Start Development Server
```bash
python manage.py runserver
```

### Create Database
```bash
python manage.py migrate
```

### Create New Migrations
```bash
python manage.py makemigrations
```

### Access Django Shell
```bash
python manage.py shell
```

### View Database in Admin
```bash
python manage.py createsuperuser
# Then visit http://127.0.0.1:8000/admin/
```

### Collect Static Files
```bash
python manage.py collectstatic
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `models.py` | Database models (UserProfile, UserExpenseAccount, Transaction) |
| `views.py` | View logic (signup, login, dashboard, transactions) |
| `forms.py` | Django forms (SignUp, Login, Expense, etc.) |
| `signals.py` | Auto-create UserProfile & UserExpenseAccount |
| `urls.py` | URL routing |
| `templates/home/` | HTML templates |
| `settings.py` | Django configuration |

---

## 🔍 Testing the Application

### Test User Registration
```python
# In Django shell (python manage.py shell)
from django.contrib.auth.models import User

# Create test user
user = User.objects.create_user(
    username='testuser',
    email='test@example.com',
    password='testpass123',
    first_name='Test',
    last_name='User'
)

# Verify account was created
print(user.expense_account)  # Should print the ExpenseAccount
print(user.profile)  # Should print the UserProfile
```

### Test Transactions
```python
# Get user's account
account = user.expense_account

# Add balance
account.current_balance = 1000
account.total_amount = 1000
account.save()

# Record an expense
from home.models import Transaction
expense = Transaction.objects.create(
    user_account=account,
    transaction_type='expense',
    amount=50,
    description='Groceries'
)

# Update balance
account.current_balance -= 50
account.save()

# View all transactions
transactions = account.transactions.all()
print(transactions)
```

---

## 📊 Data Models Summary

### UserProfile
- Stores user's personal info (phone, address, city, bio)
- Linked to User via OneToOne relationship
- Auto-created when user registers

### UserExpenseAccount
- Tracks financial data
- `total_amount`: Sum of all additions
- `current_balance`: total_amount - total_expenses
- `target_amount`: Monthly savings goal
- Auto-created when user registers

### Transaction
- Records every financial activity
- `transaction_type`: 'expense' or 'addition'
- `amount`: Transaction amount
- `description`: Optional note
- `created_at`: Timestamp

---

## 🎯 Next Steps

1. **Customize Colors**: Edit CSS in templates
2. **Add Features**: 
   - Budget categories
   - Recurring transactions
   - Export to CSV
   - Mobile app
3. **Deploy**: 
   - Use Heroku, AWS, or DigitalOcean
   - Setup Gunicorn
   - Configure PostgreSQL
   - Enable HTTPS

---

## 📞 Need Help?

1. Check `README.md` for detailed documentation
2. Review Django docs: https://docs.djangoproject.com/
3. Check Django signals: https://docs.djangoproject.com/en/stable/topics/signals/
4. Check views.py comments for inline documentation

---

**Last Updated**: November 6, 2025
