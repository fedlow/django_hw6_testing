from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Employee
from .serializers import EmployeeSerializer
from .permissions import IsAdminOrCaretakerOrReadOnly
from .filters import EmployeeFilter


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by("id").prefetch_related("images")
    serializer_class = EmployeeSerializer
    filterset_class = EmployeeFilter
    permission_classes = [IsAdminOrCaretakerOrReadOnly]