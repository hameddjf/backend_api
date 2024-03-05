"""tests for proguide apis"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from decimal import Decimal

from core.models import ProGuide, Tag
from proguide.serializers import ProGuideSerializer, ProGuideDetailSerializer


PROGUIDES_URL = reverse('proguide:proguide-list')


def detail_url(proguide_id):
    """create and return a proguide detail url"""
    return reverse("proguide:proguide-detail", args=[proguide_id])


def create_proguide(user, **params):
    """create and return a sample proguide"""
    defaults = {
        'title': 'object num1',
        'time_minutes': 22,
        'price': Decimal('1.11'),
        'description': 'description object num1',
        'link': 'http://example.com/proguide.pdf',
    }

    defaults.update(params)

    proguide = ProGuide.objects.create(user=user, **defaults)
    return proguide


def create_user(**params):
    """create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicProGuideAPITests(TestCase):
    """test unauthenticated api requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """test auth is required to call api"""
        result = self.client.get(PROGUIDES_URL)

        # retrieve just user is authenticated
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProGuideApiTest(TestCase):
    """test authenticated api requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='hameddjf33@gmail.com', password='12345678')
        self.client.force_authenticate(self.user)

    def test_retrieve_proguide(self):
        """test retrieving a list of proguide"""
        create_proguide(user=self.user)
        create_proguide(user=self.user)

        result = self.client.get(PROGUIDES_URL)

        proguides = ProGuide.objects.all().order_by('-id')
        serializer = ProGuideSerializer(proguides, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_proguide_list_limited_to_user(self):
        """test list of proguide is limited to authenticated user"""
        other_user = create_user(
            email='hameddjf01@gmail.com',
            password='12345678',
        )
        create_proguide(user=other_user)
        create_proguide(user=self.user)

        result = self.client.get(PROGUIDES_URL)

        proguides = ProGuide.objects.filter(user=self.user)
        serializer = ProGuideSerializer(proguides, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_get_proguide_detail(self):
        """test get proguide detail"""
        proguide = create_proguide(user=self.user)

        url = detail_url(proguide.id)
        result = self.client.get(url)

        serializer = ProGuideDetailSerializer(proguide)

        self.assertEqual(result.data, serializer.data)

    def test_create_proguide(self):
        """test creating a proguide"""
        payload = {
            'title': 'object num1',
            'time_minutes': 30,
            'price': Decimal('3.41'),
        }
        result = self.client.post(PROGUIDES_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

        # retrieve object with id
        proguide = ProGuide.objects.get(id=result.data['id'])

        # k = key , v = value
        for k, v in payload.items():
            self.assertEqual(getattr(proguide, k), v)
        self.assertEqual(proguide.user, self.user)

    def test_partial_update(self):
        """test partial update of a proguide"""
        original_link = 'http://example.com/proguide.pdf'
        proguide = create_proguide(
            user=self.user,
            title='object num1',
            link=original_link,
        )

        payload = {'title': 'new object title num1'}
        url = detail_url(proguide.id)
        # EXPECTED change the title with patch on url
        result = self.client.patch(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        proguide.refresh_from_db()
        self.assertEqual(proguide.title, payload['title'])
        self.assertEqual(proguide.link, original_link)
        self.assertEqual(proguide.user, self.user)

    def test_full_update(self):
        """test full update of proguide"""
        proguide = create_proguide(
            user=self.user,
            title='object num1',
            link='http://example.com/proguide.pdf',
            description='description of object num1',
        )
        payload = {
            'title': 'new title object num1',
            'link': 'http://example.com/new-proguide.pdf',
            'description': 'new proguide description',
            'time_minutes': 10,
            'price': Decimal('4.12'),
        }

        url = detail_url(proguide.id)
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)

        proguide.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(proguide, k), v)

        self.assertEqual(proguide.user, self.user)

    def test_update_user_returns_error(self):
        """test changing the proguide user result in an error"""
        new_user = create_user(
            email='hameddjf01@gmail.com', password='12345678')

        proguide = create_proguide(user=self.user)
        payload = {'user': new_user.id, }
        url = detail_url(proguide.id)

        self.client.patch(url, payload)
        proguide.refresh_from_db()
        self.assertEqual(proguide.user, self.user)

    def test_delete_proguide(self):
        """test deleting a proguide successful"""
        proguide = create_proguide(user=self.user)

        url = detail_url(proguide.id)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ProGuide.objects.filter(id=proguide.id).exists())

    def test_delete_other_users_proguide_error(self):
        """test trying to delete another users proguide gives error"""
        new_user = create_user(
            email='hameddjf02@gmail.com', password='12345678')
        proguide = create_proguide(user=new_user)

        url = detail_url(proguide.id)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(ProGuide.objects.filter(id=proguide.id).exists())

    def test_create_proguide_with_new_tags(self):
        """test creating a proguide with new tags"""
        payload = {
            'title': 'title num1',
            'time_minutes': 30,
            'price': Decimal('9.21'),
            'tags': [{'name': 'hameddjf01'}, {'name': 'hameddjf02'}]
        }

        result = self.client.post(PROGUIDES_URL, payload, format='json')

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        proguides = ProGuide.objects.filter(user=self.user)
        # check for authenticated user ...bool
        self.assertEqual(proguides.count(), 1)
        # به اولین ایتمی ک برگردونده شده proguides اختصاص دادن
        proguide = proguides[0]
        # counting the tags,must have 2 tags (in payload)
        self.assertEqual(proguide.tags.count(), 2)
        for tag in payload['tags']:
            exists = proguide.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_proguide_with_existing_tags(self):
        """test creating a proguide with existing tag"""
        tag_indian = Tag.objects.create(user=self.user, name='hameddjf33')
        payload = {
            'title': 'object num2',
            'time_minutes': '42',
            'price': Decimal('65.21'),
            'tags': [{'name': 'hameddjf33'}, {'name': 'hameddjf01'}],
        }
        result = self.client.post(PROGUIDES_URL, payload, format='json')
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        proguides = ProGuide.objects.filter(user=self.user)
        self.assertEqual(proguides.count(), 1)
        proguide = proguides[0]
        self.assertEqual(proguide.tags.count(), 2)
        self.assertIn(tag_indian, proguide.tags.all())
        for tag in payload['tags']:
            exists = proguide.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """test creating tag when updating a proguide"""
        proguide = create_proguide(user=self.user)

        payload = {
            'tags': [{'name': 'hameddjf33'}]
        }
        url = detail_url(proguide.id)
        # change (patch) the tags from payload
        result = self.client.patch(url, payload, format='json')

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        # expected get the new tag from Tag (create new tag than get it)
        new_tag = Tag.objects.get(user=self.user, name='hameddjf33')
        # check the new tag for existing in proguide
        self.assertIn(new_tag, proguide.tags.all())

    def test_update_proguide_assign_tag(self):
        """test assigning an existing tag when updating a proguide"""

        tag_me = Tag.objects.create(user=self.user, name='hameddjf33')
        proguide = create_proguide(user=self.user)
        proguide.tags.add(tag_me)

        tag_you = Tag.objects.create(user=self.user, name='hameddjf01')
        payload = {
            'tags': [{'name': 'hameddjf01'}]
        }
        url = detail_url(proguide.id)
        result = self.client.patch(url, payload, format='json')

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertIn(tag_you, proguide.tags.all())
        self.assertNotIn(tag_me, proguide.tags.all())

    def test_clear_proguide_tags(self):
        """test clearing a proguides tags"""
        tag = Tag.objects.create(user=self.user, name='hameddjf33')
        proguide = create_proguide(user=self.user)
        proguide.tags.add(tag)
        payload = {'tags': []}
        url = detail_url(proguide.id)
        result = self.client.patch(url, payload, format='json')

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(proguide.tags.count(), 0)
