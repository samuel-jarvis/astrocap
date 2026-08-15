from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods


from .models import (
    Balance,
    Bank,
    Bitcoin,
    Contact,
    Paypal,
    Transaction,
    Verification,
)


# Create your views here.
def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def _get_or_create_balance(user):
    """Return a balance for both new accounts and legacy users."""
    balance, _ = Balance.objects.get_or_create(
        user=user,
        defaults={'username': user.username},
    )
    return balance


def _parse_withdrawal_amount(raw_amount):
    """Validate the integer amount supported by the existing database model."""
    try:
        amount = Decimal(raw_amount)
    except (InvalidOperation, TypeError):
        return None

    if (
        not amount.is_finite()
        or amount != amount.to_integral_value()
        or amount < 50
        or amount > 9223372036854775807
    ):
        return None

    return int(amount)


@login_required(login_url='signin')
def resendOtp(request):
    user = request.user
    verification, _ = Verification.objects.get_or_create(
        user=user,
        defaults={'email': user.username, 'otp': 0, 'verified': True}
    )
    verification.verified = True
    verification.otp = 0
    verification.save(update_fields=['verified', 'otp'])
    messages.success(request, 'Email verification bypassed')
    return redirect('dashboard')


@login_required(login_url='signin')
def verification(request):
    # check otp
    if request.method == 'POST':
        otp = request.POST.get('otp', '').strip()
        verification, _ = Verification.objects.get_or_create(
            user=request.user,
            defaults={'email': request.user.username, 'otp': 0},
        )

        if otp == str(verification.otp):
            verification.verified = True
            verification.save(update_fields=['verified'])
            return redirect('dashboard')

        else:
            messages.error(request, 'Invalid OTP')
            return redirect('verification')

    return render(request, 'verification.html')


def forgottenPassword(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(username=email).exists():
            request.session['reset_email'] = email
            messages.success(
                request, 'Email service unavailable. Proceed to reset your password.')
            return redirect('resetPassword')
        else:
            messages.error(request, 'Email does not exist')
            return redirect('forgottenPassword')
    else:
        return render(request, 'forgottenPassword.html')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            email = request.session.get('reset_email')
            if not email:
                messages.error(
                    request, 'Start the reset process with your email')
                return redirect('forgottenPassword')
            try:
                user = User.objects.get(username=email)
                user.set_password(password)
                user.save()
                request.session.pop('reset_email', None)
                messages.success(request, 'Password Reset Successful')
                return redirect('signin')
            except User.DoesNotExist:
                messages.error(request, 'Account not found for reset')
                return redirect('forgottenPassword')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('resetPassword')

    return render(request, 'resetPassword.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        country = request.POST['country']
        phone = request.POST['phone']
        message = request.POST['message']

        contact = Contact(name=name, email=email,
                          country=country, message=message, phone=phone)

        contact.save()
        # return redirect('contacts')

    return render(request, 'contact.html')


@login_required(login_url='signin')
def transactions(request):
    invests = Transaction.objects.filter(user=request.user).order_by('-date')
    context = {
        'invests': invests
    }
    return render(request, 'dashboard/transactions.html', context)


@login_required(login_url='signin')
def dashboard(request):
    return render(
        request,
        'dashboard/overview.html',
        {'balance': _get_or_create_balance(request.user)},
    )


@login_required(login_url='signin')
def profile(request):
    return render(
        request,
        'dashboard/profile.html',
        {'balance': _get_or_create_balance(request.user)},
    )


@login_required(login_url='signin')
def deposit(request):
    return render(request, 'dashboard/deposit.html')


@login_required(login_url='signin')
def support(request):
    if request.method == 'POST':
        topic = request.POST.get('topic', 'General').strip()
        message = request.POST.get('message', '').strip()
        phone = request.POST.get('phone', '').strip()
        country = request.POST.get('country', '').strip()

        allowed_topics = {'Account', 'Deposit', 'Withdrawal', 'Technical', 'General'}
        if topic not in allowed_topics:
            topic = 'General'

        if not message:
            messages.error(request, 'Tell us how we can help.')
            return redirect('support')

        if len(message) > 85:
            messages.error(request, 'Keep your message to 85 characters or fewer.')
            return redirect('support')

        Contact.objects.create(
            name=(request.user.get_full_name() or request.user.username)[:100],
            email=request.user.username[:100],
            country=country[:100],
            phone=phone[:100],
            message=f'[{topic}] {message}',
        )
        messages.success(request, 'Your support request has been sent to the admin team.')
        return redirect('support')

    return render(request, 'dashboard/support.html')


def forgot(request):
    return redirect('forgottenPassword')


def signin(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method != 'POST':
        return render(request, 'signin.html')

    username = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')

    if not username or not password:
        messages.error(request, 'Please provide both email and password')
        return redirect('signin')

    user = auth.authenticate(username=username, password=password)

    if user is None:
        messages.error(request, 'Invalid credentials')
        return redirect('signin')

    auth.login(request, user)

    if not Verification.objects.filter(user=user).exists():
        Verification.objects.create(
            user=user,
            otp=0,
            verified=True,
            email=username
        )

    return redirect('dashboard')


def signup(request):
    if request.method != 'POST':
        return render(request, 'signup.html')

    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    username = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')
    password2 = request.POST.get('password2', '')

    if password != password2:
        messages.error(request, "Passwords do not match")
        return redirect('signup')

    if User.objects.filter(username=username).exists():
        messages.error(
            request, 'It seems you are already registered, please sign in')
        return redirect('signup')

    try:
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        verification = Verification.objects.create(
            user=user,
            otp=0,
            verified=True,
            email=username
        )

        Balance.objects.get_or_create(
            user=user,
            defaults={'username': username},
        )

        messages.success(
            request, 'Account created successfully. Please sign in.')
        return redirect('signin')

    except Exception as e:
        print(f'Signup error: {str(e)}')
        messages.error(
            request, 'An error occurred during signup. Please try again.')
        return redirect('signup')


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('signin')

    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('signin')


@login_required(login_url='signin')
@require_http_methods(['GET', 'POST'])
def withdraw(request):
    if request.method == 'GET':
        return render(request, 'dashboard/withdraw.html')

    amount = _parse_withdrawal_amount(request.POST.get('amount'))
    if amount is None:
        messages.error(request, 'Enter a whole-dollar amount of at least $50.')
        return redirect('withdraw')

    username = request.user.username

    if 'bitcoin' in request.POST:
        wallet = request.POST.get('wallet', '').strip()
        if not wallet:
            messages.error(request, 'Enter a wallet address.')
            return redirect('withdraw')
        Bitcoin.objects.create(amount=amount, wallet=wallet, username=username)

    elif 'paypal' in request.POST:
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, 'Enter the PayPal email address.')
            return redirect('withdraw')
        Paypal.objects.create(amount=amount, email=email, username=username)

    elif 'bank' in request.POST:
        account_name = request.POST.get('accountname', '').strip()
        bank_name = request.POST.get('bankname', '').strip()
        account_number = request.POST.get('accountnumber', '').strip()

        if not all((account_name, bank_name, account_number)) or not account_number.isdigit():
            messages.error(request, 'Enter valid bank account details.')
            return redirect('withdraw')

        Bank.objects.create(
            amount=amount,
            account_name=account_name,
            bank_name=bank_name,
            account_number=account_number,
            username=username,
        )

    else:
        messages.error(request, 'Choose a withdrawal method.')
        return redirect('withdraw')

    messages.success(request, 'Your withdrawal request is being processed.')
    return redirect('withdraw')
