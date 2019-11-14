from django import forms
from .models import Photo, Comment

class PhotoForm(forms.ModelForm) :

  # 메타 데이터 -> 데이터의 데이터
  # ex) 사진 한장 (촬영장비 이름, 촬영환경 등)
  class Meta:
    model = Photo
    fields = ('photo','content')


class CommentForm(forms.ModelForm):
  content = forms.CharField(
    label='댓글',
    widget=forms.Textarea(
      attrs={
        'class':'content',
        'placeholder':'댓글 입력해라...',
        'rows':1,
        
      }
    )
  )

  class Meta:
    model = Comment
    fields = ('content',)

