from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, required=True)
    password = forms.CharField(
        label='password', required=True, max_length=20, min_length=6, widget=forms.PasswordInput)