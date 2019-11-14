from django.contrib import admin
from .models import Photo, Comment, Hashtag

class PhotoAdmin(admin.ModelAdmin):
  list_display = ('pk','photo','content','created_at','updated_at')

class CommentAdmin(admin.ModelAdmin):
  list_display = ('pk','content','created_at','updated_at')

class HashtagAdmin(admin.ModelAdmin):
  list_display = ('content',)


admin.site.register(Photo, PhotoAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Hashtag, HashtagAdmin)