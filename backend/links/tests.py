from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from django.core.cache import cache
from django.db import IntegrityError, close_old_connections, connection
from django.test import TransactionTestCase, override_settings
from rest_framework.test import APITestCase

from .models import ShortLink
from .throttles import CreateLinkThrottle, StatisticsThrottle
from .views import RESERVED_CODES, generate_short_code


class LinkTests(APITestCase):
    def setUp(self):
        cache.clear()

    def create(self, url='https://example.com/a?b=1'):
        return self.client.post('/api/links/', {'original_url': url}, format='json')

    def test_create_and_statistics(self):
        response = self.create()
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['original_url'], 'https://example.com/a?b=1')
        self.assertEqual(data['click_count'], 0)
        self.assertTrue(data['created_at'])
        self.assertRegex(data['short_code'], r'^[a-zA-Z0-9]{7}$')
        self.assertEqual(data['short_url'], f"http://testserver/{data['short_code']}/")
        stats = self.client.get(f"/api/links/{data['short_code']}/stats/")
        self.assertEqual(stats.status_code, 200)
        self.assertEqual(stats.json(), data)

    def test_http_and_https(self):
        for url in ['http://example.com', 'https://example.com']:
            with self.subTest(url=url):
                self.assertEqual(self.create(url).status_code, 201)

    def test_invalid_urls(self):
        for url in ['', 'invalid', 'example.com', 'ftp://example.com',
                    'ftps://example.com', 'javascript:alert(1)', 'data:text/html,test',
                    'file:///etc/passwd', 'https://user:secret@example.com',
                    'https://example.com/' + 'a' * 2048]:
            with self.subTest(url=url):
                response = self.create(url)
                self.assertEqual(response.status_code, 400)
                self.assertIn('original_url', response.json())
        self.assertEqual(ShortLink.objects.count(), 0)

    def test_missing_field_and_invalid_json(self):
        self.assertEqual(self.client.post('/api/links/', {}, format='json').status_code, 400)
        self.assertEqual(self.client.post('/api/links/', '{', content_type='application/json').status_code, 400)

    def test_read_only_fields(self):
        response = self.client.post('/api/links/', {
            'original_url': 'https://example.com', 'short_code': 'admin', 'click_count': 500,
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(response.json()['short_code'], 'admin')
        self.assertEqual(response.json()['click_count'], 0)

    def test_redirect_and_count(self):
        link = ShortLink.objects.create(original_url='https://example.com/a?b=1', short_code='abc1234')
        for _ in range(3):
            response = self.client.get('/abc1234/')
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response['Location'], link.original_url)
            self.assertEqual(response['Cache-Control'], 'no-store')
        link.refresh_from_db()
        self.assertEqual(link.click_count, 3)
        self.assertEqual(self.client.head('/abc1234/').status_code, 302)
        self.assertEqual(self.client.post('/abc1234/').status_code, 405)
        self.client.get('/api/links/abc1234/stats/')
        link.refresh_from_db()
        self.assertEqual(link.click_count, 3)

    def test_missing_code(self):
        self.assertEqual(self.client.get('/missing/').status_code, 404)
        response = self.client.get('/api/links/missing/stats/')
        self.assertEqual(response.status_code, 404)
        self.assertIn('detail', response.json())

    def test_methods(self):
        self.assertEqual(self.client.get('/api/links/').status_code, 405)
        self.assertEqual(self.client.post('/api/links/missing/stats/').status_code, 405)

    def test_generator(self):
        codes = {generate_short_code() for _ in range(1000)}
        self.assertEqual(len(codes), 1000)
        self.assertTrue(all(len(code) == 7 and code.isalnum() for code in codes))

    @patch('links.views.generate_short_code', side_effect=['taken01', 'fresh01'])
    def test_collision_retry(self, generator):
        ShortLink.objects.create(original_url='https://example.com', short_code='taken01')
        response = self.create()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['short_code'], 'fresh01')
        self.assertEqual(generator.call_count, 2)

    @patch('links.views.generate_short_code', return_value='taken01')
    def test_collision_exhaustion(self, generator):
        ShortLink.objects.create(original_url='https://example.com', short_code='taken01')
        response = self.create()
        self.assertEqual(response.status_code, 503)
        self.assertEqual(generator.call_count, 5)
        self.assertEqual(ShortLink.objects.count(), 1)

    def test_reserved_codes(self):
        for code in RESERVED_CODES:
            with self.subTest(code=code), patch('links.views.generate_short_code', side_effect=[code.upper(), 'fresh01']):
                response = self.create()
                self.assertEqual(response.status_code, 201)
                self.assertEqual(response.json()['short_code'], 'fresh01')
                ShortLink.objects.all().delete()

    @patch('links.views.ShortLink.objects.create', side_effect=IntegrityError('other constraint'))
    def test_unrelated_integrity_error_is_not_retried(self, create):
        with self.assertRaises(IntegrityError):
            self.create()
        self.assertEqual(create.call_count, 1)

    @override_settings(SHORT_URL_BASE='https://short.example.com')
    def test_configurable_short_base(self):
        response = self.create()
        self.assertEqual(response.json()['short_url'], f"https://short.example.com/{response.json()['short_code']}/")

    def test_creation_throttle_and_client_isolation(self):
        with patch.object(CreateLinkThrottle, 'get_rate', return_value='2/min'):
            self.assertEqual(self.create().status_code, 201)
            self.assertEqual(self.create().status_code, 201)
            response = self.create()
            self.assertEqual(response.status_code, 429)
            self.assertIn('Retry-After', response)
            response = self.client.post('/api/links/', {'original_url': 'https://example.com'},
                                        format='json', REMOTE_ADDR='192.0.2.1')
            self.assertEqual(response.status_code, 201)

    def test_statistics_throttle(self):
        with patch.object(StatisticsThrottle, 'get_rate', return_value='1/min'):
            self.assertEqual(self.client.get('/api/links/missing/stats/').status_code, 404)
            self.assertEqual(self.client.get('/api/links/missing/stats/').status_code, 429)


class ConcurrentRedirectTests(TransactionTestCase):
    def test_concurrent_redirects_postgresql(self):
        if connection.vendor != 'postgresql':
            self.skipTest('Concorrência real requer PostgreSQL; SQLite bloqueia escritas concorrentes.')
        ShortLink.objects.create(original_url='https://example.com', short_code='parallel')

        def visit(_):
            from django.test import Client
            close_old_connections()
            try:
                return Client().get('/parallel/').status_code
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            statuses = list(pool.map(visit, range(20)))
        self.assertEqual(statuses, [302] * 20)
        self.assertEqual(ShortLink.objects.get(short_code='parallel').click_count, 20)
