from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class RegisterForm(UserCreationForm):
	email = forms.EmailField(max_length=200, required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")
	
	def __init__(self, *args, **kwargs):
		super(RegisterForm, self).__init__(*args, **kwargs)

		input_classes = "rounded-lg text-gray-800 block w-full px-4 py-3 mb-4 border border-transparent border-gray-200 focus:ring focus:ring-indigo-400 focus:outline-none"
		self.fields['username'].widget.attrs['class'] = self.fields['email'].widget.attrs['class'] = self.fields['password2'].widget.attrs['class'] = input_classes
		self.fields['password1'].widget.attrs['class'] = input_classes[10:] + " rounded-l-lg"

		self.fields['username'].widget.attrs['placeholder'] = 'Username'
		self.fields['email'].widget.attrs['placeholder'] = 'E-mail address'
		self.fields['password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['password2'].widget.attrs['placeholder'] = 'Repeat password'
		
	def save(self, commit=True):
		user = super(RegisterForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user

class LoginForm(AuthenticationForm):
	remember_me = forms.BooleanField(required=False)

	def __init__(self, *args, **kwargs):
		super(LoginForm, self).__init__(*args, **kwargs)

		input_classes = "rounded-lg text-gray-800 block w-full px-4 py-3 mb-4 border border-transparent border-gray-200 focus:ring focus:ring-indigo-400 focus:outline-none"
		self.fields['username'].widget.attrs['class'] = input_classes
		self.fields['password'].widget.attrs['class'] = input_classes[10:] + " rounded-l-lg"
		self.fields['remember_me'].widget.attrs['class'] = 'form-checkbox h-5 w-5 text-green-400'

		self.fields['username'].widget.attrs['placeholder'] = 'Username'
		self.fields['password'].widget.attrs['placeholder'] = 'Password'