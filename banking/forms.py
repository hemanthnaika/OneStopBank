from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserAccount
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserAccount, BillPayment,CustomerSupport
from django.utils.safestring import mark_safe

class RegistrationForm(UserCreationForm):
    # Override password fields to apply custom styles
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm',
            'placeholder': 'Create a password',
        }),
        label=mark_safe("Password <span style='color: red;'>*</span>")
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm',
            'placeholder': 'Confirm your password',
        }),
        label=mark_safe("Confirm Password <span style='color: red;'>*</span>")
    )

    class Meta:
        model = UserAccount
        fields = [
            'first_name',
            'last_name',
            'email', 
            'account_number', 
            'account_type', 
            'phone_number', 
            'address', 
            'date_of_birth', 
            'password1', 
            'password2',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm',
                'placeholder': 'Enter your First Name ',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm',
                'placeholder': 'Enter your Last Name (optional)',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm',
                'placeholder': 'Enter your email',
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm',
                'placeholder': 'Enter your account number',
            }),
            'account_type': forms.Select(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm',
                'placeholder': 'Enter your phone number',
                'pattern': r'^\+?[1-9]\d{1,14}$',  # Ensures the input matches E.164 format
                'title': "Phone number must be in the format: '+999999999'. Up to 15 digits allowed.",
             }),
            'address': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm',
                'rows': 3,
                'placeholder': 'Enter your address',
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm',
                'type': 'date',
            }),
        }
        labels = {
            'first_name': mark_safe("First Name <span style='color: red;'>*</span>"),
            'email': mark_safe("Email <span style='color: red;'>*</span>"),
            'account_number': mark_safe("Account Number <span style='color: red;'>*</span>"),
            'account_type': mark_safe("Account Type <span style='color: red;'>*</span>"),
            'phone_number': mark_safe("Phone Number <span style='color: red;'>*</span>"),
            'date_of_birth': mark_safe("Date of Birth <span style='color: red;'>*</span>"),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UserAccount.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if UserAccount.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("An account with this phone number already exists.")
        return phone_number




class DepositForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm',
            'placeholder': 'Enter amount to deposit',
        }),
    )

    


class TransferForm(forms.Form):
    recipient_account_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm mt-2 ',
            'placeholder': 'Recipient Account Number'
        }),
        label="Recipient Account Number"
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm mt-2',
            'placeholder': 'Enter transfer amount'
        }),
        label="Amount to Transfer"
    )


class BillPaymentForm(forms.ModelForm):
    details = forms.CharField(
        required=False,
        label="",  # Label will be added dynamically via the template.
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm',
            'placeholder': 'Enter details (e.g., Bill Number)',
        })
    )

    class Meta:
        model = BillPayment
        fields = ['category', 'details', 'amount']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm',
                'placeholder': 'Enter Amount',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        details = cleaned_data.get('details')

        # Validation for 'details' field based on category
        if category == 'ELECTRICITY' and not details:
            raise forms.ValidationError({'details': 'Electricity requires a bill number.'})
        elif category == 'WATER' and not details:
            raise forms.ValidationError({'details': 'Water requires a connection number.'})
        elif category == 'PHONE' and not details:
            raise forms.ValidationError({'details': 'Phone requires a phone number.'})
        elif category == 'GAS' and not details:
            raise forms.ValidationError({'details': 'Gas requires a customer ID.'})
        return cleaned_data
    
class CustomerSupportForm(forms.ModelForm):
    class Meta:
        model = CustomerSupport
        fields = ['full_name', 'email', 'subject', 'message', 'agree_terms']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'w-full p-3 mt-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-3 mt-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'subject': forms.TextInput(attrs={'class': 'w-full p-3 mt-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'message': forms.Textarea(attrs={'class': 'w-full p-3 mt-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 4}),
            'agree_terms': forms.CheckboxInput(attrs={'class': 'h-5 w-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500'}),
        }
        
        


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserAccount
        fields = ['first_name', 'last_name', 'phone_number', 'address', 'date_of_birth', 'user_profile']
        
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full p-3 mt-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full p-3 mt-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter your last name'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full p-3 mt-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter your phone number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full p-3 mt-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter your address',
                'rows': 3
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'w-full p-3 mt-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'user_profile': forms.FileInput(attrs={
                'class': 'w-full p-3 mt-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 col-span-2',
                'onchange': 'previewImage(event)'  # JavaScript function for preview
            }),
        }

