'''
Created on Mar 25, 2015

@author: ansh
'''
from django.contrib.auth.models import User
from django import forms
from django.core.validators import MinLengthValidator,RegexValidator
from .models import UserProfile,Sharing,ProfilePicture



class UserForm(forms.ModelForm):
    password = forms.CharField(label='Password',widget=forms.PasswordInput(attrs={'class':'input_box','size': '30'}),validators=[MinLengthValidator(6),RegexValidator(r'^[a-zA-Z]\w*$',message='Enter according to the format given.')])
    email=forms.EmailField(label='Email',widget=forms.TextInput(attrs={'class':'input_box','size': '30'}))
    username=forms.CharField(label='Username',widget=forms.TextInput(attrs={'class':'input_box','size': '30'}),validators=[MinLengthValidator(6)])
    first_name=forms.CharField(label='Name',widget=forms.TextInput(attrs={'class':'input_box','size': '30'}),validators=[MinLengthValidator(4),RegexValidator(r'^[a-zA-Z ]*$',message='Only spaces & alphabets allowed.')])
    class Meta:
        model = User
        fields = ('username','first_name','email', 'password',)
    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(username=username).count():
            raise forms.ValidationError(u'Email ID already in use.')
        return email



class UserProfileForm(forms.ModelForm):
    GENDER_CHOICES=[('male','Male'),('female','Female')]
    dob=forms.DateField(widget=forms.DateInput(format = '%Y-%m-%d',attrs={'id':'dob','placeholder': 'Date of Birth (YYYY-MM-DD)','required':'required', 'class':'form-control'}),input_formats=('%Y-%m-%d',))
    number=forms.CharField(widget=forms.TextInput(attrs={'id':'number','required':'required','placeholder':'Enter Phone Number','class':'form-control'}))
    institute=forms.CharField(widget=forms.TextInput(attrs={'id':'institute','placeholder':'Enter College or Institute Name','required':'required','class':'form-control'}))
    gender=forms.ChoiceField(choices=GENDER_CHOICES,widget=forms.Select(attrs={'id':'gender','required':'required','class':'form-control'}))
    class Meta:
        model = UserProfile
        fields = ('dob','gender','institute','number')



class ProfilePictureForm(forms.ModelForm):
    picture=forms.ImageField(label='Profile Picture',required=False,error_messages ={'invalid':"Image files only"},\
                                   widget=forms.FileInput(attrs={'onchange':'display_thumbnail(this);','id':'uploaded_picture'}))
    class Meta:
        model = ProfilePicture
        fields = ('picture',)



class SharingForm(forms.ModelForm):
    share_to=forms.CharField(widget=forms.TextInput(attrs={'id':'share_username','name':'share_username','placeholder':'Enter username',
                                                           'class':'form-control','type':'search','autocomplete':'off'
                                                           }))
    document=forms.FileField(widget=forms.FileInput(attrs={'id':'shared_document','name':'shared_document','type':'file','onchange':'checkForMimeAndSize(this);'}))
    message=forms.CharField(widget=forms.Textarea(attrs={'id':'shared_message','name':'shared_message','cols':'60','rows':'3','placeholder':'You may send a message. Maximum of 120 characters','word-wrap':'break-word','resize':'none',}),required=False)
    class Meta:
        model = Sharing
        fields=('share_to','document','message')
