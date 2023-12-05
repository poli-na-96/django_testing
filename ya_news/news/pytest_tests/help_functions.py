from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

User = get_user_model()

COMMENT_TEXT = 'Текст комментария'

NEW_COMMENT_TEXT = 'Обновлённый комментарий'


def set_up_data_for_logic_tests_create_comments():
    news = News.objects.create(title='Заголовок', text='Текст')
    url = reverse('news:detail', args=(news.id,))
    form_data = {'text': COMMENT_TEXT}
    user = User.objects.create(username='Мимо Крокодил')
    auth_client = Client()
    auth_client.force_login(user)
    return url, form_data, auth_client, user, news


def set_up_data_for_logic_tests_delete_comments():
    news = News.objects.create(title='Заголовок', text='Текст')
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = news_url + '#comments'
    author = User.objects.create(username='Автор комментария')
    author_client = Client()
    author_client.force_login(author)
    reader = User.objects.create(username='Читатель')
    reader_client = Client()
    reader_client.force_login(reader)
    comment = Comment.objects.create(
        news=news,
        author=author,
        text=COMMENT_TEXT
    )
    edit_url = reverse('news:edit', args=(comment.id,))
    delete_url = reverse('news:delete', args=(comment.id,))
    form_data = {'text': NEW_COMMENT_TEXT}
    return (url_to_comments, author_client, reader_client,
            comment, edit_url, delete_url, form_data)


def set_up_data_for_route_tests_for_list_of_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


def set_up_data_for_route_tests_create_for_one_page():
    news = News.objects.create(
        title='Тестовая новость', text='Просто текст.'
    )
    detail_url = reverse('news:detail', args=(news.id,))
    author = User.objects.create(username='Комментатор')
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return detail_url, author
