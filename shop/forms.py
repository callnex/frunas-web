from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(
        label='Nombre completo',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Ej. Willy Wonka'}),
    )
    username = forms.CharField(
        label='Nombre de usuario',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Ej. candyfan123'}),
    )
    email = forms.EmailField(
        label='Correo electronico',
        widget=forms.EmailInput(attrs={'placeholder': 'tu@correo.dulce'}),
    )
    password1 = forms.CharField(
        label='Contrasena',
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Minimo 8 caracteres'}),
    )
    password2 = forms.CharField(
        label='Confirmar contrasena',
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Repite tu contrasena'}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('full_name', 'username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este correo ya esta registrado.')
        return email

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya existe.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['full_name'].strip()
        user.email = self.cleaned_data['email'].strip().lower()
        user.is_active = False
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={'placeholder': 'Tu nombre de usuario'}),
    )
    password = forms.CharField(
        label='Contrasena',
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Tu contrasena'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
