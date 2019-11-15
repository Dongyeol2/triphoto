from django import template

register = template.Library()

@register.filter
def hashtag_link(photo):
  content = photo.content + ' '
  hashtags = photo.hashtags.all()

  for hashtag in hashtags:
    content = content.replace(
      hashtag.content + ' ',
      f'<a href="photos/{hashtag.pk}/hashtag/">{hashtag.content}</a> '
    )
  return content
