from http import HTTPStatus
import pytest

from django.contrib.auth import get_user_model

from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


User = get_user_model()

COMMENT_TEXT = 'Текст комментария'

NEW_COMMENT_TEXT = 'Обновлённый комментарий'


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, url, form_data):
    Comment.objects.all().delete()
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(url, form_data, user_client, user, news):
    response = user_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == user


@pytest.mark.django_db
@pytest.mark.parametrize(
    'word',
    BAD_WORDS
)
def test_user_cant_use_bad_words(url, user_client, word):
    bad_words_data = {'text': f'Какой-то текст, {word}, еще текст'}
    response = user_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment(url_to_comments, new_comment,
                                   author_comm_client, delete_url):
    previous_comments_count = Comment.objects.count()
    response = author_comm_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert previous_comments_count - comments_count == 1
    assert new_comment.id not in Comment.objects.all()


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(user_client, delete_url):
    response = user_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_edit_comment(url_to_comments, author_comm_client,
                                 new_comment, edit_url, form_data_new):
    response = author_comm_client.post(edit_url, data=form_data_new)
    assertRedirects(response, url_to_comments)
    new_comment.refresh_from_db()
    assert new_comment.text == NEW_COMMENT_TEXT


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(user_client, comment,
                                                edit_url, form_data):
    response = user_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
