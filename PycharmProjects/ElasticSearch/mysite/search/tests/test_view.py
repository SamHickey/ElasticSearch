from django.test import TestCase
from django.urls import reverse

# Create your tests here.

class ViewTest(TestCase):

    # test url exists
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/search/')
        self.assertEqual(response.status_code, 200)

    # test url is accessible by its name
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('search:search'))
        self.assertEqual(response.status_code, 200)

    # test that url uses the desired template
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('search:search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/index.html')


