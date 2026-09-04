from django.contrib.auth.models import User
from django.test import TestCase

from .models import Patient, Profile


class SignupViewTests(TestCase):

	def test_signup_creates_patient_account_and_logs_user_in(self):
		response = self.client.post(
			'/signup/',
			{
				'username': 'newpatient',
				'first_name': 'New',
				'last_name': 'Patient',
				'email': 'newpatient@example.com',
				'password': 'A-strong-password-123',
				'password_confirmation': 'A-strong-password-123',
				'age': '34',
				'phone': '5551234567',
				'address': '12 Health Street',
			}
		)

		self.assertRedirects(response, '/dashboard/', fetch_redirect_response=True)
		user = User.objects.get(username='newpatient')
		self.assertTrue(user.check_password('A-strong-password-123'))
		self.assertEqual(Profile.objects.get(user=user).role, 'Patient')
		self.assertEqual(Patient.objects.get(user=user).age, 34)
		self.assertEqual(str(response.wsgi_request.user), 'newpatient')

	def test_signup_rejects_duplicate_username(self):
		User.objects.create_user(
			username='existing',
			password='A-strong-password-123'
		)

		response = self.client.post(
			'/signup/',
			{
				'username': 'EXISTING',
				'password': 'A-strong-password-123',
				'password_confirmation': 'A-strong-password-123',
				'age': '34',
				'phone': '5551234567',
				'address': '12 Health Street',
			}
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'That username is already in use.')
		self.assertEqual(User.objects.filter(username__iexact='existing').count(), 1)

# Create your tests here.
