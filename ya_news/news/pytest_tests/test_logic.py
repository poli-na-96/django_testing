import pytest
from http import HTTPStatus

from django.contrib.auth import get_user_model

from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

from .help_functions import (set_up_data_for_logic_tests_create_comments,
                             set_up_data_for_logic_tests_delete_comments)


User = get_user_model()

COMMENT_TEXT = 'Текст комментария'

NEW_COMMENT_TEXT = 'Обновлённый комментарий'


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client):
    url, form_data, _, _, _ = set_up_data_for_logic_tests_create_comments()
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment():
    (url, form_data, auth_client,
        user, news) = set_up_data_for_logic_tests_create_comments()
    response = auth_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == user


@pytest.mark.django_db
def test_user_cant_use_bad_words():
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url, _, auth_client, _, _ = set_up_data_for_logic_tests_create_comments()
    response = auth_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment():
    (url_to_comments, author_client,
        _, _, _, delete_url, _) = set_up_data_for_logic_tests_delete_comments()
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user():
    (_, _, reader_client,
        _, _, delete_url, _) = set_up_data_for_logic_tests_delete_comments()
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_edit_comment():
    (url_to_comments, author_client, _, comment,
        edit_url, _, form_data) = set_up_data_for_logic_tests_delete_comments()
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user():
    (_, _, reader_client, comment,
        edit_url, _, form_data) = set_up_data_for_logic_tests_delete_comments()
    response = reader_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
