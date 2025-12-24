from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import CV, CustomUser, DescriptionJobOffer, DomainCV

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        label="", 
        widget=forms.TextInput(attrs={
            'class': 'form-style', 
            'placeholder': 'Your Email', 
            'id': 'logemail', 
            'autocomplete': 'off'
        })
    )

    username = forms.CharField(
        label="", 
        max_length=100, 
        widget=forms.TextInput(attrs={
            'class': 'form-style', 
            'placeholder': 'Your Full Name', 
            'id': 'logname',
            'autocomplete': 'off'
        })
    )

    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-style',
            'id': 'role'
        })
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'role')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-style',
            'placeholder': 'Your Password',
            'id': 'logpass1',
            'autocomplete': 'off'
        })

        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-style',
            'placeholder': 'Repeat Password',
            'id': 'logpass2',
            'autocomplete': 'off'
        })

        self.fields['username'].label = ''
        self.fields['username'].help_text = ''
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = ''

class UploadCVForm(forms.ModelForm):
    domains = forms.ModelMultipleChoiceField(
        queryset=DomainCV.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        required=True,
        label="Domaines de compétence"
    )

    class Meta:
        model = CV
        fields = ["fichier", "domains"]

class JobDescriptionForm(forms.ModelForm):
    class Meta:
        model = DescriptionJobOffer
        fields = ["description", "domain"]
        widgets = {
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "domain": forms.Select(attrs={"class": "form-control"}),
        }


