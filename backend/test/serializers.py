from rest_framework import serializers


class ReservationsSerializer(serializers.Serializer):
    reservationID = serializers.EmailField()
    content = serializers.CharField(max_length=200)
    created = serializers.DateTimeField()
