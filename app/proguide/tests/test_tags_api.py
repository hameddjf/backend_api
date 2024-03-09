"""tests forr the tags api"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, ProGuide
from proguide.serializers import TagSerializer

from decimal import Decimal


TAGS_URL = reverse('proguide:tag-list')


def detail_url(tag_id):
    """create and return a tag detail url"""
    return reverse('proguide:tag-detail', args=[tag_id])


def create_user(email='hameddjf33@gmail.com', password='12345678'):
    """create and return a user"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsTests(TestCase):
    """test unauthenticated api requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """test auth is required for retrieving tags"""
        resullt = self.client.get(TAGS_URL)

        self.assertEqual(resullt.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """test authenticated api requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """test retrieving a list of tags"""
        Tag.objects.create(user=self.user, name='hameddjf01')
        Tag.objects.create(user=self.user, name='hameddjf02')

        result = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_tags_limited_to_user(self):
        """test list of tags is limited to authenticated user"""
        user2 = create_user(email='hameddjf01@gmail.com')
        Tag.objects.create(user=user2, name='hameddjf03')
        tag = Tag.objects.create(user=self.user, name='hameddjf04')

        result = self.client.get(TAGS_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        # check for 1 result return (1 tag in response)
        self.assertEqual(len(result.data), 1)
        """more test for check the first name &
                        id of first response will the user is authenticate"""
        self.assertEqual(result.data[0]['name'], tag.name)
        self.assertEqual(result.data[0]['id'], tag.id)

    def test_update_tag(self):
        tag = Tag.objects.create(user=self.user, name='hameddjf01')
        payload = {'name': 'hameddjf'}
        url = detail_url(tag.id)
        result = self.client.patch(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_deleting_tag(self):
        """test deleting a tag"""
        tag = Tag.objects.create(user=self.user, name='hameddjf03')
        url = detail_url(tag.id)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_proguide(self):
        """test listing tags to those assigned to proguide"""
        tag1 = Tag.objects.create(user=self.user, name='hameddjf33')
        tag2 = Tag.objects.create(user=self.user, name='hameddjf01')
        proguide = ProGuide.objects.create(
            title='hameddjf33@gmail.com',
            time_minutes=23,
            price=Decimal('2.43'),
            user=self.user,
        )
        proguide.tags.add(tag1)

        result = self.client.get(TAGS_URL, {'assigned_only': 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertIn(s1.data, result.data)
        self.assertNotIn(s2.data, result.data)

    def test_filtered_tags_unique(self):
        """test filtered tags returns a unique list"""
        tag = Tag.objects.create(user=self.user, name='hameddjf33')
        Tag.objects.create(user=self.user, name='hameddjf01')
        proguide1 = ProGuide.objects.create(
            title='hameddjf33@gmail.com',
            time_minutes=4,
            price=Decimal('43.23'),
            user=self.user,
        )
        proguide2 = ProGuide.objects.create(
            title='hameddjf01@gmail.com',
            time_minutes=32,
            price=Decimal('55.55'),
            user=self.user,
        )

        proguide1.tags.add(tag)
        proguide2.tags.add(tag)

        result = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(result.data), 1)
