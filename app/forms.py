from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.template.context_processors import request

from app.models import Profile, Question, Tag, Answer


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']

        if not username.isalnum():
            self.add_error('username', 'Username should be alphanumeric')
        return username.strip()


class UserForm(forms.ModelForm):
    nickname = forms.CharField(widget=forms.TextInput, label="Nickname")
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirmation = forms.CharField(widget=forms.PasswordInput)
    avatar = forms.ImageField(required=False)
    username = forms.CharField(widget=forms.TextInput, label="Login")

    class Meta:
        model = User
        fields = ('username', 'email', 'nickname', 'password', 'password_confirmation', 'avatar')

    def clean(self):
        data = super().clean()

        if data['password'] != data['password_confirmation']:
            raise ValidationError('Passwords do not match!')

        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.save()
        profile = Profile(user=user, image=self.cleaned_data['avatar'], nickname=self.cleaned_data['nickname'])
        profile.save()


        return user

class SettingsForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput, label="Login", required=False)
    avatar = forms.ImageField(widget=forms.FileInput, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    nickname = forms.CharField(widget=forms.TextInput, label='Nickname', required=False)

    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        profile_instance = kwargs.pop('profile_instance', None)
        super().__init__(*args, **kwargs)

        if profile_instance:
            self.fields['avatar'].initial = profile_instance.image
            self.fields['bio'].initial = profile_instance.bio
            self.fields['nickname'].initial = profile_instance.nickname

    def save(self, user_instance=None, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

        if user_instance:
            profile, _ = Profile.objects.get_or_create(user=user_instance)
            profile.image = self.cleaned_data.get('avatar', profile.image)
            profile.bio = self.cleaned_data.get('bio', profile.bio)
            profile.nickname = self.cleaned_data.get('nickname', profile.nickname)
            profile.save()

        return user

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if username == '':
            raise ValidationError('Username cannot be empty')

        try:
            User.objects.exclude(pk=self.instance.pk).get(username=username)
        except ObjectDoesNotExist:
            return username
        raise ValidationError(f"User with username: {username} already exists")

    def clean_nickname(self):
        nickname = self.cleaned_data['nickname'].strip()
        if nickname == '':
            raise ValidationError('Nickname cannot be empty')

        try:
            Profile.objects.exclude(user=self.instance).get(nickname=nickname)
        except ObjectDoesNotExist:
            return nickname
        raise ValidationError(f"User with nickname: {nickname} already exists")


class AskForm(forms.ModelForm):
    title = forms.CharField()
    text = forms.CharField(widget=forms.Textarea)
    tags = forms.CharField(widget=forms.TextInput, help_text='Separate tags with comma')

    class Meta:
        model = Question
        fields = ('title', 'text', 'tags')

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        tags = [tag.strip() for tag in tags.split(',')]
        for tag in tags:
            if not tag.isidentifier():
                self.add_error('tags', 'Tags should be alphanumeric')
        return tags

    def save(self, user=None, commit=True):
        question = Question(title=self.cleaned_data['title'], text=self.cleaned_data['text'], author=user)
        if commit:
            question.save()
        tags = self.cleaned_data['tags']
        for tag in tags:
            tag, _ = Tag.objects.get_or_create(tag_name=tag)
            question.tags.add(tag)
        return question


class AnswerForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter your answer here...'}),
                           label='Add answer')

    class Meta:
        model = Answer
        fields = ('text',)

    def save(self, question=None, user=None, commit=True):
        answer = super().save(commit=False)
        answer.question = question
        answer.author = user
        question.num_answers += 1
        if commit:
            answer.save()
            question.save()
        return answer

    def get_answer_id(self):
        return self.instance.id