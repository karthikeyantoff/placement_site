import os
import sys
import unittest
import json

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from models.database import get_db

class TestAuth(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        with self.app.app_context():
            self.db = get_db()

    def test_01_admin_login_success(self):
        payload = {'username': 'sivasubramaniyan', 'password': 'sivu@12345', 'role': 'admin'}
        res = self.client.post('/api/auth/login', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('user', {}).get('role'), 'admin')
        self.assertEqual(data.get('redirect_url'), '/dashboard')

    def test_02_manager_login_success(self):
        payload = {'username': 'jeyakannan', 'password': 'jk@12345', 'role': 'manager'}
        res = self.client.post('/api/auth/login', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('user', {}).get('role'), 'manager')

    def test_03_lead_login_success(self):
        payload = {'username': 'lead-1', 'password': 'lead1@12345', 'role': 'lead'}
        res = self.client.post('/api/auth/login', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('user', {}).get('role'), 'lead')

    def test_04_login_invalid_password(self):
        payload = {'username': 'sivasubramaniyan', 'password': 'wrong_password_123', 'role': 'admin'}
        res = self.client.post('/api/auth/login', json=payload)
        self.assertEqual(res.status_code, 401)
        data = res.get_json()
        self.assertIn('Incorrect password', data.get('error', ''))

    def test_05_login_nonexistent_user(self):
        payload = {'username': 'non_existent_user_999', 'password': 'any_password', 'role': 'admin'}
        res = self.client.post('/api/auth/login', json=payload)
        self.assertEqual(res.status_code, 401)
        data = res.get_json()
        self.assertIn('Invalid username', data.get('error', ''))

    def test_06_login_role_mismatch(self):
        payload = {'username': 'lead-1', 'password': 'lead1@12345', 'role': 'admin'}
        res = self.client.post('/api/auth/login', json=payload)
        self.assertEqual(res.status_code, 401)
        data = res.get_json()
        self.assertIn('Role mismatch', data.get('error', ''))

    def test_07_login_missing_fields(self):
        payload = {'username': 'sivasubramaniyan'}
        res = self.client.post('/api/auth/login', json=payload)
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn('required', data.get('error', ''))

    def test_08_login_options_preflight(self):
        res = self.client.open('/api/auth/login', method='OPTIONS')
        self.assertEqual(res.status_code, 200)

    def test_09_login_get_redirect(self):
        res = self.client.get('/api/auth/login')
        self.assertEqual(res.status_code, 302)
        self.assertIn('/login', res.headers.get('Location', ''))

    def test_10_me_endpoint_unauthenticated(self):
        res = self.client.get('/api/auth/me')
        self.assertEqual(res.status_code, 401)

    def test_11_me_endpoint_authenticated(self):
        login_res = self.client.post('/api/auth/login', json={'username': 'sivasubramaniyan', 'password': 'sivu@12345', 'role': 'admin'})
        self.assertEqual(login_res.status_code, 200)
        me_res = self.client.get('/api/auth/me')
        self.assertEqual(me_res.status_code, 200)
        data = me_res.get_json()
        self.assertTrue(data.get('authenticated'))
        self.assertEqual(data.get('user', {}).get('username'), 'sivasubramaniyan')

    def test_12_logout_clears_session(self):
        self.client.post('/api/auth/login', json={'username': 'sivasubramaniyan', 'password': 'sivu@12345', 'role': 'admin'})
        logout_res = self.client.post('/api/auth/logout')
        self.assertEqual(logout_res.status_code, 200)
        me_res = self.client.get('/api/auth/me')
        self.assertEqual(me_res.status_code, 401)

    def test_13_dashboard_unauthorized_redirect(self):
        res = self.client.get('/dashboard')
        self.assertEqual(res.status_code, 302)
        self.assertIn('/login', res.headers.get('Location', ''))

if __name__ == '__main__':
    unittest.main(verbosity=2)
