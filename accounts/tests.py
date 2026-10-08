from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .models import CustomUser, OTP


class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="reset@example.com",
            password="OldPass123!",
            first_name="Reset",
            last_name="User",
            role="CUSTOMER",
            is_active=True,
        )
        self.client = APIClient()

    def create_otp(self, created_at):
        otp = OTP.objects.create(user=self.user, otp="1234")
        OTP.objects.filter(pk=otp.pk).update(create_at=created_at)
        return otp

    def test_valid_otp_resets_password_and_is_consumed(self):
        otp = self.create_otp(timezone.now())

        response = self.client.post(
            "/api/v1/accounts/reset_password/",
            {
                "email": self.user.email,
                "otp": "1234",
                "new_password": "NewPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPass123!"))
        self.assertFalse(OTP.objects.filter(pk=otp.pk).exists())

    def test_expired_otp_does_not_reset_password(self):
        self.create_otp(timezone.now() - timedelta(minutes=10))

        response = self.client.post(
            "/api/v1/accounts/reset_password/",
            {
                "email": self.user.email,
                "otp": "1234",
                "new_password": "NewPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("OldPass123!"))
