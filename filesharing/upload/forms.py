from django import forms
from models import file, myUser, folder
from django.contrib.auth.models import User


class userForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'First Name',
                'required': 'required',
                'class': 'form-control',
            }
        )
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Last Name',
                'required': 'required',
                'class': 'form-control',
            }
        )
    )
    username = forms.RegexField(
        label="Employee Id",
        regex=r'^\d+$',
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Employee Id',
                'pattern': '\d+',
                'required': 'required',
                'title': 'Must be in digits',
                'class': 'form-control',
            }),
        error_message='Must be in digits'
    )
    confirm_password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Confirm Password',
                'required': 'required',
                'class': 'form-control',
            }
        )
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'Email',
                'required': 'required',
                'class': 'form-control',
            }
        )
    )

    class Meta:
        model = User
        widgets = {
            'password': forms.PasswordInput(
                attrs={
                    'placeholder': 'Password',
                    'required': 'required',
                    'class': 'form-control',
                }
            ),
        }
        fields = ('first_name', 'last_name', 'email',
                  'username', 'password', 'confirm_password')

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password:
            if not password == confirm_password:
                raise forms.ValidationError("Passwords donot match")
        return confirm_password


class myUserForm(forms.ModelForm):
    class Meta:
        model = myUser
        fields = ()


class fileForm(forms.ModelForm):
    fileDb = forms.FileField(label='Select the File')

    class Meta:
        model = file
        fields = ['fileDb']

    def clean_fileDb(self):
        tempFile = self.cleaned_data.get('fileDb', False)
        if tempFile:
            if tempFile.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Upload File too Large(>10MB)")
            return tempFile
        else:
            raise forms.ValidationError("Cannot read Uploaded file")


accessChoices = (
    ('R', 'Read'),
    ('W', 'Read/Write'),
)


class shareForm(forms.Form):
    username = forms.CharField(
        label='Employee Id',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Type Employee Id and Hit Enter',
                'class': 'form-control tokenfield',
            }),
        required=True
    )
    access = forms.ChoiceField(
        widget=forms.RadioSelect(),
        label='Access',
        choices=accessChoices,
        initial='R'
    )
