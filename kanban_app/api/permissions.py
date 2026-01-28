from rest_framework.permissions import BasePermission, SAFE_METHODS  
  
        
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
