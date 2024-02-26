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
