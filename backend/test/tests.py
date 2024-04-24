from django.test import TestCase, Client
from django.db import connection
from django.contrib.auth.hashers import make_password
from datetime import datetime, time
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

    def test_available_times(self):
        response = self.client.get(path=(AVAILABLE_TIMES + TEST_ROOM_ID + '/2024-01-01/'))
        self.assertEqual(response.status_code, 200)
        print(response.data)
        self.assertEqual(response.data, [(time(8, 0), time(10, 0)), (time(14, 0), time(17, 0))])
    


class RoomsGetMethodTest(TestCase):
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
            minCapacity=1,
            maxCapacity=1,
            noiseLevel=2,
            openTime=time(8, 0),
            closeTime=time(20, 0),
        )
        self.student = models.Student.objects.create(
            studentId='test-stu1',
            email='student@example.com',
            password=make_password('password'),
            phone='0101010101',
        )
        self.reservation = models.Reservations.objects.create(
            roomId=self.room,
            studentId=self.student,
            date=datetime(2024, 1, 1).date(),
            startTime=time(8, 0),
            endTime=time(10, 0),
        )
    
    def test_get_all_rooms(self):
        response = self.client.get(path=('/test/getAllRooms/'),content_type=CONTENT_TYPE_JSON)
        self.assertEqual(len(response.data),1)
    
    def test_get_available_rooms(self):
        data = {
            CONTENT: {
                'date':'2024-01-01'
            }
        }
        response = self.client.get(path=('/test/getAvailableRooms/8:00/9:00/'),data=data, 
                                    content_type=CONTENT_TYPE_JSON)
       
        self.assertEqual(len(response.data),0)

        response = self.client.get(path=('/test/getAvailableRooms/12:00/4:00/'),data=data, 
                                    content_type=CONTENT_TYPE_JSON)
       
        self.assertEqual(len(response.data),1)

    


class ReservationsTest:
    def setUp(self):
        pass
    

    def test_get_reservations_in_time_range():
        pass




