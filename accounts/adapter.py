from django.core.exceptions import PermissionDenied

from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):

    def is_open_for_signup(self, request):
        """
        Prevents signup by raising a 403 error.
        """
    
        raise PermissionDenied