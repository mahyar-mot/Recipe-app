from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer


TAG_URL = reverse('recipe:tag-list')


class PublicTests(TestCase):
    """Test for public apis"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test to check unauthorized user is blocked"""
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTests(TestCase):
    """Test for private apis"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@mahyar.com',
            'testpassword'
            )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Desert')

        res = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_user_created_tag(self):
        """Test that returned tags are for this user"""
        user2 = get_user_model().objects.create_user(
            'other@mahyar.com',
            'otherPass'
        )
        Tag.objects.create(user=user2, name='Vegan')
        tag = Tag.objects.create(user=self.user, name='Desert')

        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test fro createing new tag"""
        payload = {'name': 'Test Tag'}
        self.client.post(TAG_URL, payload)

        exists = Tag.objects.filter(
            user=self.user, name=payload['name']).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(TAG_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """Test filtering tags by those assigned to recipes"""
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            title='Corainder eggs on toast',
            time_minute=10,
            price=5.0,
            user=self.user
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAG_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
