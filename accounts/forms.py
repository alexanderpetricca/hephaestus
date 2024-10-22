from django.contrib.auth import forms as auth_forms

from allauth.account.forms import (
    LoginForm, 
    ChangePasswordForm, 
    ResetPasswordForm, 
    ResetPasswordKeyForm,
)

from .models import CustomUser


# Admin Forms ----------

class CustomUserAdminCreateForm(auth_forms.UserCreationForm):
    """Form used to create a user in the admin backend"""

    class Meta:
        model = CustomUser
        fields = ('__all__')


class CustomUserAdminChangeForm(auth_forms.UserChangeForm):
    """Form used to update a user in the admin backend"""

    class Meta:
        model = CustomUser
        fields = ('__all__')


# Allauth / Accounts Forms ----------

class CustomLoginForm(LoginForm):
    """
    Override settings on AllAuth login form.
    """

    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        
        self.fields['login'].label = ""
        self.fields['login'].widget.attrs.update({
            'placeholder': 'Email Address',
            'class': 'form-control',
        })
        
        self.fields['password'].label = ""
        self.fields['password'].help_text = ""
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Password',
            'class': 'form-control',
        })


class CustomPasswordChangeForm(ChangePasswordForm):
    """
    Override settings on AllAuth change password form.
    """
    
    def __init__(self, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)

        self.fields['oldpassword'].label = ""
        self.fields['oldpassword'].widget.attrs.update({
            'placeholder': 'Current Password',
            'class': 'form-control',
        })
        
        self.fields['password1'].label = ""
        self.fields['password1'].help_text = ""
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'New Password',
            'class': 'form-control',
        })
        
        self.fields['password2'].label = ""
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm New Password',
            'class': 'form-control',
        })


class CustomPasswordResetForm(ResetPasswordForm):
    """
    Override settings on AllAuth reset password form.
    """    
    
    def __init__(self, *args, **kwargs):
        super(CustomPasswordResetForm, self).__init__(*args, **kwargs)

        self.fields['email'].label = ""        
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Email Address',
            'class': 'form-control',
        })


class CustomResetPasswordKeyForm(ResetPasswordKeyForm):
    """
    Override settings on AllAuth reset password from key form.
    """    
    
    def __init__(self, *args, **kwargs):
        super(CustomResetPasswordKeyForm, self).__init__(*args, **kwargs)

        self.fields['password1'].label = ""
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'New Password',
            'class': 'form-control',
        })
        
        self.fields['password2'].label = ""
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm New Password',
            'class': 'form-control',
        }) 