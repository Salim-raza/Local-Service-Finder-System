from datetime import date, time
from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import CustomUser
from categories.models import Category
from service.models import Service
from .models import Booking


class BookingWorkflowTests(TestCase):
    def setUp(self):
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
        )
        self.other_provider = CustomUser.objects.create_user(
            email="other-provider@example.com",
            password="Pass123!",
            first_name="Other",
            last_name="Provider",
            role="SERVICE_PROVIDER",
            is_active=True,
        )
        category = Category.objects.create(user=self.provider, name="Repairs")
        self.service = Service.objects.create(
            provider=self.provider,
            category=category,
            name="Repair",
            image="repair.jpg",
            our_base_price="25.00",
        )
        self.other_service = Service.objects.create(
            provider=self.other_provider,
            category=category,
            name="Other repair",
            image="other-repair.jpg",
            our_base_price="30.00",
        )
        self.booking = self.create_booking(self.service)
        self.client = APIClient()

    def create_booking(self, service, status=Booking.Status.PENDING):
        return Booking.objects.create(
            user=self.customer,
            service=service,
            booking_date=date(2026, 11, 1),
            booking_time=time(10, 30),
            status=status,
        )

    def provider_url(self, action, booking):
        return f"/api/v1/dashboard/service_provider/{action}/{booking.pk}/"

    def test_customer_can_update_booking_date(self):
        self.client.force_authenticate(self.customer)

        response = self.client.patch(
            f"/api/v1/booking/booking_update/{self.booking.pk}/",
            {"booking_date": "2026-11-02"},
            format="multipart",
        )

        self.assertEqual(response.status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.booking_date, date(2026, 11, 2))

    def test_customer_can_cancel_pending_booking(self):
        self.client.force_authenticate(self.customer)

        response = self.client.post(
            f"/api/v1/booking/cancel_booking/{self.booking.pk}/",
            {"cancellation_reason": "Plans changed"},
            format="multipart",
        )

        self.assertEqual(response.status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, Booking.Status.CANCELLED)
        self.assertEqual(self.booking.cancelled_by, self.customer)
        self.assertIsNotNone(self.booking.cancelled_at)

    @patch("dashboard.views.service_provider_dashboard.send_mail")
    def test_provider_can_accept_own_booking_only(self, send_mail):
        self.client.force_authenticate(self.provider)

        forbidden_booking = self.create_booking(self.other_service)
        response = self.client.post(
            self.provider_url("accept_booking", forbidden_booking)
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(forbidden_booking.status, Booking.Status.PENDING)

        response = self.client.post(
            self.provider_url("accept_booking", self.booking)
        )
        self.assertEqual(response.status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, Booking.Status.ACCEPTED)
        send_mail.assert_called_once()

    @patch("dashboard.views.service_provider_dashboard.send_mail")
    def test_provider_can_reject_own_booking(self, send_mail):
        self.client.force_authenticate(self.provider)

        response = self.client.post(
            self.provider_url("reject_booking", self.booking)
        )

        self.assertEqual(response.status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, Booking.Status.REJECTED)
        send_mail.assert_called_once()

    def test_provider_can_complete_accepted_booking(self):
        self.client.force_authenticate(self.provider)
        accepted_booking = self.create_booking(
            self.service,
            status=Booking.Status.ACCEPTED,
        )

        response = self.client.post(
            self.provider_url("complete_booking", accepted_booking)
        )

        self.assertEqual(response.status_code, 200)
        accepted_booking.refresh_from_db()
        self.assertEqual(accepted_booking.status, Booking.Status.COMPLETED)
        self.assertIsNotNone(accepted_booking.completed_time)

    def test_accepted_booking_list_uses_accepted_status(self):
        self.client.force_authenticate(self.provider)
        accepted_booking = self.create_booking(
            self.service,
            status=Booking.Status.ACCEPTED,
        )

        response = self.client.get(
            "/api/v1/dashboard/service_provider/get_accept_booking/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["id"] for item in response.data["data"]],
            [accepted_booking.pk],
        )
