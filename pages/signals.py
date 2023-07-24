# a signal receiver function that creates an otp object when a user is created

def create_otp(sender, instance, created, **kwargs):
    if created:
        # generate otp
        Otp.objects.create(user=instance, otp=0)

