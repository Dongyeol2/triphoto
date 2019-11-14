from django import template

register = template.Library()

@register.filter
def hashtag_link(article):
  content = photos.content + ' '
  hashtags = photos.hashtags.all()

  for hashtag in hashtags:
    content = content.replace(
      hashtag.content + ' ',
      f'<a href="photos/{hashtag.pk}/hashtag/">{hashtag.content}</a> '
    )
  return content
