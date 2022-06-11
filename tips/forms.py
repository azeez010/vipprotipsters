from django.forms import CharField, PasswordInput, forms, ModelForm, EmailInput
from tips.models import User

class SignUp(ModelForm):
    password = CharField(widget=PasswordInput, required=True)
    confirm_password = CharField(widget=PasswordInput, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'country', 'password']
    
    def __init__(self, *args, **kwargs):
        super(SignUp, self).__init__(*args, **kwargs)

        for fieldname in ['username']:
            self.fields[fieldname].help_text = None

    def clean(self):
        cleaned_data = super(SignUp, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "password and confirm_password does not match"
            )
       
class Login(forms.Form): 
    email = CharField(widget=EmailInput, max_length=300, required=True, help_text=None)
    password = CharField(widget=PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        super(Login, self).__init__(*args, **kwargs)

        for fieldname in ['email', 'password']:
            self.fields[fieldname].help_text = None
        
    