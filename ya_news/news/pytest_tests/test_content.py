import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

from .help_functions import (set_up_data_for_route_tests_for_list_of_news,
                             set_up_data_for_route_tests_create_for_one_page)

User = get_user_model()

HOME_URL = reverse('news:home')


@pytest.mark.django_db
def test_news_count(client):
    set_up_data_for_route_tests_for_list_of_news()
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client):
    set_up_data_for_route_tests_for_list_of_news()
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, ):
    response = client.get(set_up_data_for_route_tests_create_for_one_page()[0])
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client):
    response = client.get(set_up_data_for_route_tests_create_for_one_page()[0])
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(client):
    url, author = set_up_data_for_route_tests_create_for_one_page()
    client.force_login(author)
    response = client.get(url)
    assert 'form' in response.context
