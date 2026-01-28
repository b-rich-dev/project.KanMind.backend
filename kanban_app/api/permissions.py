from rest_framework.permissions import BasePermission, SAFE_METHODS

# class IsStaffOrReadOnly(BasePermission):
#     def has_permission(self, request, view):
#         is_staff = bool(request.user and request.user.is_staff)
#         return is_staff or request.method in SAFE_METHODS
    
    
# class IsAdminForDeleteOrPatchAndReadOnly(BasePermission):
#     def has_permission(self, request, view):
#         if request.method in SAFE_METHODS:
#             return True
#         elif request.method == 'DELETE':
#             return bool(request.user and request.user.is_superuser)
#         else:
#             return bool(request.user and request.user.is_staff)
        
        
# class IsOwnerOrAdmin(BasePermission):
#     def has_object_permission(self, request, view, obj):
#         if request.method in SAFE_METHODS:
#             return True
#         elif request.method == 'DELETE':
#             return bool(request.user and request.user.is_superuser)
#         else:
#             return bool(request.user and request.user == obj.user) or bool(request.user and request.user.is_staff)
        
        
class IsBoardOwnerOrMember(BasePermission):
    """
    Permission class for board access.
    
    Allows access if user is the board owner or a member of the board.
    Only owner can delete the board.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        # obj is a KanbanBoard instance
        # For DELETE, only owner is allowed
        if request.method == 'DELETE':
            return bool(request.user and request.user == obj.owner)
        # For other methods (GET, PATCH, PUT), owner or member
        return bool(request.user and (request.user == obj.owner or request.user in obj.members.all()))


# class IsReviewer(BasePermission):
#     """
#     Permission class for board modification.
    
#     Only the board owner has permission to modify or delete the board.
#     """
#     def has_permission(self, request, view):
#         return bool(request.user and request.user.is_authenticated)
    
#     def has_object_permission(self, request, view, obj):
#         # obj is a KanbanBoard instance
#         return bool(request.user and request.user == obj.reviewer)

# class IsBoardOwnerOrTaskAssignee(BasePermission):
#     """
#     Permission class for task access.
    
#     - Board owner has full access to all tasks in their board
#     - Task assignee can only access/modify their assigned task
#     """
#     def has_permission(self, request, view):
#         return bool(request.user and request.user.is_authenticated)
    
#     def has_object_permission(self, request, view, obj):
#         # obj is a Task instance
#         return bool(request.user and (
#             request.user == obj.board.owner or 
#             request.user == obj.assignee
#         ))
    