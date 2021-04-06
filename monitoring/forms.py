from django import forms
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):

    username = forms.CharField(label='', help_text='', widget=forms.TextInput(attrs={'placeholder': 'username'}))
    password = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'password', 'type': 'password'}))
    password_repeat = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'repeat password', 'type': 'password'}))
    email = forms.EmailField(label='', widget=forms.TextInput(attrs={'placeholder': 'e-mail'}))

    class Meta:
        model = User
        fields = ('username', 'password', 'password_repeat', 'email')


class AddServerForm(forms.Form):
    ip = forms.CharField(label='', help_text='', widget=forms.TextInput(attrs={'placeholder': 'ip'}))
    port = forms.IntegerField(help_text='', widget=forms.TextInput(attrs={'placeholder': 'port'}))
