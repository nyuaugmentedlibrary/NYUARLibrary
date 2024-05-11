def generateReservationId():
    resId = random.randint(0, MAX_RESERVATION_ID)
    try:
        while True:
            models.Reservations.objects.get(reservationId=resId)
            resId = random.randint(0, MAX_RESERVATION_ID)
    except models.Reservations.DoesNotExist:
        return resId
