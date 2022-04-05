from posts.models import Post, Comment
from django import forms


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_text(self):
        data = self.cleaned_data['text']
        if not data == '':
            return data
        raise forms.ValidationError('Поле необходимо заполнить')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        data = self.cleaned_data['text']
        if not data == '':
            return data
        raise forms.ValidationError('Поле необходимо заполнить')
