from rest_framework import permissions


class IsAdminOrCaretakerOrReadOnly(permissions.BasePermission):
    """
    Разрешает чтение всем.
    Смотритель (Caretaker) и Администратор могут изменять (PATCH, PUT).
    Удалять и создавать может только Администратор.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Админ может всё
        if request.user.is_staff or request.user.groups.filter(name="Administrator").exists():
            return True
            
        # Смотритель может изменять, но не создавать/удалять
        if request.method in ["PUT", "PATCH"]:
            if request.user.groups.filter(name="Caretaker").exists():
                return True
                
        return False