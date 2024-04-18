from django.test import TestCase, Client
from django.db import connection
from . import models

# Endpoints
REGISTER       = '/test/registerStudent/'
CREATE_LIBRARY = '/test/createLibrary/'
CREATE_ROOM = '/test/createRoom/'

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

        
        
