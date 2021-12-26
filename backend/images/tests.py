from os import link
from re import S
from django.test import TestCase
import requests
# import requests
from images.models import Image
from rest_framework.test import APIRequestFactory
from rest_framework import serializers, status
from rest_framework.test import APITestCase

from images.serializers import ImageSerializer

class ImageTestCase(TestCase):
    def setUp(self):
        self.lion_url = "https://upload.wikimedia.org/wikipedia/commons/7/73/Lion_waiting_in_Namibia.jpg"
        self.cat_url = "https://static01.nyt.com/images/2021/09/14/science/07CAT-STRIPES/07CAT-STRIPES-mediumSquareAt3X-v2.jpg"
        self.broken_url = "https://upload.wikimedia.org/wikipedia/commons/7/73/Lion_waiting_in_Namibia.jpg123123"
        Image.objects.create(
            name="lion",
            picture=None,
            url=self.lion_url,
            parent_picture=None
        )
        Image.objects.create(
            name="broken_link",
            picture=None,
            url=self.broken_url,
            parent_picture=None
        )
        Image.objects.create(
            name="link_no_img",
            picture=None,
            url='https://google.com',
            parent_picture=None
        )

    def test_image_validation_from_not_existing_url(self):
        broken_img = Image.objects.get(name="broken_link")
        broken_img_serialized = ImageSerializer(instance=broken_img).data
        serializer = ImageSerializer(data=broken_img_serialized)
        self.assertFalse(serializer.is_valid())

    def test_image_validation_from_url_without_image(self):
        link_no_img = Image.objects.get(name="link_no_img")
        link_no_img_serialized = ImageSerializer(instance=link_no_img).data
        serializer = ImageSerializer(data=link_no_img_serialized)
        self.assertFalse(serializer.is_valid())

    def test_image_resize(self):
        width = 200
        height = 250

        lion = Image.objects.get(name="lion")
        lion_resized = lion.resize(width, height)
        serializer = ImageSerializer(lion_resized)
        self.assertIsNotNone(lion_resized.picture)
        self.assertEqual(lion_resized.picture.width, width)
        self.assertEqual(lion_resized.picture.height, height)
