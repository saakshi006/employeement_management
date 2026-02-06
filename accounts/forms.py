from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Email or Username'
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email or Username'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})

class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role')
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    # UserCreationForm's password fields are not in Meta, so we handle them in __init__
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['role', 'username', 'email']: # Passwords
                 field.widget.attrs['class'] = 'form-control'
