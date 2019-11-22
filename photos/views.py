import hashlib
from itertools import chain
from IPython import embed
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Photo, Comment, Hashtag
from .forms import PhotoForm, CommentForm

# Create your views here.
def index(request):
  # if request.user.is_authenticated:
  #   gravatar_url = hashlib.md5(request.user.email.encode('utf-8').lower().strip()).hexdigest()
  # else:
  #   gravatar_url = None

  photos = Photo.objects.all()
  context = {'photos':photos,}
  return render(request,'photos/index.html',context)

@login_required
def create(request):
  #사용자로부터 데이터를 받아서 DB에 저장하는 함수
  if request.method == 'POST':
    form = PhotoForm(request.POST, request.FILES)
    # embed()
    if form.is_valid():
      photo = form.save(commit = False)

      photo.user = request.user
      photo=form.save()
      # hashtag
      # 게시글 내용을 split해서 리스트로 만듦
      for word in photo.content.split():
        # word가 '#'으로 시작할 경우 해시태그 등록
        if word.startswith('#'):
          hashtag, created = Hashtag.objects.get_or_create(content=word)
          photo.hashtags.add(hashtag)
    return redirect('photos:detail', photo.pk)
  else:
    form = PhotoForm()

  #form으로 전달받는 형태 2가지
  # 1. GET 요청 -> 비어있는 폼 전달
  # 2. 유효성 검증 실패 -> 에러 메시지를 포함한 채로 폼 전달
  context = {'form':form}
  return render(request,'photos/form.html', context)

#게시글 상세정보를 가져오는 함수
def detail(request,photo_pk):
  #article = Article.objects.get(pk=article_pk)
  photo = get_object_or_404(Photo, pk=photo_pk)
  
  person = get_object_or_404(get_user_model(), pk=photo.user_id)
  comment_form = CommentForm()
  comments = photo.comment_set.all()
  context = {
    'photo':photo,
    'person':person,
    'comment_form':comment_form,
    'comments':comments,
  }
  return render(request,'photos/detail.html',context)

@require_POST
def delete(request, photo_pk):
  # 지금 사용자가 로그인 되어 있는가?
  if request.user.is_authenticated:
    # 삭제할 게시글 가져옴  
    photo = get_object_or_404(Photo, pk=photo_pk)
    # 지금 로그인한 사용자와 게시글 작성자 비교
    if request.user == photo.user:
      photo.delete()
    else:
      return redirect('photos:detail', photo.pk)
  return redirect('photos:index')
  
@login_required
def update(request, photo_pk):
  photo = get_object_or_404(Photo, pk=photo_pk)
  if request.user == photo.user:
    if request.method == 'POST':
      form = PhotoForm(request.POST, instance=photo)
      if form.is_valid():
        photo = form.save()
        # hashtag
        photo.hashtags.clear()
        for word in photo.content.split():
          if word.startswith('#'):
            hashtag, create = Hashtag.objects.get_or_create(content=word)
            photo.hashtags.add(hashtag)

        return redirect('photos:detail', photo.pk)
    else :
      form = PhotoForm(instance=photo)
  else:
    return redirect('photos:index')

  context = {
    'form':form,
    'photo':photo,
  }
  return render(request, 'photos/form.html', context)

# 댓글 생성 뷰 함수
@require_POST
def comment_create(request, photo_pk):
  if request.user.is_authenticated:
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
      comment = comment_form.save(commit=False)
      comment.user = request.user
      comment.photo_id = photo_pk
      comment.save()
  return redirect('photos:detail', photo_pk)


#댓글 삭제 뷰 함수
@require_POST
def comment_delete(request, photo_pk, comment_pk):
  # 1. 로그인 여부 확인
  if request.user.is_authenticated:
    comment = get_object_or_404(Comment, pk=comment_pk)
    # 2. 로그인한 사용자와 댓글 작성자가 같을 경우
    if request.user == comment.user:
      comment.delete()
  return redirect('photos:detail', photo_pk)

@login_required
def like(request, photo_pk):
  # 좋아요 누를 게시글 가져오기
  photo = get_object_or_404(Photo, pk=photo_pk)
  # 현재 접속하고 있는 유저
  user = request.user

  # 현재 게시글을 좋아요 누른 사람 목록에서, 
  # 현재 접속한 유저가 있을 경우 -> 좋아요 취소
  if user in photo.like_users.all():
    photo.like_users.remove(user)
  # 목록에 없을 경우 -> 좋아요 누르기
  else:
    photo.like_users.add(user)
  return redirect('photos:index')

@login_required
def follow(request, photo_pk, user_pk):
  # 게시글 작성한 유저
  person = get_object_or_404(get_user_model(), pk=user_pk)
  # 지금 접속하고 있는 유저
  user = request.user
  # 게시글 작성 유저 팔로워 명단에 접속 중인 유저가 있을 경우
  # -> 언팔
  if person != user :
    if user in person.followers.all():
      person.followers.remove(user)
    # 명단에 없으면
    # -> 팔로우
    else:
      person.followers.add(user)
    # 게시글 상세정보로 redirect
  return redirect('photos:detail', photo_pk)

# 내가 팔로우 하는 사람의 글 + 내가 작성한 글
def list(request):
  # 내가 팔로우하고 있는 사람들
  followings = request.user.followers.all()
  # 내가 팔로우하고 있는 사람들 + 나 -> 합치기
  followings = chain(followings, [request.user])
  # 위 명단 사람들 게시글 가져오기
  photos = Photo.objects.filter(user__in=followings).order_by('-pk').all()
  comment_form = CommentForm()
  context = {
    'photos':photos,
    'comment_form':comment_form,
  }
  return render(request, 'photos/photo_list.html', context)

# 모든 사람 글
def explore(request):
  photos = Photo.objects.all()
  comment_form = CommentForm()
  context = {
    'photos':photos,
    'comment_form':comment_form,
  }
  return render(request, 'photos/photo_list.html', context)

def hashtag(request, hash_pk):
  # 해시태그 가져오기
  hashtag = get_object_or_404(Hashtag, pk=hash_pk)
  # 해당 해시태그를 참조하는 게시글들 가져오기
  photos = hashtag.photo_set.order_by('-pk')
  context = {
    'hashtag' : hashtag,
    'photos' : photos,
  }
  return render(request, 'photos/hashtag.html', context)



def test(request):
  return render(request, 'photos/test.html')