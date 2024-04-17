from django.test import TestCase, Client
from . import models
from django.db import connection

# Endpoints
REGISTER = '/registerStudent/'

# Request Body Fields
STUDENT_ID = 'studentId'
EMAIL = 'email'
PHONE = 'phone'
PASSWORD = 'password'

# Test Data
TEST_STUDENTID = 'abc123'
TEST_EMAIL = 'abc123@nyu.edu'
TEST_PHONE = '1010101010'
TEST_PASSWORD = 'password'


class ARLibTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_db_connection(self):
        self.assertTrue(connection is not None)

    def test_register_student(self):
        data = {
            STUDENT_ID: TEST_STUDENTID,
            EMAIL: TEST_EMAIL,
            PHONE: TEST_PHONE,
            PASSWORD: TEST_PASSWORD
        }

        response = self.client.post(path=REGISTER, data=data)
        self.assertEqual(response.status_code, 200)
        