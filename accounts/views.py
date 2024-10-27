from django.views.generic import TemplateView
from django.urls import reverse

from django.contrib.auth.mixins import LoginRequiredMixin

from allauth.account.views import PasswordChangeView


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    Allauth override to allow redirect following password change.
    """

    def get_success_url(self):
        success_url = reverse('account_change_password_done')
        return success_url


class PasswordChangeDoneView(LoginRequiredMixin, TemplateView):
    """
    Redirects to confirmation page when a user has successfully changed their 
    own password.
    """
    
    template_name = 'account/password_change_done.html'