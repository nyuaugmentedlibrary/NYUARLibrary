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
    def setUp(self):
        self.client = Client()

    def test_register_student(self):
        data = {
            STUDENT_ID: TEST_STUDENTID,
            EMAIL: TEST_EMAIL,
            PHONE: TEST_PHONE,
            PASSWORD: TEST_PASSWORD
        }

        self.client.post(path=REGISTER, data=data)

        try:
            my_student = models.Student.objects.get(pk=TEST_STUDENTID)
        except models.Student.DoesNotExist:
            print("Student with ID {} does not exist in the database.".format(TEST_STUDENTID))
            all_students = models.Student.objects.all()
            print("All students in the database:", all_students)
            raise
