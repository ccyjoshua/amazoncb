"""
Base view classes for all registration workflows.

"""

from django.conf import settings
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth import authenticate, get_user_model, login, models, views
from django.urls import reverse

from myauth import signals
from myauth.forms import RegistrationForm


class BaseRegistrationView(FormView):
    """
    Base class for user registration views.

    """
    disallowed_url = 'registration_disallowed'
    form_class = RegistrationForm
    success_url = None
    template_name = 'myauth/signup.html'

    def dispatch(self, *args, **kwargs):
        """
        Check that user signup is allowed before even bothering to
        dispatch or do other processing.

        """
        if not self.registration_allowed():
            return redirect(self.disallowed_url)
        return super(BaseRegistrationView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        new_user = self.register(form)
        success_url = self.get_success_url(new_user) if \
            (hasattr(self, 'get_success_url') and
             callable(self.get_success_url)) else \
            self.success_url

        # success_url may be a string, or a tuple providing the full
        # argument set for redirect(). Attempting to unpack it tells
        # us which one it is.
        try:
            to, args, kwargs = success_url
            return redirect(to, *args, **kwargs)
        except ValueError:
            return redirect(success_url)

    def registration_allowed(self):
        """
        Override this to enable/disable user registration, either
        globally or on a per-request basis.

        """
        return getattr(settings, 'REGISTRATION_OPEN', True)

    def register(self, form):
        """
        Implement user-registration logic here. Access to both the
        request and the registration form is available here.

        """
        raise NotImplementedError


class ActivationView(TemplateView):
    """
    Base class for user activation views.

    """
    success_url = None
    template_name = 'registration/activate.html'

    def get(self, *args, **kwargs):
        """
        The base activation logic; subclasses should leave this method
        alone and implement activate(), which is called from this
        method.

        """
        activated_user = self.activate(*args, **kwargs)
        if activated_user:
            signals.user_activated.send(
                sender=self.__class__,
                user=activated_user,
                request=self.request
            )
            success_url = self.get_success_url(activated_user) if \
                (hasattr(self, 'get_success_url') and
                 callable(self.success_url)) else \
                self.success_url
            try:
                to, args, kwargs = success_url
                return redirect(to, *args, **kwargs)
            except ValueError:
                return redirect(success_url)
        return super(ActivationView, self).get(*args, **kwargs)

    def activate(self, *args, **kwargs):
        """
        Implement account-activation logic here.

        """
        raise NotImplementedError


User = get_user_model()


class RegistrationView(BaseRegistrationView):
    """
    Registration via the simplest possible process: a user supplies a
    username, email address and password (the bare minimum for a
    useful account), and is immediately signed up and logged in.

    """
    def register(self, form):
        new_user = form.save()
        new_user = authenticate(
            username=getattr(new_user, User.USERNAME_FIELD),
            password=form.cleaned_data['password1']
        )
        login(self.request, new_user)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=self.request)
        return new_user

    def get_success_url(self, user):
        return '/'


class BuyerRegistrationView(RegistrationView):
    template_name = 'myauth/signup_buyer.html'

    def register(self, form):
        new_user = super(BuyerRegistrationView, self).register(form)
        buyer_group = models.Group.objects.get(name='buyer_group')
        new_user.groups.add(buyer_group)
        return new_user

    def get_success_url(self, user):
        return reverse('buyer_product_list')


class SellerRegistrationView(RegistrationView):
    template_name = 'myauth/signup_seller.html'

    def register(self, form):
        new_user = super(SellerRegistrationView, self).register(form)
        seller_group = models.Group.objects.get(name='seller_group')
        new_user.groups.add(seller_group)
        return new_user

    def get_success_url(self, user):
        return reverse('seller_product_list')


class SignInView(views.LoginView):
    template_name = 'myauth/signin.html'

    def get_success_url(self):
        if self.request.user.groups.filter(name='seller_group').exists():
            return reverse('seller_product_list')
        elif self.request.user.groups.filter(name='buyer_group').exists():
            return reverse('buyer_product_list')
        else:
            return '/'


class SignOutView(views.LogoutView):
    # template_name = 'myauth/signin.html'
    next_page = '/'
