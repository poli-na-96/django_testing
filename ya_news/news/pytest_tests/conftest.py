from datetime import datetime, timedelta
import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from news.models import News, Comment


User = get_user_model()

COMMENT_TEXT = 'Текст комментария'

NEW_COMMENT_TEXT = 'Обновлённый комментарий'


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст'
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author
    )
    return comment


@pytest.fixture
def url(news):
    url = reverse('news:detail', args=(news.id,))
    return url


@pytest.fixture
def form_data():
    form_data = {'text': COMMENT_TEXT}
    return form_data


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create(username='Мимо крокодил')


@pytest.fixture
def user_client(user, client):
    client.force_login(user)
    return client


@pytest.fixture
def url_to_comments(news):
    news_url = reverse('news:detail', args=(news.id,))
    url_to_comments = news_url + '#comments'
    return url_to_comments


@pytest.fixture
def new_comment(news, author_comm):
    new_comment = Comment.objects.create(
        news=news,
        author=author_comm,
        text=NEW_COMMENT_TEXT
    )
    return new_comment


@pytest.fixture
def author_comm(django_user_model):
    return django_user_model.objects.create(username='Автор новости')


@pytest.fixture
def author_comm_client(author_comm, client):
    client.force_login(author_comm)
    return client


@pytest.fixture
def edit_url(new_comment):
    edit_url = reverse('news:edit', args=(new_comment.id,))
    return edit_url


@pytest.fixture
def delete_url(new_comment):
    delete_url = reverse('news:delete', args=(new_comment.id,))
    return delete_url


@pytest.fixture
def form_data_new():
    form_data_new = {'text': NEW_COMMENT_TEXT}
    return form_data_new


@pytest.fixture
def all_news():
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


@pytest.fixture
def test_news():
    test_news = News.objects.create(
        title='Тестовая новость', text='Просто текст.'
    )
    return test_news


@pytest.fixture
def detail_url(test_news):
    detail_url = reverse('news:detail', args=(test_news.id,))
    return detail_url


@pytest.fixture
def commentor(test_news):
    commentor = User.objects.create(username='Комментатор')
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=test_news, author=commentor, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return commentor


@pytest.fixture
def id_for_args(news):
    return news.id,
