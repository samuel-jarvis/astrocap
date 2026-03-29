from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
# from django.core.mail import send_mail
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import get_template
# from django.template import Context
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail


from .models import Contact, Bitcoin, Paypal, Bank, Verification, Transaction


# Create your views here.
def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def resendOtp(request):
    if request.user.is_authenticated:
        user = request.user
        verification, _ = Verification.objects.get_or_create(
            user=user,
            defaults={'email': user.username, 'otp': 0, 'verified': True}
        )
        verification.verified = True
        verification.otp = 0
        verification.save()
        messages.success(request, 'Email verification bypassed')
        return redirect('dashboard')
    else:
        return redirect('signin')


def verification(request):
    # check otp
    if request.method == 'POST':
        otp = request.POST['otp']
        user = request.user
        verification = Verification.objects.get(user=request.user)

        print(otp)
        print(verification.otp)

        if otp == str(verification.otp):
            print('otp verified')
            verification.verified = True
            verification.save()
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
            messages.success(request, 'Email service unavailable. Proceed to reset your password.')
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
                messages.error(request, 'Start the reset process with your email')
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


def transactions(request):
    invests = Transaction.objects.filter(user=request.user)
    context = {
        'invests': invests
    }
    print(invests)
    return render(request, 'transactions.html', context)


def dashboard(request):
    if request.user.is_authenticated:
        return render(request, 'dashboard.html')
    else:
        return redirect('signin')


def profile(request):
    if request.user.is_authenticated:
        return render(request, 'profile.html')
    else:
        return redirect('signin')


def deposit(request):
    if request.user.is_authenticated:
        return render(request, 'deposit.html')
    else:
        return redirect('signin')


def forgot(request):
    return render(request, 'forgot.html')


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

        user = auth.authenticate(username=username, password=password)
        auth.login(request, user)

        verification = Verification.objects.create(
            user=user,
            otp=0,
            verified=True,
            email=username
        )

        return redirect('dashboard')

    except Exception as e:
        print(f'Signup error: {str(e)}')
        messages.error(
            request, 'An error occurred during signup. Please try again.')
        return redirect('signup')


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('signin')


def withdraw(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'withdraw.html')

        if request.method == 'POST' and 'bitcoin' in request.POST:
            amount = request.POST['amount']
            wallet = request.POST['wallet']
            username = request.POST['username']

            withdraw = Bitcoin(amount=float(amount),
                               wallet=wallet, username=username)

            withdraw.save()

            messages.success(request, 'Withdrawal Processing')
            return render(request, 'withdraw.html')

        if request.method == 'POST' and 'paypal' in request.POST:
            amount = request.POST['amount']
            email = request.POST['email']
            username = request.POST['username']

            withdraw = Paypal(amount=float(amount),
                              email=email, username=username)

            withdraw.save()

            messages.success(request, 'Withdrawal Processing')
            return render(request, 'withdraw.html')

        if request.method == 'POST' and 'bank' in request.POST:
            amount = float(request.POST['amount'])
            account_name = request.POST['accountname']
            bank_name = request.POST['bankname']
            account_number = request.POST['accountnumber']
            username = request.POST['username']

            withdraw = Bank(amount=amount, account_name=account_name,
                            bank_name=bank_name, account_number=account_number, username=username)

            withdraw.save()

            messages.success(request, 'Withdrawal Processing')
            return render(request, 'withdraw.html')

    else:
        return redirect('signin')
