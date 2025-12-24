from rest_framework import serializers

from .models import Booking, Guest, Room, Service


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'number', 'room_type', 'capacity', 'price', 'status', 'description']


class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['id', 'full_name', 'email', 'phone_number']


class BookingSerializer(serializers.ModelSerializer):
    room_detail = RoomSerializer(source='room', read_only=True)
    guest_detail = GuestSerializer(source='guest', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'room',
            'guest',
            'check_in',
            'check_out',
            'status',
            'total_price',
            'notes',
            'room_detail',
            'guest_detail',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ('total_price', 'created_at', 'updated_at')


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'price', 'is_active']
