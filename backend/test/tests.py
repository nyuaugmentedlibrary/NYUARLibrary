from django.test import TestCase, Client
from django.db import connection
from django.urls import URLPattern, URLResolver, get_resolver
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

    def test_db_connection(self):
        self.assertTrue(connection is not None)

    def print_endpoints(self, urlpatterns, parent_pattern=None):
        for pattern in urlpatterns:
            if isinstance(pattern, URLResolver):
                if parent_pattern is None:
                    self.print_endpoints(pattern.url_patterns, pattern.pattern)
                else:
                    self.print_endpoints(pattern.url_patterns, parent_pattern)
            elif isinstance(pattern, URLPattern):
                if parent_pattern is not None:
                    self.stdout.write(parent_pattern.regex.pattern + pattern.pattern.regex.pattern)
                else:
                    self.stdout.write(pattern.pattern.regex.pattern)

    def test_print_endpoints(self):
        resolver = get_resolver()
        self.print_endpoints(resolver.url_patterns)

    def test_register_student(self):
        data = {
            STUDENT_ID: TEST_STUDENTID,
            EMAIL: TEST_EMAIL,
            PHONE: TEST_PHONE,
            PASSWORD: TEST_PASSWORD
        }

        response = self.client.post(path=REGISTER, data=data)
        self.assertEqual(response.status_code, 200)
        