from django.forms import CharField, PasswordInput, TextInput, forms, ModelForm, EmailInput
from tips.models import User


class ChangePassword(ModelForm):
    password = CharField(label="", widget=PasswordInput(attrs={'placeholder': 'Password', "class": "w-full border-2 border-gray-500 my-2 py-2 px-2"}), required=True)
    confirm_password = CharField(label="", widget=PasswordInput(attrs={'placeholder': 'Confirm password', "class": "w-full border-2 border-gray-500 my-2 py-2 px-2"}), required=True)
    
    class Meta:
        model = User
        fields = ['password']


class SignUp(ModelForm):
    password = CharField(label="", widget=PasswordInput(attrs={'placeholder': 'Password', "class": "w-full border-2 border-gray-500 my-1 py-1 px-2"}), required=True)
    confirm_password = CharField(label="", widget=PasswordInput(attrs={'placeholder': 'Confirm password', "class": "w-full border-2 border-gray-500 my-1 py-1 px-2"}), required=True)

    
    class Meta:
        model = User
        fields = ['username', 'email', 'country', 'password']
        widgets = {
            'name': TextInput(attrs={'placeholder': 'Username', "class": "w-full border-2 border-gray-500 my-2 py-2 px-2"}),
            'email': EmailInput(attrs={'placeholder': 'Email Address', "class": "w-full border-2 border-gray-500 my-2 py-2 px-2"}),
        }
    
    def __init__(self, *args, **kwargs):
        super(SignUp, self).__init__(*args, **kwargs)
        
        for fieldname in ['username', 'country', 'email']:
            self.fields[fieldname].label = ""
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update({'class': 'w-full border-2 border-gray-500 my-2 py-2 px-2'})


    def clean(self):
        cleaned_data = super(SignUp, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "password and confirm_password does not match"
            )
       
class Login(forms.Form): 
    email = CharField(label="", widget=EmailInput(attrs={'placeholder': 'Email Address', "class": "w-full border-2 border-gray-500 my-2 py-2 px-2"}), max_length=300, required=True, help_text=None)
    password = CharField(label="", widget=PasswordInput(attrs={'placeholder': 'Password',"class": "w-full border-2 border-gray-500 my-2 py-2 px-2"}), required=True)

    def __init__(self, *args, **kwargs):
        super(Login, self).__init__(*args, **kwargs)

        for fieldname in ['email', 'password']:
            self.fields[fieldname].help_text = None
        
    