from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.views import generic
from django.http import HttpResponse

from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import RegisterForm, LoginForm
from .tokens import account_activation_token

from django.template.loader import render_to_string
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout as user_logout
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.mail import EmailMessage

def signup(request):

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your WSM account.'
            message = render_to_string('registration/confirmation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            form.add_error(field=None, error='Please confirm your email address to complete the registration')
    else:
        if request.user.is_authenticated:
            return redirect(reverse('home'))
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')

def logout(request):
    user_logout(request)
    return redirect(reverse("home"))

#def password_change(request):
#    pass

#def password_reset(request):
#    pass

class UpdatedLoginView(LoginView):
    template_name = "registration/login.html"
    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse("home"))
        return super(UpdatedLoginView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        remember_me = form.cleaned_data['remember_me']
        if not remember_me:
            self.request.session.set_expiry(0) # 2 weeks by default with remember_me
            self.request.session.modified = True
        return super(UpdatedLoginView, self).form_valid(form)