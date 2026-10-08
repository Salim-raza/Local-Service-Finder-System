from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import CustomUser
from categories.models import Category
from .models import Service


class ServiceAccessTests(TestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_user(
            email="admin@example.com",
            password="Pass123!",
            first_name="Test",
            last_name="Admin",
            role="ADMIN",
            is_active=True,
        )
        self.provider = CustomUser.objects.create_user(
            email="provider@example.com",
            password="Pass123!",
            first_name="Test",
            last_name="Provider",
            role="SERVICE_PROVIDER",
            is_active=True,
        )
        self.other_provider = CustomUser.objects.create_user(
            email="other-provider@example.com",
            password="Pass123!",
            first_name="Other",
            last_name="Provider",
            role="SERVICE_PROVIDER",
            is_active=True,
        )
        self.customer = CustomUser.objects.create_user(
            email="customer@example.com",
            password="Pass123!",
            first_name="Test",
            last_name="Customer",
            role="CUSTOMER",
            is_active=True,
        )
        category = Category.objects.create(user=self.admin, name="Repairs")
        self.provider_service = self.create_service(self.provider, category, "Provider service")
        self.other_service = self.create_service(self.other_provider, category, "Other service")
        self.client = APIClient()

    def create_service(self, provider, category, name):
        return Service.objects.create(
            provider=provider,
            category=category,
            name=name,
            image="service.jpg",
            our_base_price="25.00",
        )

    def service_url(self, service):
        return f"/api/v1/service/service_modify/{service.pk}/"

    def test_customer_cannot_modify_service(self):
        self.client.force_authenticate(self.customer)

        response = self.client.delete(self.service_url(self.provider_service))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Service.objects.filter(pk=self.provider_service.pk).exists())

    def test_provider_can_modify_only_own_service(self):
        self.client.force_authenticate(self.provider)

        forbidden_response = self.client.delete(self.service_url(self.other_service))
        allowed_response = self.client.delete(self.service_url(self.provider_service))

        self.assertEqual(forbidden_response.status_code, 404)
        self.assertEqual(allowed_response.status_code, 200)
        self.assertFalse(Service.objects.filter(pk=self.provider_service.pk).exists())
        self.assertTrue(Service.objects.filter(pk=self.other_service.pk).exists())

    def test_admin_can_delete_provider_service(self):
        self.client.force_authenticate(self.admin)

        response = self.client.delete(self.service_url(self.provider_service))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Service.objects.filter(pk=self.provider_service.pk).exists())
