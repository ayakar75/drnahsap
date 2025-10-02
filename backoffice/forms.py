from django import forms


class ManagerLoginForm(forms.Form):
    email = forms.EmailField(label="E-posta")
    password = forms.CharField(label="Şifre", widget=forms.PasswordInput)
