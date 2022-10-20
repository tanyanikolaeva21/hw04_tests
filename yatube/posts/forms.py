from django import forms
from .models import Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        help_texts = {
            'text': 'Напишите новый текст сообщения',
            'group': 'Выберете группу',
        }
        fields = ('text', 'group')
