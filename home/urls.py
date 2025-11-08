from django.urls import path, include
from home.views import *

urlpatterns = [
    # Authentication URLs
    path('signup/', signup, name='signuppage'),
    path('', login_view, name='loginpage'),
    path('logout/', logout_view, name='logoutpage'),
    
    # Main application URLs
    # path('', finance, name='financepage'),
    path('home/', home, name='homepage'),
    path('transcations/', transcation, name='transcationpage'),
    path('transcations/download-pdf/', download_transactions_pdf, name='download_pdf'),
    path('pricing/', pricing, name='pricingpage'),
    path('analytics/', analytics, name='analyticspage'),
]
