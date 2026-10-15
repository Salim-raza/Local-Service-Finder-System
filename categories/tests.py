from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import CustomUser
from categories.models import Category


class CategoryApiTests(TestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_user(
            email="admin@example.com",
            password="test-password",
            first_name="Test",
            last_name="Admin",
            role="ADMIN",
            is_active=True,
        )
        self.customer = CustomUser.objects.create_user(
            email="customer@example.com",
            password="test-password",
            first_name="Test",
            last_name="Customer",
            role="CUSTOMER",
            is_active=True,
        )
        self.category = Category.objects.create(user=self.admin, name="Repairs")
        self.client = APIClient()

    def test_category_list_is_public(self):
        response = self.client.get("/api/v1/categories/all_category/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["name"], "Repairs")

    def test_customer_cannot_create_category(self):
        self.client.force_authenticate(self.customer)

        response = self.client.post(
            "/api/v1/categories/create_category/",
            {"name": "Cleaning"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Category.objects.filter(name="Cleaning").exists())

    def test_admin_can_create_category(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            "/api/v1/categories/create_category/",
            {"name": "Cleaning"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["category"]["name"], "Cleaning")
        self.assertTrue(
            Category.objects.filter(name="Cleaning", user=self.admin).exists()
        )

    def test_category_names_are_unique_without_case_sensitivity(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            "/api/v1/categories/create_category/",
            {"name": "repairs"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Category.objects.count(), 1)

    def test_update_rejects_case_insensitive_duplicate_but_allows_same_name(self):
        other_category = Category.objects.create(
            user=self.admin,
            name="Cleaning",
        )
        self.client.force_authenticate(self.admin)
        url = f"/api/v1/categories/category_modify/{self.category.pk}/"

        duplicate_response = self.client.patch(
            url,
            {"name": "cleaning"},
            format="json",
        )
        unchanged_response = self.client.patch(
            url,
            {"name": "REPAIRS"},
            format="json",
        )

        self.assertEqual(duplicate_response.status_code, 400)
        self.assertEqual(unchanged_response.status_code, 200)
        self.assertEqual(
            Category.objects.get(pk=self.category.pk).name,
            "REPAIRS",
        )
        self.assertTrue(Category.objects.filter(pk=other_category.pk).exists())

    def test_customer_cannot_modify_category(self):
        self.client.force_authenticate(self.customer)

        response = self.client.patch(
            f"/api/v1/categories/category_modify/{self.category.pk}/",
            {"name": "New name"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Repairs")

    def test_admin_can_delete_category(self):
        self.client.force_authenticate(self.admin)

        response = self.client.delete(
            f"/api/v1/categories/category_modify/{self.category.pk}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Category.objects.filter(pk=self.category.pk).exists())

    def test_search_requires_a_non_empty_query(self):
        missing_response = self.client.get(
            "/api/v1/categories/category_search/"
        )
        blank_response = self.client.get(
            "/api/v1/categories/category_search/?search=%20%20"
        )

        self.assertEqual(missing_response.status_code, 400)
        self.assertEqual(blank_response.status_code, 400)

    def test_search_returns_matching_categories(self):
        response = self.client.get(
            "/api/v1/categories/category_search/?search=pair"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [category["name"] for category in response.data["category"]],
            ["Repairs"],
        )
