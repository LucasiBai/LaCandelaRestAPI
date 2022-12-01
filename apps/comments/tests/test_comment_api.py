from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient

from db.models import Comment, Product, Category, Order, ShippingInfo
