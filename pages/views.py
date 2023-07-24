from random import randint
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
    otp = randint(100000, 999999)
    print(otp)
    return render(request, 'index.html')


def about(request):
    user = request.user
    # get user email
    print(user.first_name)
    return render(request, 'about.html')

def resendOtp(request):
    if request.user.is_authenticated:
        # set the user verification.otp to the new otp
        user = request.user
        
        verification = Verification.objects.get(user=user)

        # generate 6 digit otp
        otp = randint(100000, 999999)

        verification.otp = otp
        verification.save()

        subject = "Your Astrocapital OTP"
        body = f'Hello {user.first_name}. \n Your OTP is {otp}'
        from_email = settings.EMAIL_HOST_USER

        message = EmailMessage(subject, body, from_email, [user.username])
        message.send()

        messages.success(request, 'Check your email for OTP')
        return redirect('verification')
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

        # check if email exists
        if User.objects.filter(username=email).exists():
            # generate 6 digit otp
            otp = randint(100000, 999999)
            print(otp)

            # create otp object with user id, otp and verified status
            verification = Verification.objects.get(email=email)
            verification.otp = otp
            verification.save()

            subject = "Astrocapital Password Reset"
            body = f'Hello {email}. \n \n Your OTP is {otp}'
            from_email = settings.EMAIL_HOST_USER
            to = [email]

            message = EmailMessage(subject, body, from_email, to)
            message.send()

            messages.success(request, 'Check your email for OTP')
            return redirect('resetPassword')
        else:
            messages.error(request, 'Email does not exist')
            return redirect('forgottenPassword')
    else:
        return render(request, 'forgottenPassword.html')
    
def resetPassword(request):
    if request.method == 'POST':
        otp = request.POST['otp']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            verification = Verification.objects.get(otp=otp)

            if otp == str(verification.otp):
                user = User.objects.get(username=verification.email)
                user.set_password(password)
                user.save()

                messages.success(request, 'Password Reset Successful')
                return redirect('signin')
            else:
                messages.error(request, 'Invalid OTP')
                return redirect('resetPassword')
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
        return redirect('login')
    

def profile(request):
    if request.user.is_authenticated:
        return render(request, 'profile.html')
    else:
        return redirect('login')


def deposit(request):
    if request.user.is_authenticated:
        return render(request, 'deposit.html')
    else:
        return redirect('login')


def forgot(request):
    return render(request, 'forgot.html')


def signin(request):
    if request.user.is_authenticated:
        verification = Verification.objects.get(user=request.user)

        if verification.verified == False:
            return redirect('verification')
        
        return render(request, 'dashboard.html')
    else:
        if request.method == 'POST':
            username = request.POST['email']
            password = request.POST['password']

            user = auth.authenticate(username=username, password=password)

            # create otp object if user dont' have for existing users
            if Verification.objects.filter(user=user).exists():
                print('user exists')

            else:
                verification = Verification(user=user, otp=000000, verified=True, email=username)
                verification.save()

            if user is not None:
                auth.login(request, user)
                # messages.success(request, 'You are now logged in')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid Credentials')
                return redirect('signin')
        else:
            return render(request, 'signin.html')


def signup(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            # Check email
            if User.objects.filter(username=username).exists():
                messages.error(
                    request, 'It seems you are already registered signin')
                return redirect('signup')
            else:
                user = User.objects.create_user(
                    username=username, password=password, first_name=first_name, last_name=last_name)
                user.save()

                user = auth.authenticate(username=username, password=password)
                auth.login(request, user)

                # generate 6 digit otp
                otp = randint(100000, 999999)
                print(otp)

                # create otp object with user id, otp and verified status
                verification = Verification(user=user, otp=otp, verified=False, email=username)
                verification.save()

                subject = "Welcome to AstroCapital Investment"
                body = f'Hello {username}. \n \n Thank you for signing up to our platform \n \n Your OTP is {otp}'
                from_email = settings.EMAIL_HOST_USER
                to = [username]

                # html_message = render_to_string('email.html', {'first_name': first_name, 'last_name': last_name})
                message = EmailMessage(subject, body, from_email, to)
                # message.content_subtype = 'html'
                message.send()

                # messages.success(
                #     request, 'Verify your email to continue')
                return redirect('verification')
        else:
            messages.error(request, "Passwords do not Match")
            return redirect('signup')
    else:
        return render(request, 'signup.html')


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

            withdraw = Bitcoin(amount=amount, wallet=wallet, username=username)

            withdraw.save()

            messages.success(request, 'Withdrawal Processing')
            return render(request, 'withdraw.html')

        if request.method == 'POST' and 'paypal' in request.POST:
            amount = request.POST['amount']
            email = request.POST['email']
            username = request.POST['username']

            withdraw = Paypal(amount=amount, email=email, username=username)

            withdraw.save()

            messages.success(request, 'Withdrawal Processing')
            return render(request, 'withdraw.html')

        if request.method == 'POST' and 'bank' in request.POST:
            amount = request.POST['amount']
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
        return redirect('login')
