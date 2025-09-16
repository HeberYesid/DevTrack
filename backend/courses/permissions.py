from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'ADMIN')


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'TEACHER')


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'STUDENT')


class IsOwnerTeacherOrAdmin(BasePermission):
    """Object-level: only the subject teacher or admin can modify; others read-only if permitted by view."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, 'role', None) == 'ADMIN':
            return True
        # obj can be Subject or related model with 'subject' attribute
        subject = getattr(obj, 'subject', obj)
        if request.method in SAFE_METHODS:
            return True
        return getattr(subject, 'teacher_id', None) == user.id


class IsTeacherOrAdmin(BasePermission):
    def has_permission(self, request, view):
        role = getattr(request.user, 'role', None)
        return bool(request.user and request.user.is_authenticated and role in {'ADMIN', 'TEACHER'})
