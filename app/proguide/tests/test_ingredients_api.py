"""test for the ingredients api"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from proguide.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('proguide:ingredient-list')


def detail_url(ingredient_id):
    """create and return an ingredient detail url"""
    return reverse('proguide:ingredient-detail', args=[ingredient_id])


def create_user(email='hameddjf33@gmail.com', password='12345678'):
    """create and return user"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientsApiTests(TestCase):
    """test unauthenticated api requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """test auth is required for retrieving ingredients"""
        result = self.client.get(INGREDIENTS_URL)

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """test unauthenticated api requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='hameddjf33')
        Ingredient.objects.create(user=self.user, name='hameddjf01')

        result = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """test list of ingredients is limited to authenticated user"""
        # create unauthenticated user
        user2 = create_user(email='hameddjf02@gmail.com', )
        # create ingredient for user2
        Ingredient.objects.create(user=user2, name='paper')
        # create ingredient for authenticated user
        ingredient = Ingredient.objects.create(
            user=self.user, name='pen')
        # get all ingredients list for authenticated user
        result = self.client.get(INGREDIENTS_URL)

        # status test
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        # check len result is 1 to authenticated user(we created 2 ingredient)
        self.assertEqual(len(result.data), 1)
        # check name ingredient for first object & return name of ingredient
        self.assertEqual(result.data[0]['name'], ingredient.name)
        # check id ingredient for first object & return id of ingredient
        self.assertEqual(result.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """test updating an ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='paper')

        # rename paper to book
        payload = {'name': 'book'}
        # creating url with ingredient id
        url = detail_url(ingredient.id)
        # اعمال کردنشون
        result = self.client.patch(url, payload)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        # check tha name in database (is name in payload)
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """test deleting an ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='pen')

        url = detail_url(ingredient.id)
        # delete url ingredient id
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        # retrieve ingredient objects for user & ..
        ingredients = Ingredient.objects.filter(user=self.user)
        # expected no ingredient
        self.assertFalse(ingredients.exists())
