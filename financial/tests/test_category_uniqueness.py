from django.contrib.auth import get_user_model
from django.test import TestCase

from financial.forms import CategoryForm
from financial.models import Category

User = get_user_model()


class CategoryUniquenessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alex", "alex@example.com", "pass-1234")
        self.other_user = User.objects.create_user("jamie", "jamie@example.com", "pass-9876")

    def test_category_name_is_case_insensitive_per_user(self):
        Category.objects.create(user=self.user, name="Groceries")

        form = CategoryForm({"name": "  groceries "}, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn("already have a category", form.errors["name"][0])

    def test_category_name_allows_same_label_for_other_users(self):
        Category.objects.create(user=self.user, name="Groceries")
        Category.objects.create(user=self.other_user, name="Groceries")
        self.assertEqual(Category.objects.filter(name__iexact="Groceries").count(), 2)
