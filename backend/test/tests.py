from django.test import TestCase, Client
from django.db import connection
from django.contrib.auth.hashers import make_password
from datetime import datetime, time
import json
from . import models

# Endpoints
REGISTER       = '/test/registerStudent/'
CREATE_LIBRARY = '/test/createLibrary/'
CREATE_ROOM = '/test/createRoom/'
AVAILABLE_TIMES = '/test/availableTimes/'

# Request Body Fields
CONTENT      = 'content'
CONTENT_TYPE_JSON = 'application/json'
STUDENT_ID   = 'studentId'
EMAIL        = 'email'
PHONE        = 'phone'
PASSWORD     = 'password'
LIBRARY_NAME = "libraryName"
LOCATION     = "location"
ROOM_ID = 'roomId'
ROOM_TYPE = 'roomType'
MIN_CAPACITY = 'minCapacity'
MAX_CAPACITY = 'maxCapacity'
NOISE_LEVEL = 'noiseLevel'
OPEN_HOUR = 'openHour'
OPEN_MINUTE = 'openMinute'
CLOSE_HOUR = 'closeHour'
CLOSE_MINUTE = 'closeMinute'

# Test Data
TEST_STUDENTID = 'abc123'
TEST_PASSWORD = 'password'

TEST_LBRY_NAME = 'my library'

TEST_ROOM_ID = 'EZ103'


class ARLibTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.register_student()
        self.create_library()
        self.create_room()


    def register_student(self):
        email = TEST_STUDENTID + '@nyu.edu'
        data = {
            CONTENT : {
                STUDENT_ID: TEST_STUDENTID,
                EMAIL: email,
                PHONE: '1010101010',
                PASSWORD: TEST_PASSWORD
            }
        }

        response = self.client.post(path=REGISTER, 
                                    data=data, 
                                    content_type=CONTENT_TYPE_JSON)
        my_student = models.Student.objects.get(pk=TEST_STUDENTID)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(my_student is not None)


    def create_library(self):
        data = {
            CONTENT: {
                LIBRARY_NAME: TEST_LBRY_NAME,
                LOCATION: 'manhattan',
                PHONE: '0101010101'
            }
        }

        response = self.client.post(path=CREATE_LIBRARY, 
                                    data=data, 
                                    content_type=CONTENT_TYPE_JSON)
        my_library = models.Library.objects.get(pk=TEST_LBRY_NAME)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(my_library is not None)


    def create_room(self):
        data = {
            CONTENT: {
                ROOM_ID: TEST_ROOM_ID,
                LIBRARY_NAME: TEST_LBRY_NAME,
                ROOM_TYPE: 'study',
                MIN_CAPACITY: 2,
                MAX_CAPACITY: 8,
                NOISE_LEVEL: 2,
                OPEN_HOUR: 8,
                OPEN_MINUTE: 0,
                CLOSE_HOUR: 20,
                CLOSE_MINUTE: 0
            }
        }

        response = self.client.post(path=CREATE_ROOM, 
                                    data=data, 
                                    content_type=CONTENT_TYPE_JSON)
        my_room = models.Room.objects.get(pk=TEST_ROOM_ID)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(my_room is not None)

    def test_db_connection(self):
        self.assertTrue(connection is not None)

class AvailableTimesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.library = models.Library.objects.create(
            libraryName=TEST_LBRY_NAME,
            location='Manhattan',
            phone='0101010101',
        )
        self.room = models.Room.objects.create(
            roomId=TEST_ROOM_ID,
            libraryName=self.library,
            roomType='study',
            minCapacity=2,
            maxCapacity=8,
            noiseLevel=2,
            openTime=time(8, 0),
            closeTime=time(20, 0),
        )
        self.room2 = models.Room.objects.create(
            roomId='OTHER123',
            libraryName=self.library,
            roomType='study',
            minCapacity=2,
            maxCapacity=8,
            noiseLevel=2,
            openTime=time(8, 0),
            closeTime=time(20, 0),
        )
        self.student = models.Student.objects.create(
            studentId='abc123',
            email='student@example.com',
            password=make_password('password'),
            phone='0101010101',
        )
        self.reservation = models.Reservations.objects.create(
            roomId=self.room,
            studentId=self.student,
            date=datetime(2024, 1, 1).date(),
            startTime=time(10, 0),
            endTime=time(12, 0),
        )
        self.reservation2 = models.Reservations.objects.create(
            roomId=self.room,
            studentId=self.student,
            date=datetime(2024, 1, 1).date(),
            startTime=time(12, 0),
            endTime=time(14, 0),
        )
        self.reservation3 = models.Reservations.objects.create(
            roomId=self.room,
            studentId=self.student,
            date=datetime(2024, 1, 1).date(),
            startTime=time(17, 0),
            endTime=time(20, 0),
        )
        self.reservation4 = models.Reservations.objects.create(
            roomId=self.room2,
            studentId=self.student,
            date=datetime(2024, 1, 1).date(),
            startTime=time(8, 0),
            endTime=time(10, 0),
        )
        self.reservation5 = models.Reservations.objects.create(
            roomId=self.room2,
            studentId=self.student,
            date=datetime.now().date(),
            startTime=time(8, 0),
            endTime=time(10, 0),
        ) 

    def test_available_times(self):
        response = self.client.get(path=(AVAILABLE_TIMES + TEST_ROOM_ID + '/2024-01-01/'))
        self.assertEqual(response.status_code, 200)
        print(response.data)
        self.assertEqual(response.data, [(time(8, 0), time(10, 0)), (time(14, 0), time(17, 0))])
    
    def test_create_reservations(self):
        url = '/test/createReservation/'
        date = datetime.now().date().isoformat()
        data = {
            'content': {
                'studentId': TEST_STUDENTID,
                'roomId': TEST_ROOM_ID,
                'date': date,
                'startHour': 11,
                'startMinute': 0,
                'endHour': 11,
                'endMinute': 30
            }
        }

        response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200, "Response status code should be 200.")

        reservations = models.Reservations.objects.filter(roomId=TEST_ROOM_ID, date=date)
        self.assertEqual(len(reservations), 1, "Exactly one reservation should be created.")

        reservation = reservations[0]
        self.assertEqual(reservation.roomId.roomId, TEST_ROOM_ID, "The room ID should match.")
        self.assertEqual(reservation.studentId.studentId, TEST_STUDENTID, "The student ID should match.")
        self.assertEqual(reservation.date.strftime('%Y-%m-%d'), date, "The date should match the requested date.")
        self.assertEqual(reservation.startTime, time(11, 0), "The start time should be 11:00.")
        self.assertEqual(reservation.endTime, time(11, 30), "The end time should be 11:30.")

        # Try to create a reservation that overlaps but with a different room
        data['content']['roomId'] = 'OTHER123'
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200, "Response status code should be 200.")

        # Try to create a reservation that overlaps in time
        data['content']['roomId'] = TEST_ROOM_ID
        data['content']['startHour'] = 10
        data['content']['startMinute'] = 15
        data['content']['endHour'] = 11
        data['content']['endMinute'] = 45

        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400, "Response status code should be 400.")

        # Try to create a reservation that is past the room closing time
        data['content']['startHour'] = 20
        data['content']['startMinute'] = 15
        data['content']['endHour'] = 21
        data['content']['endMinute'] = 45

        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400, "Response status code should be 400.")

        # Try to create a reservation that is right after our original reservation
        data['content']['startHour'] = 11
        data['content']['startMinute'] = 30
        data['content']['endHour'] = 12
        data['content']['endMinute'] = 0

        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200, "Response status code should be 200.")
