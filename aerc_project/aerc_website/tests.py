from django.test import TestCase
from django.urls import reverse
from aerc_website.models import *

class TestAercWebAppGuest(TestCase):

    # test redirect without logging in
    def test_01_index_redirect(self): 
        response = self.client.get(reverse('index'))
        self.assertEqual(response.url, '/login')
    def test_02_index_redirect(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.url, '/login')
    def test_03_index_redirect(self):
        response = self.client.get(reverse('vehicle'))
        self.assertEqual(response.url, '/login')
    def test_04_index_redirect(self):
        response = self.client.get(reverse('house'))
        self.assertEqual(response.url, '/login')
    def test_05_index_redirect(self):
        response = self.client.get(reverse('crypto'))
        self.assertEqual(response.url, '/login')
    def test_06_index_redirect(self):
        response = self.client.get(reverse('stock'))
        self.assertEqual(response.url, '/login')
    def test_07_index_redirect(self):
        response = self.client.get(reverse('redirect_logout'))
        self.assertEqual(response.url, '/login')

class TestAercWebAppAdmin(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
                    username='admin',
                    password='admin12345')
    
    def setUp(self): # Login for each test
        self.client.post(reverse('login'), {'username': 'admin', 'password': 'admin12345'})

    def test_01_index(self): # test index page
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_02_home(self): # test home page
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_03_house(self): # test home page
        response = self.client.get(reverse('house'))
        self.assertEqual(response.status_code, 200)

    def test_04_vehicle(self): # test vehicle page
        response = self.client.get(reverse('vehicle'))
        self.assertEqual(response.status_code, 200)

    def test_05_crypto(self): # test crypto page
        response = self.client.get(reverse('crypto'))
        self.assertEqual(response.status_code, 200)

    def test_06_stock(self): # test stock page
        response = self.client.get(reverse('stock'))
        self.assertEqual(response.status_code, 200)

    def test_07_logout(self): # test stock page
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login")