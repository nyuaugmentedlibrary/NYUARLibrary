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
TEST_EMAIL = 'abc123@nyu.edu'
TEST_PHONE = '1010101010'
TEST_PASSWORD = 'password'

TEST_LBRY_NAME = 'my library'
TEST_LBRY_LOC = 'manhattan'
TEST_LBRY_PHONE = '0101010101'

TEST_ROOM_ID = 'EZ103'
TEST_ROOM_TYPE = 'study'
TEST_ROOM_MINCAP = 2
TEST_ROOM_MAXCAP = 8
TEST_ROOM_NOISELVL = 2
TEST_ROOM_OPENHR = 8
TEST_ROOM_OPENMIN = 0
TEST_ROOM_CLOSEHR = 20
TEST_ROOM_CLOSEMIN = 0


class ARLibTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.register_student()
        self.create_library()
        self.create_room()


    def register_student(self):
        data = {
            CONTENT : {
                STUDENT_ID: TEST_STUDENTID,
                EMAIL: TEST_EMAIL,
                PHONE: TEST_PHONE,
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
                LOCATION: TEST_LBRY_LOC,
                PHONE: TEST_LBRY_PHONE
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
                ROOM_TYPE: TEST_ROOM_TYPE,
                MIN_CAPACITY: TEST_ROOM_MINCAP,
                MAX_CAPACITY: TEST_ROOM_MAXCAP,
                NOISE_LEVEL: TEST_ROOM_NOISELVL,
                OPEN_HOUR: TEST_ROOM_OPENHR,
                OPEN_MINUTE: TEST_ROOM_OPENMIN,
                CLOSE_HOUR: TEST_ROOM_CLOSEHR,
                CLOSE_MINUTE: TEST_ROOM_CLOSEMIN
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

        
        