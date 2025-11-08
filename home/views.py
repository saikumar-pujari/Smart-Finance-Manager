from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from decimal import Decimal
import json
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from .models import UserExpenseAccount, Transaction
from .forms import (
    ExpenseForm, AddAmountForm, TargetAmountForm,
    SignUpForm, LoginForm, UserProfileForm
)


# ==================== AI SUGGESTIONS ====================

def generate_ai_suggestions(total_amount, total_expenses, total_additions, target_amount, current_balance):
    """
    Generate smart savings suggestions based on user's financial data.
    Uses rule-based AI logic for recommendations.
    """
    suggestions = []
    
    # Convert all to float for calculations
    total_amount = float(total_amount) if total_amount else 0
    total_expenses = float(total_expenses) if total_expenses else 0
    total_additions = float(total_additions) if total_additions else 0
    target_amount = float(target_amount) if target_amount else 0
    current_balance = float(current_balance) if current_balance else 0
    
    # Calculate percentages
    if total_amount > 0:
        expense_percentage = (total_expenses / total_amount) * 100
        balance_percentage = (current_balance / total_amount) * 100
    else:
        expense_percentage = 0
        balance_percentage = 0
    
    # Suggestion 1: Spending Rate
    if expense_percentage > 70:
        suggestions.append({
            'emoji': '🚨',
            'title': 'High Spending Alert',
            'message': f'You\'re spending {expense_percentage:.1f}% of your total amount! Try to reduce it to below 60%.',
            'type': 'danger'
        })
    elif expense_percentage > 50:
        suggestions.append({
            'emoji': '⚠️',
            'title': 'Moderate Spending',
            'message': f'Your spending is at {expense_percentage:.1f}%. Consider cutting expenses by 10-15%.',
            'type': 'warning'
        })
    else:
        suggestions.append({
            'emoji': '✅',
            'title': 'Good Spending Control',
            'message': f'Great! You\'re only spending {expense_percentage:.1f}% of your amount. Keep it up!',
            'type': 'success'
        })
    
    # Suggestion 2: Target Goal Progress
    if target_amount > 0:
        target_progress = (current_balance / target_amount) * 100
        if target_progress >= 100:
            suggestions.append({
                'emoji': '🎉',
                'title': 'Target Achieved!',
                'message': f'Congratulations! You\'ve reached your savings target of ₹{target_amount:.2f}!',
                'type': 'success'
            })
        elif target_progress >= 75:
            suggestions.append({
                'emoji': '🏃',
                'title': 'Almost There!',
                'message': f'You\'re {target_progress:.1f}% towards your goal! Just ₹{target_amount - current_balance:.2f} more to go.',
                'type': 'info'
            })
        elif target_progress >= 50:
            suggestions.append({
                'emoji': '💪',
                'title': 'Halfway There',
                'message': f'You\'re 50% towards your savings goal. Speed up to reach ₹{target_amount:.2f}!',
                'type': 'info'
            })
        else:
            suggestions.append({
                'emoji': '🎯',
                'title': 'Keep Building',
                'message': f'Save ₹{(target_amount - current_balance):.2f} more to reach your target of ₹{target_amount:.2f}.',
                'type': 'warning'
            })
    
    # Suggestion 3: Daily Average
    if total_expenses > 0:
        avg_daily = total_expenses / 30  # Assuming monthly
        suggestions.append({
            'emoji': '📊',
            'title': 'Daily Average Spending',
            'message': f'Your average daily expense is ₹{avg_daily:.2f}. Try to keep it below ₹{avg_daily * 0.8:.2f}.',
            'type': 'info'
        })
    
    # Suggestion 4: Balance Health
    if current_balance < (total_amount * 0.1):
        suggestions.append({
            'emoji': '⚡',
            'title': 'Low Balance Warning',
            'message': 'Your balance is running low! Consider adding more funds to your account.',
            'type': 'danger'
        })
    elif current_balance > (total_amount * 0.5):
        suggestions.append({
            'emoji': '💰',
            'title': 'Healthy Balance',
            'message': f'Great balance! You have ₹{current_balance:.2f} available for emergencies.',
            'type': 'success'
        })
    
    # Suggestion 5: Income Analysis
    if total_additions > 0 and total_expenses > 0:
        ratio = total_expenses / total_additions
        if ratio < 0.3:
            suggestions.append({
                'emoji': '💵',
                'title': 'Excellent Savings Rate',
                'message': f'You\'re saving {((1-ratio)*100):.1f}% of your income! That\'s excellent.',
                'type': 'success'
            })
        elif ratio < 0.5:
            suggestions.append({
                'emoji': '📈',
                'title': 'Good Savings Habit',
                'message': f'You\'re saving {((1-ratio)*100):.1f}% of your income. This is a healthy rate.',
                'type': 'success'
            })
        else:
            suggestions.append({
                'emoji': '🔍',
                'title': 'Review Your Budget',
                'message': f'You\'re spending {(ratio*100):.1f}% of your income. Try to increase savings.',
                'type': 'warning'
            })
    
    return suggestions


# ==================== AUTHENTICATION VIEWS ====================

def signup(req):
    """User registration view."""
    if req.user.is_authenticated:
        return redirect('homepage')
    
    if req.method == 'POST':
        form = SignUpForm(req.POST)
        if form.is_valid():
            user = form.save()
            messages.success(req, f'Account created! Please login.')
            return redirect('loginpage')
    else:
        form = SignUpForm()
    
    return render(req, 'home/signup.html', {'form': form})


def login_view(req):
    """User login view."""
    if req.user.is_authenticated:
        return redirect('homepage')
    
    if req.method == 'POST':
        form = LoginForm(req, data=req.POST)
        if form.is_valid():
            user = form.get_user()
            login(req, user)
            messages.success(req, f'Welcome back!')
            return redirect('homepage')
        else:
            messages.error(req, 'Invalid credentials!')
    else:
        form = LoginForm()
    
    return render(req, 'home/login.html', {'form': form})


def logout_view(req):
    """User logout view."""
    logout(req)
    messages.success(req, 'Logged out successfully!')
    return redirect('loginpage')


# ==================== DASHBOARD & FINANCE VIEWS ====================

def finance(req):
    """Finance landing page."""
    return render(req, 'home/finance.html')


@login_required(login_url='loginpage')
def home(req):
    """Main dashboard view for expense tracking."""
    account = req.user.expense_account
    
    # Handle expense form submission
    if req.method == 'POST' and 'expense_submit' in req.POST:
        expense_form = ExpenseForm(req.POST)
        if expense_form.is_valid():
            amount = expense_form.cleaned_data['expense_amount']
            description = expense_form.cleaned_data.get('description', '')
            
            if account.current_balance >= amount:
                account.current_balance -= amount
                account.save()
                
                Transaction.objects.create(
                    user_account=account,
                    transaction_type='expense',
                    amount=amount,
                    description=description or 'Expense'
                )
                messages.success(req, f'Expense of ₹{amount} added!')
            else:
                messages.error(req, f'Insufficient balance!')
            
            return redirect('homepage')
    
    # Handle add amount form submission
    if req.method == 'POST' and 'add_submit' in req.POST:
        add_form = AddAmountForm(req.POST)
        if add_form.is_valid():
            amount = add_form.cleaned_data['add_amount']
            
            account.current_balance += amount
            account.total_amount += amount
            account.save()
            
            Transaction.objects.create(
                user_account=account,
                transaction_type='addition',
                amount=amount,
                description='Amount Added'
            )
            messages.success(req, f'₹{amount} added!')
            
            return redirect('homepage')
    
    # Handle target amount form submission
    if req.method == 'POST' and 'target_submit' in req.POST:
        target_form = TargetAmountForm(req.POST)
        if target_form.is_valid():
            target = target_form.cleaned_data['target_amount']
            account.target_amount = target
            account.save()
            messages.success(req, f'Target set to ₹{target}!')
            
            return redirect('homepage')
    
    # Initialize forms
    expense_form = ExpenseForm()
    add_form = AddAmountForm()
    target_form = TargetAmountForm()
    
    # Get last 5 transactions
    last_transactions = account.transactions.all()[:5]
    
    # Calculate analytics
    total_expenses = sum(
        t.amount for t in account.transactions.filter(transaction_type='expense')
    )
    total_additions = account.total_amount
    current_balance = account.current_balance
    target = account.target_amount
    
    # Calculate remaining target
    remaining_target = max(Decimal('0'), target - current_balance) if target > 0 else Decimal('0')
    
    # Prepare chart data
    chart_data = {
        'labels': ['Balance Available', 'Total Expenses', 'Target Savings'],
        'values': [float(current_balance), float(total_expenses), float(target)],
        'colors': ['#27ae60', '#e74c3c', '#3498db']
    }
    
    context = {
        'account': account,
        'expense_form': expense_form,
        'add_form': add_form,
        'target_form': target_form,
        'last_transactions': last_transactions,
        'remaining_target': remaining_target,
        'total_expenses': total_expenses,
        'total_additions': total_additions,
        'chart_data': json.dumps(chart_data),
    }
    
    return render(req, 'home/homepage.html', context)


@login_required(login_url='loginpage')
def transcation(req):
    """View all transactions."""
    account = req.user.expense_account
    
    # Handle transaction deletion
    if req.method == 'POST' and 'delete_transaction' in req.POST:
        transaction_id = req.POST.get('transaction_id')
        try:
            transaction = Transaction.objects.get(id=transaction_id, user_account=account)
            
            # Reverse the transaction
            if transaction.transaction_type == 'expense':
                account.current_balance += transaction.amount
            else:
                account.current_balance -= transaction.amount
                account.total_amount -= transaction.amount
            
            account.save()
            transaction.delete()
            messages.success(req, 'Transaction deleted!')
        except Transaction.DoesNotExist:
            messages.error(req, 'Transaction not found!')
        
        return redirect('transcationpage')
    
    transactions = account.transactions.all()
    
    # Calculate totals
    total_expenses = sum(
        t.amount for t in transactions.filter(transaction_type='expense')
    )
    total_additions = sum(
        t.amount for t in transactions.filter(transaction_type='addition')
    )
    
    context = {
        'account': account,
        'transactions': transactions,
        'total_expenses': total_expenses,
        'total_additions': total_additions,
    }
    
    return render(req, 'home/transcations.html', context)


def pricing(req):
    """Pricing page."""
    return render(req, 'home/pricing.html')


@login_required(login_url='loginpage')
def analytics(req):
    """Analytics page with AI suggestions."""
    account = req.user.expense_account
    
    # Calculate analytics
    total_expenses = sum(
        t.amount for t in account.transactions.filter(transaction_type='expense')
    )
    total_additions = sum(
        t.amount for t in account.transactions.filter(transaction_type='addition')
    )
    
    # Generate AI suggestions
    suggestions = generate_ai_suggestions(
        total_amount=account.total_amount,
        total_expenses=total_expenses,
        total_additions=total_additions,
        target_amount=account.target_amount,
        current_balance=account.current_balance
    )
    
    context = {
        'account': account,
        'total_expenses': total_expenses,
        'total_additions': total_additions,
        'suggestions': suggestions,
    }
    
    return render(req, 'home/analytics.html', context)


@login_required(login_url='loginpage')
def download_transactions_pdf(req):
    """Download transaction history as PDF."""
    account = req.user.expense_account
    transactions = account.transactions.all()
    
    # Calculate totals
    total_expenses = sum(
        t.amount for t in transactions.filter(transaction_type='expense')
    )
    total_additions = sum(
        t.amount for t in transactions.filter(transaction_type='addition')
    )
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=12
    )
    
    # Title
    title = Paragraph("📊 Transaction History Report", title_style)
    elements.append(title)
    
    # User Info
    user_info = f"<b>User:</b> {req.user.first_name} {req.user.last_name} ({req.user.username})<br/>" \
                f"<b>Email:</b> {req.user.email}<br/>" \
                f"<b>Generated:</b> {datetime.now().strftime('%d %B %Y, %H:%M')}"
    elements.append(Paragraph(user_info, styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary Section
    summary_heading = Paragraph("Account Summary", heading_style)
    elements.append(summary_heading)
    
    summary_data = [
        ['Metric', 'Amount'],
        ['Current Balance', f'₹{float(account.current_balance):.2f}'],
        ['Total Income', f'₹{float(total_additions):.2f}'],
        ['Total Expenses', f'₹{float(total_expenses):.2f}'],
        ['Savings Goal', f'₹{float(account.target_amount):.2f}'],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Transactions Section
    if transactions.exists():
        trans_heading = Paragraph("Transaction Details", heading_style)
        elements.append(trans_heading)
        
        # Build transaction table
        trans_data = [
            ['Date', 'Type', 'Amount', 'Description', 'Balance'],
        ]
        
        running_balance = Decimal('0')
        for trans in transactions.order_by('-created_at'):
            date_str = trans.created_at.strftime('%d-%m-%Y')
            trans_type = 'Expense' if trans.transaction_type == 'expense' else 'Income'
            amount_str = f"₹{float(trans.amount):.2f}"
            desc = trans.description or '-'
            
            if trans.transaction_type == 'expense':
                running_balance -= trans.amount
            else:
                running_balance += trans.amount
            
            balance_str = f"₹{float(running_balance):.2f}"
            
            trans_data.append([date_str, trans_type, amount_str, desc, balance_str])
        
        trans_table = Table(trans_data, colWidths=[1.2*inch, 1*inch, 1*inch, 1.5*inch, 1.3*inch])
        trans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(trans_table)
    else:
        elements.append(Paragraph("No transactions found.", styles['Normal']))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_text = "This is an official record of your financial transactions. " \
                  "Keep this document safe for your records."
    elements.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    
    # Return PDF as response
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="transaction_history_{datetime.now().strftime("%d_%m_%Y")}.pdf"'
    
    return response
