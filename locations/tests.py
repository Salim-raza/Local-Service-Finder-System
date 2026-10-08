from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import CustomUser
from .models import District, Division


class LocationUpdateTests(TestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_user(
            email="admin@example.com",
            password="Pass123!",
            first_name="Test",
            last_name="Admin",
            role="ADMIN",
            is_active=True,
        )
        self.division = Division.objects.create(name="Old Division")
        self.district = District.objects.create(
            name="Old District",
            division=self.division,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_admin_can_update_division_and_district(self):
        division_response = self.client.patch(
            f"/api/v1/location/update_division/{self.division.pk}/",
            {"name": "New Division"},
            format="json",
        )
        district_response = self.client.patch(
            f"/api/v1/location/update_district/{self.district.pk}/",
            {"name": "New District"},
            format="json",
        )

        self.assertEqual(division_response.status_code, 200)
        self.assertEqual(district_response.status_code, 200)
        self.division.refresh_from_db()
        self.district.refresh_from_db()
        self.assertEqual(self.division.name, "New Division")
        self.assertEqual(self.district.name, "New District")
