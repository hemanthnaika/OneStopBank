from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm,DepositForm,TransferForm,BillPaymentForm,CustomerSupportForm,UserProfileUpdateForm
from .models import UserAccount,BillPayment,Transaction
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import uuid
from decimal import Decimal


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)  # Use `username` for email
        if user is not None:
            login(request, user)
            return redirect("home")  # Replace 'home' with your actual home page URL name
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect('login') 



# Function to check the most recent transaction status
def check_recent_transaction_status(user):
    # Fetch the most recent transaction for the user
    recent_transaction = Transaction.objects.filter(user=user).order_by('-created_at').first()
    
    if recent_transaction:
        # Determine if it's a debit or credit
        if recent_transaction.amount < Decimal('0') or recent_transaction.type.lower() == "debit":
            transaction_type = "Debited"
        else:
            transaction_type = "Credited"

        # Return details of the transaction
        return {
            "transaction_type": transaction_type,
            "amount": abs(recent_transaction.amount),  # Return the absolute value for display
            "description": recent_transaction.description,
            "status": recent_transaction.status,
            "created_at": recent_transaction.created_at,
        }
    else:
        # If no transactions are found
        return {
            "transaction_type": "No Transaction",
            "amount": Decimal('0.00'),
            "description": "",
            "status": "",
            "created_at": None,
        }

@login_required
def home(request):
    # Fetch the 5 most recent transactions for the logged-in user
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:5]
    

    # Use the helper function to get details of the most recent transaction
    recent_transaction_details = check_recent_transaction_status(request.user)

    # Pass the calculated values and recent transactions to the template
    context = {
        'recent_transactions': recent_transactions,
        'transaction_type': recent_transaction_details["transaction_type"],
        'recent_transaction': recent_transaction_details,
        'amount': recent_transaction_details["amount"],
    }

    # Render the context to the specified template
    return render(request, 'base.html', context)



def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect('login')  # Redirect to the login page
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

from .models import Transaction

@login_required
def deposit(request):
    user = request.user
    account = UserAccount.objects.get(email=request.user.email) 
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            amount_in_paisa = int(amount * 100)

            # Create Razorpay order
            order = razorpay_client.order.create({
                "amount": amount_in_paisa,
                "currency": "INR",
                "payment_capture": "1"
            })

            # Save transaction
            transaction = Transaction.objects.create(
                user=user,
                razorpay_order_id=order["id"],
                amount=amount,
                status="PENDING",
                type="DEPOSIT",
                description="Deposit via Razorpay"
                
            )

            # Pass order details to the template
            context = {
                "form": form,
                "order_id": order["id"],
                "amount": amount,
                "razorpay_key_id": settings.RAZORPAY_KEY_ID
            }
            return render(request, "pages/deposit.html", context)
    else:
        form = DepositForm()

    return render(request, "pages/deposit.html", {"form": form,'balance': account.balance})


@csrf_exempt
def deposit_callback(request):
    if request.method == "POST":
        razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        payment_data = request.POST

        try:
            # Verify Razorpay signature
            razorpay_client.utility.verify_payment_signature({
                "razorpay_order_id": payment_data["razorpay_order_id"],
                "razorpay_payment_id": payment_data["razorpay_payment_id"],
                "razorpay_signature": payment_data["razorpay_signature"]
            })

            # Fetch transaction
            transaction = Transaction.objects.get(razorpay_order_id=payment_data["razorpay_order_id"])
            if transaction.status != "PENDING":
                messages.error(request, "Transaction already processed.")
                return redirect("home")

            # Update transaction and user balance
            transaction.status = "SUCCESS"
            transaction.razorpay_payment_id = payment_data["razorpay_payment_id"]
            transaction.save()

            user = transaction.user
            user.balance += transaction.amount
            user.save()

            messages.success(request, f"₹{transaction.amount} deposited successfully!")
            return redirect("home")

        except Transaction.DoesNotExist:
            messages.error(request, "Transaction not found.")
            return redirect("deposit")

        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed. Please try again.")
            return redirect("deposit")

    return redirect("home")


@login_required
def transfer(request):
    sender_account = UserAccount.objects.get(email=request.user.email)  # Current user's account

    if request.method == "POST":
        form = TransferForm(request.POST)
        if form.is_valid():
            recipient_account_number = form.cleaned_data['recipient_account_number']
            amount = form.cleaned_data['amount']

            try:
                recipient_account = UserAccount.objects.get(account_number=recipient_account_number)
            except UserAccount.DoesNotExist:
                messages.error(request, "Recipient account not found.")
                return redirect('transfer')

            if sender_account.balance < amount:
                messages.error(request, "Insufficient funds to complete the transfer.")
            elif sender_account == recipient_account:
                messages.error(request, "You cannot transfer funds to your own account.")
            else:
                # Deduct from sender
                sender_account.balance -= amount
                sender_account.save()

                # Add to recipient
                recipient_account.balance += amount
                recipient_account.save()
                
                # Create a transaction record for the sender
                Transaction.objects.create(
                    razorpay_payment_id=uuid.uuid4(),
                    user=sender_account,
                    amount=amount,
                    type="DEBIT",
                    status="SUCCESS",
                    description=f"Transfer to {recipient_account_number}"
                )

                # Create a transaction record for the recipient
                Transaction.objects.create(
                    user=recipient_account,
                    razorpay_payment_id=uuid.uuid4(),
                    amount=amount,
                    type="CREDIT",
                    status="SUCCESS",
                    description=f"Transfer from {sender_account.account_number}"
                )

                messages.success(request, f"Successfully transferred ₹{amount} to account {recipient_account_number}.")
                return redirect('transfer')
    else:
        form = TransferForm()

    return render(request, 'pages/transfer.html', {'form': form, 'balance': sender_account.balance})


@login_required
def bill(request):
    user = request.user

    if request.method == 'POST':
        form = BillPaymentForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            amount = form.cleaned_data['amount']

            # Check if the user has sufficient balance
            if user.balance < amount:
                messages.error(request, "Insufficient balance to make this payment.")
            else:
                # Deduct the amount from the user's balance
                user.balance -= amount
                user.save()

                # Create a bill payment record
                BillPayment.objects.create(
                    user=user,
                    category=category,
                    amount=amount,
                )

                # Create a transaction for the bill payment
                Transaction.objects.create(
                    user=user, 
                    razorpay_payment_id=uuid.uuid4(),  # Optional, as it's not a Razorpay transaction
                    amount=-amount,  # Negative amount for debit
                    status="SUCCESS",
                    description=f"Bill Payment for {category}",
                    type="DEBIT",  # Assuming it's a debit transaction
                )

                messages.success(request, f"Successfully paid ₹{amount} for {category}.")
                return redirect('bill')
    else:
        form = BillPaymentForm()

    return render(request, 'pages/bill.html', {'form': form, 'balance': user.balance})

def customer_support(request):
    if request.method == 'POST':
        form = CustomerSupportForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('thank_you')  # Redirect to a thank you page or similar
    else:
        form = CustomerSupportForm()
    return render(request, 'pages/CustomerSupport.html', {'form': form})

@login_required
def profile(request):
    
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()  # Save the updated profile
            return redirect('account_dashboard')  # Redirect to the account dashboard after saving
    else:
        form = UserProfileUpdateForm(instance=request.user)  # Pre-populate the form with current user data
    return render(request, 'pages/ProfileSettings.html',{'form': form})

def history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'pages/history.html', {'transactions': transactions})

def thank_you(request):
    return render(request, 'pages/thank_you.html')

def account_dashboard(request):
    return render(request, 'pages/account_dashboard.html')