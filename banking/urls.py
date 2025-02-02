
from django.urls import path,include
from . import views
from .views import register_view,deposit_callback
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('',views.home,name='home'),
    path('deposit/',views.deposit,name='deposit'),
    path('deposit/callback/', deposit_callback, name='deposit_callback'),
    path('transfer/',views.transfer,name='transfer'),
    path('bill/',views.bill,name='bill'),
    path('customerSupport/',views.customer_support,name='customer_support'),
    path('profile/',views.profile,name='profile',),
    path('history/',views.history,name='history'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('account-dashboard/', views.account_dashboard, name='account_dashboard'),
]# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)