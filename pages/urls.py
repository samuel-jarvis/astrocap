from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
  path('', views.index, name='index'),
  path('about', views.about, name='about'),
  path('contact', views.contact, name='contact'),
  path('dashboard', views.dashboard, name='dashboard'),
  path('deposit', views.deposit, name='deposit'),
  path('forgot', views.forgot, name='forgot'),
  path('signin', views.signin, name='signin'),
  path('forgottenPassword', views.forgottenPassword, name='forgottenPassword'),
  path('resetPassword', views.resetPassword, name='resetPassword'),
  path('signup', views.signup, name='signup'),
  path('verification', views.verification, name='verification'),
  path('transactions', views.transactions, name='transactions'),
  path('resendOtp', views.resendOtp, name='resendOtp'),
  path('withdraw', views.withdraw, name='withdraw'),
  path('profile', views.profile, name='profile'),
  path('logout', views.logout, name='logout'),
]
