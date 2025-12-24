from __future__ import annotations

from datetime import date

from django.core.exceptions import ValidationError
from django.db import models


class Room(models.Model):
    class RoomStatus(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        OCCUPIED = 'occupied', 'Occupied'
        MAINTENANCE = 'maintenance', 'Maintenance'

    number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=RoomStatus.choices,
        default=RoomStatus.AVAILABLE,
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['number']

    def __str__(self) -> str:
        return f"Room {self.number}"

    def is_available(self, start: date, end: date) -> bool:
        return not self.bookings.filter(
            status__in=Booking.ACTIVE_STATUSES,
            check_in__lt=end,
            check_out__gt=start,
        ).exists()


class Guest(models.Model):
    full_name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self) -> str:
        return self.full_name


class Booking(models.Model):
    class BookingStatus(models.TextChoices):
        RESERVED = 'reserved', 'Reserved'
        CHECKED_IN = 'checked_in', 'Checked In'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    ACTIVE_STATUSES = {BookingStatus.RESERVED, BookingStatus.CHECKED_IN}

    room = models.ForeignKey(Room, related_name='bookings', on_delete=models.CASCADE)
    guest = models.ForeignKey(Guest, related_name='bookings', on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.RESERVED,
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-check_in', '-created_at']

    def __str__(self) -> str:
        return f"Booking for {self.room} ({self.check_in} - {self.check_out})"

    def clean(self) -> None:
        if self.check_out <= self.check_in:
            raise ValidationError('Check-out date must be after check-in date.')

        overlapping = Booking.objects.filter(
            room=self.room,
            status__in=self.ACTIVE_STATUSES,
            check_in__lt=self.check_out,
            check_out__gt=self.check_in,
        ).exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError('Room is not available for the selected dates.')

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.total_price:
            duration = (self.check_out - self.check_in).days
            self.total_price = duration * self.room.price
        super().save(*args, **kwargs)


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name
