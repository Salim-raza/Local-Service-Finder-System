from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import CustomUser


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_user(
            email="admin@example.com",
            password="Pass123!",
            first_name="Test",
            last_name="Admin",
            role="ADMIN",
            is_active=True,
            is_approved=True,
        )
        self.customer = CustomUser.objects.create_user(
            email="customer@example.com",
            password="Pass123!",
            first_name="Test",
            last_name="Customer",
            role="CUSTOMER",
            is_active=True,
        )
        self.provider = CustomUser.objects.create_user(
            email="provider@example.com",
            password="Pass123!",
            first_name="Test",
            last_name="Provider",
            role="SERVICE_PROVIDER",
            is_active=True,
            is_approved=True,
        )
        self.client = APIClient()

    def test_dashboard_greeting_endpoints_require_matching_roles(self):
        dashboard_urls = (
            ("/api/v1/dashboard/admin/admin/", self.admin, self.customer),
            ("/api/v1/dashboard/customer/customer/", self.customer, self.admin),
            (
                "/api/v1/dashboard/service_provider/service_provide/",
                self.provider,
                self.customer,
            ),
        )

        for url, allowed_user, denied_user in dashboard_urls:
            with self.subTest(url=url, role="allowed"):
                self.client.force_authenticate(allowed_user)
                self.assertEqual(self.client.get(url).status_code, 200)
            with self.subTest(url=url, role="denied"):
                self.client.force_authenticate(denied_user)
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_active_provider_count_uses_user_approval_fields(self):
        self.client.force_authenticate(self.admin)

        response = self.client.get(
            "/api/v1/dashboard/admin/total_activate_account_count/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, 1)
