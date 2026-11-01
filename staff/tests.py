from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Employee, EmployeeImage


class BaseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")

        self.emp1 = Employee.objects.create(
            first_name="Иван", last_name="Иванов", gender="M", role="QA", desk_number=1
        )
        self.emp2 = Employee.objects.create(
            first_name="Петр", last_name="Петров", gender="M", role="BACK", desk_number=5
        )

        # Создаем фейковое изображение (1x1 пиксель)
        image_content = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        fake_image = SimpleUploadedFile("test_image.gif", image_content, content_type="image/gif")

        self.img1 = EmployeeImage.objects.create(employee=self.emp1, order=1, image=fake_image)
        self.img2 = EmployeeImage.objects.create(employee=self.emp1, order=2, image=fake_image)

        for i in range(12):
            Employee.objects.create(
                first_name=f"Сотрудник{i}", last_name="Тестовый", gender="F", role="FRONT", desk_number=10 + i
            )


class HomePageTest(BaseTestCase):
    def test_home_page_status_code(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_home_page_context(self):
        response = self.client.get(reverse("home"))
        self.assertIn("total_employees", response.context)
        self.assertEqual(response.context["total_employees"], 14)
        self.assertIn("employees", response.context)
        self.assertTrue(len(response.context["employees"]) <= 4)


class EmployeeListTest(BaseTestCase):
    def test_employee_list_status_code(self):
        response = self.client.get(reverse("employee_list"))
        self.assertEqual(response.status_code, 200)

    def test_employee_list_pagination(self):
        response = self.client.get(reverse("employee_list"))
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["employees"]), 10)


class EmployeeDetailTest(BaseTestCase):
    def test_detail_page_unauthenticated_redirect(self):
        response = self.client.get(reverse("employee_detail", args=[self.emp1.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_detail_page_authenticated_access(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("employee_detail", args=[self.emp1.pk]))
        self.assertEqual(response.status_code, 200)

    def test_detail_page_context(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("employee_detail", args=[self.emp1.pk]))
        self.assertIn("employee", response.context)
        self.assertEqual(response.context["main_image"], self.img1)
        self.assertIn(self.img2, response.context["other_images"])


class DeskValidatorTest(BaseTestCase):
    def test_validator_adjacent_desks_error(self):
        bad_employee = Employee(first_name="Тест", last_name="Тест", gender="M", role="BACK", desk_number=2)
        with self.assertRaises(ValidationError):
            bad_employee.full_clean()

    def test_validator_same_role_adjacent_desks_ok(self):
        good_employee = Employee(first_name="Тест", last_name="Тест", gender="M", role="QA", desk_number=2)
        try:
            good_employee.full_clean()
        except ValidationError:
            self.fail("Валидатор ошибочно запретил двум QA сидеть рядом")

    def test_validator_far_desks_ok(self):
        good_employee = Employee(first_name="Тест", last_name="Тест", gender="M", role="BACK", desk_number=10)
        try:
            good_employee.full_clean()
        except ValidationError:
            self.fail("Валидатор ошибочно запретил сидеть за не соседними столами")