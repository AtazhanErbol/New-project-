import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Master, Service, TimeSlot, Booking


def _make_slot(master, when, is_booked=False):
    return TimeSlot.objects.create(date=when.date(), time=when.time(), master=master, is_booked=is_booked)


class SubmitBookingTests(TestCase):
    def setUp(self):
        self.master = Master.objects.create(name='Айгерим', is_active=True)
        self.service = Service.objects.create(
            name='Маникюр', category='manicure', description='-',
            duration_minutes=60, price_from=5000,
        )
        self.future = timezone.localtime() + datetime.timedelta(days=1)

    def _post(self, slot, **overrides):
        data = {
            'service': self.service.id,
            'client_name': 'Клиент',
            'client_phone': '+77001234567',
            'client_email': 'client@example.com',
            'comment': '',
            'consent': 'on',
            'slot_id': slot.id,
            'master_id': self.master.id,
        }
        data.update(overrides)
        return self.client.post(reverse('booking:submit'), data)

    def test_double_booking_of_same_slot_is_rejected(self):
        slot = _make_slot(self.master, self.future)
        self._post(slot)
        slot.refresh_from_db()
        self.assertTrue(slot.is_booked)
        self.assertEqual(Booking.objects.count(), 1)

        response = self._post(slot)
        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(response.status_code, 302)

    def test_cannot_book_a_past_slot(self):
        past = timezone.localtime() - datetime.timedelta(hours=1)
        slot = _make_slot(self.master, past)
        self._post(slot)
        slot.refresh_from_db()
        self.assertFalse(slot.is_booked)
        self.assertEqual(Booking.objects.count(), 0)

    def test_cannot_book_service_master_does_not_offer(self):
        other_master = Master.objects.create(name='Жанна', is_active=True)
        self.service.masters.add(other_master)  # service is restricted to other_master only
        slot = _make_slot(self.master, self.future)
        self._post(slot)
        slot.refresh_from_db()
        self.assertFalse(slot.is_booked)
        self.assertEqual(Booking.objects.count(), 0)

    def test_consent_is_required(self):
        slot = _make_slot(self.master, self.future)
        self._post(slot, consent='')
        self.assertEqual(Booking.objects.count(), 0)


class MasterDeletionTests(TestCase):
    def test_deleting_master_keeps_booking_history(self):
        master = Master.objects.create(name='Айгерим', is_active=True)
        service = Service.objects.create(
            name='Педикюр', category='pedicure', description='-',
            duration_minutes=60, price_from=7000,
        )
        slot = _make_slot(master, timezone.localtime() + datetime.timedelta(days=1), is_booked=True)
        booking = Booking.objects.create(
            service=service, master=master, slot=slot,
            client_name='Клиент', client_phone='+77001234567', client_email='client@example.com',
        )

        master.delete()

        booking.refresh_from_db()
        slot.refresh_from_db()
        self.assertIsNone(booking.master)
        self.assertIsNone(slot.master)
        self.assertTrue(Booking.objects.filter(id=booking.id).exists())
