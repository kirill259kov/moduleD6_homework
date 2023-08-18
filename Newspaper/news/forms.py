from django.forms import ModelForm
from .models import Post
from django import forms
from django.contrib.auth.models import Group
from django.db import models


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['author', 'postCategory', 'categoryType', 'title', 'text']


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=30, label='Name')

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        basic_group = Group.objects.get_or_create(name='common')[0]
        basic_group.user_set.add(user)
        user.save()

