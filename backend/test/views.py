import json
from django.http import Http404
from django.shortcuts import render
from django.db.utils import IntegrityError
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from rest_framework.decorators import api_view
from . import models
from .utils.fcns import *
from datetime import datetime, date, time
import random

# Create your views here.

@api_view(['POST'])
def create_library(request):
    """
    Requires libraryName, location, phone in request body
    """
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    content = body['content']
    print(f'{content=}')

    models.Library.objects.create(
        libraryName=content["libraryName"],
        location=content["location"],
        phone=content["phone"]
    )

    return Response()

@api_view(['POST'])
def create_room(request):
    """
    Requires roomId, libraryName, roomType, minCapacity, maxCapacity
    noiseLevel, openHour, openMinute, closeHour, closeMinute
    in request body 
    """
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    content = body['content']
    print(f'{content=}')

    try:
        library = models.Library.objects.get(pk=content['libraryName'])
        openTime = time(content["openHour"], content["openMinute"])
        closeTime = time(content["closeHour"], content["closeMinute"])
        models.Room.objects.create(
            roomId=content['roomId'],
            libraryName=library,
            roomType=content["roomType"],
            minCapacity=content["minCapacity"],
            maxCapacity=content["maxCapacity"],
            noiseLevel=content["noiseLevel"],
            openTime=openTime,
            closeTime=closeTime,
        )
    except models.Library.DoesNotExist as ex:
        raise ex

    return Response()

@api_view(['POST'])
def register_student(request):
    """
    Requires studentId, email, phone, password in request body
    """
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    content = body['content']
    print(f'{content=}')

    models.Student.objects.create(
        studentId=content["studentId"],
        email=content["email"],
        phone=content["phone"],
        password=content["password"]
    )

    return Response()

@api_view(['POST'])
def login_student(request):
    """
    Requires studentId, password in request body
    """
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    content = body['content']
    print(f'{content=}')

    try:
        student = models.Student.objects.get(pk=content['studentId'])
        if not check_password(content['password'], student.password):
            raise ValueError("Invalid password")
    except models.Student.DoesNotExist as ex:
        raise ex

    # Set session with studentId
    request.session['studentId'] = student.studentId
    return Response()

@api_view(['POST'])
def logout_student(request):
    if 'studentId' in request.session:
        del request.session['studentId']
    return Response()

@api_view(['POST'])
def create_reservation(request):
  
    """
    Requires roomId, libraryName, room_type, minCapacity, maxCapacity
    noiseLevel, date, startHour, endHour, startMinute, endMinute
    in request body
    """
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    content = body['content']
    print(f'{content=}')

    try:
        student = models.Student.objects.get(pk=content['studentId'])
        print(f'{student}')
        room = models.Room.objects.get(roomId=content['roomId'])
        print(f'{room=}')
        library = models.Library.objects.get(libraryName=content['libraryName'])
        print(f'{library=}')
    except models.Student.DoesNotExist as ex:
        raise ex
    except models.Room.DoesNotExist as ex:
        raise ex
    except models.Library.DoesNotExist as ex:
        raise ex

    year, month, day = [int(x) for x in content['date'].split('-')]
    date_dt = date(year, month, day)
    startTime = time(content["startHour"], content["startMinute"])
    endTime = time(content["endHour"], content["endMinute"])
    if date_dt < date.today() or \
        date_dt == date.today and startTime < datetime.now().time():
        raise ValueError("Requested date is already past")
    
     # Use available_times to check the availability
    available_slots = get_available_times(content['roomId'], date_dt.strftime('%Y-%m-%d'))
    is_time_available = any(startTime >= slot[0] and endTime <= slot[1] for slot in available_slots)

    if not is_time_available:
        return Response({"error": "No available slots for the requested time range"}, status=400)

    # Create reservation if the time slot is available
    models.Reservations.objects.create(
        studentId=student,
        roomId=room,
        date=date_dt,
 	    startTime=startTime,
        endTime=endTime
    )    

    return Response()

@api_view(['DELETE'])
def delete_reservation(request):
    # TODO: rewrite this completely
    """
    Requires date, startHour, endHour, startMinute, endMinute, and studentId
    in request body 
    """
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    content = body['content']
    print(f'{content=}')

    try:
        student = models.Student.objects.get(pk=content['studentId'])
        print(f'{student}')
    except models.Student.DoesNotExist as ex:
        raise ex
    
    year, month, day = [int(x) for x in content['date'].split('-')]
    date_dt = date(year, month, day)
    startTime = time(content["startHour"], content["startMinute"])
    endTime = time(content["endHour"], content["endMinute"])

    reservations = list(models.Reservations.objects.filter(
        studentId=content['studentId'],
        date=date_dt,
        startTime=startTime,
        endTime=endTime))
    
    if len(reservations) != 1:
        raise ValueError("Section does not exist")

    leftStart = reservations[0].startTime
    rightEnd = reservations[0].endTime
    roomId = reservations[0].roomId
    libraryName = reservations[0].libraryName
    print(leftStart, rightEnd, date_dt, roomId, libraryName)

    left_reservations = list(models.Reservations.objects.filter(
        studentId=None,
        date=date_dt,
        endTime=leftStart,
        roomId=roomId,
        libraryName=libraryName,
    ))
    right_reservations = list(models.Reservations.objects.filter(
        studentId=None,
        date=date_dt,
        startTime=rightEnd,
        roomId=roomId,
        libraryName=libraryName,
    ))
    print(left_reservations, right_reservations)

    if len(left_reservations) == 1:
        reservations[0].startTime = left_reservations[0].startTime
        left_reservations[0].delete()
    if len(right_reservations) == 1:
        reservations[0].endTime = right_reservations[0].endTime
        right_reservations[0].delete()
    
    reservations[0].studentId = None
    reservations[0].save()

    return Response()

@api_view(['GET'])
def check_room_availability(request, roomId):
    # TODO: use helper function for retrieving results (rewrite this)
    reservations = list(models.Reservations.objects
                        .filter(roomId=roomId, studentId=UNAVAILABLE)
                        .values('date', 'startTime', 'endTime'))
    
    resp = {'availableTimes': reservations}
    return Response(resp)

@api_view(['GET'])
def get_all_rooms(request):
    rooms = models.Room.objects.all().values()
    return Response(rooms)

@api_view(['GET'])
def get_available_rooms(request, start_time, end_time):
    """
    returns a QuerySet of rooms that are not booked within
    a specified start and end time
    
    !date must be formatted as year-month-day
    """
    start_time = datetime.strptime(start_time_str, "%H:%M").time()
    end_time = datetime.strptime(end_time_str, "%H:%M").time()

    year, month, day = [int(x) for x in content['date'].split('-')]
    rsrvDate = date(year, month, day)

    """
    conditions checked to determine if a room is unavailable:
      the reservation starts within [start_time, end_time]
      the reservation ends within [start_time, end_time]
      the reservations starts before start_time and ends after end_time
    """
    unavailable = models.Reservations.objects.filter(
        Q(  Q(startTime__gte = start_time, startTime__lte = end_time) 
            | Q(endTime__gte = start_time, endTime__lte = end_time)
            | Q(startTime__lte = start_time, endTime__gte = end_time)
        ),
        date=rsrvDate
    ).values_list('roomId', flat=True)

    available = models.Room.objects.all().exclude(roomId__in=unavailable)

    return Response(available)

@api_view(['GET'])
def get_reservations_for_student_in_time_range(request, start_time, end_time):
    if 'studentId' not in request.session:
        raise ValueError("Not logged in")
    # TODO rewrite this
    dt_start=dt_end=None
    try:
        dt_start=datetime.strptime(start_time,"%Y-%m-%dT%H:%M:%S")
        dt_end=datetime.strptime(end_time,"%Y-%m-%dT%H:%M:%S")
    except:
        raise ValueError("Invalid datetime format")
    if dt_start>=dt_end:
        raise ValueError("Start date & time must come before end date & time")
    res=models.Reservations.objects.filter(
        studentId=request.session['studentId'],
        date__gte=dt_start,
        date__lte=dt_end,
        startTime__gte=dt_start,
        endTime__lte=dt_end,
    ).values()
    return Response(res)

@api_view(['GET'])
def get_all_reservations_for_a_student(request):
    if 'studentId' not in request.session:
        raise ValueError("Not logged in")
    reservations = models.Reservations.objects.filter(studentId=request.session['studentId']).values()
    return Response(reservations)

@api_view(['GET'])
def get_all_reservations(request):
    res = models.Reservations.objects.all().values()
    return Response(res)

@api_view(['GET'])
def get_reservations_in_time_range(request):
    # TODO rewrite this
    """
    Requires start_time, end_time in request body
    """
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    content = body['content']
    print(f'{content=}')

    dt_start=dt_end=None
    try:
        dt_start=datetime.strptime(start_time,"%Y-%m-%dT%H:%M:%S")
        dt_end=datetime.strptime(end_time,"%Y-%m-%dT%H:%M:%S")
    except:
        raise ValueError("Invalid datetime format")
    if dt_start>=dt_end:
        raise ValueError("Start date & time must come before end date & time")
    res=models.Reservations.objects.filter(
        studentId__isnull=False,
        date__gte=dt_start,
        date__lte=dt_end,
        startTime__gte=dt_start,
        endTime__lte=dt_end,
    ).values()
    return Response(res)

@api_view(['GET'])
def available_times(request, roomId, date_str):
    """
    API endpoint that returns the times when a room is available.
    """
    try:
        available_times = get_available_times(roomId, date_str)
        return Response(available_times)
    except models.Room.DoesNotExist:
        raise Http404("Room not found")
    except ValueError as e:
        return Response({'error': str(e)}, status=400)

@api_view(['DELETE'])
def clear_expired_time_slots(request):
    dtobj=datetime.now()
    today=dtobj.date()
    rightnow=dtobj.time()
    expiredres=models.Reservations.objects.filter(
        date__lte=today,
        endTime__lte=rightnow,
    )
    for res in expiredres:
        res.delete()
    return Response({'message':'Expired time slots have been cleared'})

@api_view(['GET'])
def get_all_libraries(request):
    libs=models.Library.objects.all().values()
    return Response(libs)


@api_view(['GET'])
def get_all_rooms_for_library(request,libraryName):
    match=models.Room.objects.filter(libraryName=libraryName).values()
    return Response(match)


@api_view(['GET'])
def get_all_students(request):
    students=models.Student.objects.all().values()
    return Response(students)

def get_available_times(room_id, date_str): 
    """
    returns the times that a room is available
    """
    open = []

    # parse date from parameter
    year, month, day = [int(x) for x in date_str.split('-')]
    date_obj = date(year, month, day)

    # get opening and closing time of room
    my_room = models.Room.objects.get(pk=room_id)
    open = [(my_room.openTime, my_room.closeTime)]

    # get all reservations where room and date match
    reservations = models.Reservations.objects.filter(
        roomId=room_id,
        date=date_obj)

    # iterate through reservations
    for res in reservations:
        for i in range(len(open)):
            if res.startTime >= open[i][0] and res.startTime <= open[i][1]:
                # split open time range into two ranges
                if open[i][0] < res.startTime:
                    open.insert(i, (open[i][0], res.startTime))
                    i += 1
                if open[i][1] > res.endTime:
                    open.insert(i, (res.endTime, open[i][1]))
                    i += 1
                open.pop(i)
                break

    return open