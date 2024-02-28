"""
tests dor the user api.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

# از طریق ویوی مورد نظر api ازمایش مسیر
CREATE_USER_URL = reverse('user:create_page')
TOKEN_URL = reverse('user:token_page')
ME_URL = reverse('user:me_page')


def create_user(**params):
    """create and return a new user with get eny detail to params."""
    return get_user_model().objects.create_user(**params)


# درخواست هایی ک احراز هویت نشدن (نیازی به احراز هویت ندارن.)
class PublicUserApiTests(TestCase):
    """test the public features of the user API."""

    # api client ایجاد ی
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """test creating a user is successful."""
        payload = {
            'email': "hameddjf33@gmail.com",
            'password': '12345678',
            'name': 'hamed',
        }
        # برای ایجاد کاربر جدید api ارسال درخواست پوست به
        result = self.client.post(CREATE_USER_URL, payload)

        # api برای ایجاد موفقیت‌آمیز ابجکت بصورت HTTP 201 تأیید کد وضعیت
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

        # بازیابی کاربر بر اساس آدرس ایمیل (ادرس ایمیل باید قبلاً ثبت شده باشد)
        user = get_user_model().objects.get(email=payload['email'])

        # تطابق رمز عبور پیلود با کلمه عبور یوزر و تایید ایجاد موفقیت‌آمیز یوزر
        self.assertTrue(user.check_password(payload['password']))

        # تایید ارسال نکردن رمز عبور یا هش ان به یوزر
        self.assertNotIn('password', result.data)

    def test_user_with_email_exists_error(self):
        """test error return if user with email exists."""
        payload = {
            'email': 'hameddjf33@gmail.com',
            'password': '12345678',
            'name': 'hamed'
        }
        # فراخوانی تابع (ایجاد کاربر جدید) با استفاده از پارامتر های داده شده
        create_user(**payload)
        # برای ایجاد یوزر جدید API ارسال درخواست پوست بوسیله مشخصات یوزر به
        result = self.client.post(CREATE_USER_URL, payload)

        # بررسی وضعیت ناموفق بودن درخواست (کد 400)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """test an error is returnd if password less than 5 chars ."""
        payload = {
            'email': 'hameddjf33@gmail.com',
            'password': '1234',
            'name': 'hamed',
        }
        result = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

        # بررسی میکنه کاربر مورد نظر جدید باشه و بصورت بولین برمیگردونه
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """test generates token for valid credentials."""
        user_details = {
            'email': 'hameddjf33@gmail.com',
            'password': '12345678',
            'name': 'hamed',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        # post the token url and payload for result
        result = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', result.data)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """test returns error iif credentials invalid."""
        create_user(email='hameddjf33@gmail.com', password='12345678')
        payload = {'email': "hameddjf33@gmail.com", "password": "87654321"}
        result = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', result.data)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """test posting a blank password returns an error."""
        payload = {'email': 'hameddjf33@gmail.com', 'password': ''}
        result = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', result.data)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """test authentication is required for users"""
        result = self.client.get(ME_URL)

        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """test api requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='hameddjf33@gmail.com',
            password='12345678',
            name='hameddjf',
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """test retrieving profile for logged in user"""
        result = self.client.get(ME_URL)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_allowe(self):
        """test post is not allowed for the me endpoint"""
        result = self.client.post(ME_URL, {})

        self.assertEqual(result.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """test updating the user profile for the authenticated user"""
        payload = {'name': 'updated hameddjf', 'password': 'new12345678'}

        result = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(result.status_code, status.HTTP_200_OK)
