from django.test import TestCase, Client
from . import models

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
    def setup(self):
        self.client = Client()

        self.register_user(TEST_STUDENTID, TEST_EMAIL, 
                           TEST_PHONE, TEST_PASSWORD)

    
    def register_user(self, username, email, phone, password):
        data = {
            STUDENT_ID: TEST_STUDENTID,
            EMAIL: TEST_EMAIL,
            PHONE: TEST_PHONE,
            PASSWORD: TEST_PASSWORD
        }

        self.client.post(path=REGISTER, data=data)

        my_student = models.Student.objects.get(pk=TEST_STUDENTID)
        self.assertTrue(my_student is not None)
