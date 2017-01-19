from django import forms
from .models import User, Post, Comment, SearchTerm

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        emailBase, provider = email.split("@")
        domain, extension = provider.split(".")
        return email

    def clean__password(self):
        password = self.cleaned_data.get('password')
        return password

    def clean(self):
        return self.cleaned_data

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ['slug']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ['post']

class SearchForm(forms.ModelForm):
	class Meta:
		model = SearchTerm
		fields = ['category']