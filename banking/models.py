from django.utils.crypto import get_random_string
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class UserAccount(AbstractUser):
    ACCOUNT_TYPES = [
        ('SAVINGS', 'Savings Account'),
        ('CURRENT', 'Current Account'),
        ('FIXED', 'Fixed Deposit'),
    ]

    email = models.EmailField(unique=True)  # Use email as the username field
    account_number = models.CharField(max_length=12, unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='SAVINGS')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    phone_number = models.CharField(
        max_length=15, 
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\+?[1-9]\d{1,14}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    account_created_at = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    user_profile=models.ImageField(upload_to='profile_pics/', null=True)

    username = None  # Remove the username field
    USERNAME_FIELD = 'email'  # Set email as the unique identifier
    REQUIRED_FIELDS = ['account_number', 'phone_number']

    objects = UserAccountManager()

    def __str__(self):
        return f"{self.email} - {self.account_number}"



class BillPayment(models.Model):
    BILL_CATEGORIES = [
        ('ELECTRICITY', 'Electricity'),
        ('WATER', 'Water'),
        ('INTERNET', 'Internet'),
        ('PHONE', 'Phone'),
        ('GAS', 'Gas'),
    ]

    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='bill_payments')
    category = models.CharField(max_length=50, choices=BILL_CATEGORIES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=20, unique=True)

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = get_random_string(20).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.category} - ₹{self.amount}"
    
    


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('CREDIT', 'Credit'),
        ('DEBIT', 'Debit'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=255)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="PENDING")  # PENDING, SUCCESS, FAILED
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)  # CREDIT or DEBIT

    def __str__(self):
        return f"{self.user.email} - {self.type} - ₹{self.amount} ({self.status})"
    

class CustomerSupport(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    agree_terms = models.BooleanField()

    def __str__(self):
        return f"Inquiry from {self.full_name} - {self.subject}"
    
