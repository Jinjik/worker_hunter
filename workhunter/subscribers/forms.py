from django import forms

from .models import Subscriber
from scraping.models import Speciality, City


class SubscriberModelForm(forms.ModelForm):
    email = forms.EmailField(
        label='E-mail', required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    city = forms.ModelChoiceField(
        label='Город', queryset=City.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    speciality = forms.ModelChoiceField(
        label='Специальность', queryset=Speciality.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Subscriber
        fields = ('email', 'city', 'speciality', 'password', )
        exclude = ('is_active', )


class LogInForm(forms.Form):
    email = forms.EmailField(
        label='E-mail', required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_password(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            qs = Subscriber.objects.filter(email=email).first()

            if qs is None:
                raise forms.ValidationError('Пользователя с таким email не существует')
            elif password != qs.password:
                raise forms.ValidationError('Неверный пароль')

        return email


class SubscriberHiddenEmailForm(forms.ModelForm):
    city = forms.ModelChoiceField(
        label='Город', queryset=City.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    speciality = forms.ModelChoiceField(
        label='Специальность', queryset=Speciality.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.HiddenInput())
    is_active = forms.BooleanField(label='Получать рассылку', required=False, widget=forms.CheckboxInput())

    class Meta:
        model = Subscriber
        fields = ('email', 'city', 'speciality', 'password', 'is_active')


class ContactForm(forms.Form):
    email = forms.EmailField(label='E-mail', required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    city = forms.CharField(label='Город', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    speciality = forms.CharField(label='Специальность', widget=forms.TextInput(attrs={'class': 'form-control'}))
