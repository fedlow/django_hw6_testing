from rest_framework import serializers
from .models import Employee, EmployeeImage


class EmployeeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeImage
        fields = ["id", "image", "order"]


class EmployeeSerializer(serializers.ModelSerializer):
    images = EmployeeImageSerializer(many=True, read_only=True)
    tenure_days = serializers.ReadOnlyField()

    class Meta:
        model = Employee
        fields = [
            "id",
            "first_name",
            "last_name",
            "gender",
            "skills",
            "hire_date",
            "desk_number",
            "role",
            "tenure_days",
            "images",
        ]