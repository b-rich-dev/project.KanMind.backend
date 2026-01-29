from rest_framework.permissions import BasePermission
  
        
class IsBoardOwnerOrMember(BasePermission):
    """
    Permission class for board access.  
    Allows access if user is the board owner or a member of the board.
    Only owner can delete the board.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return bool(request.user and request.user == obj.owner)

        return bool(request.user and (request.user == obj.owner or request.user in obj.members.all()))


class IsTaskBoardMember(BasePermission):
    """
    Permission class for task access.  
    Allows access if user is the board owner or a member of the board.
    For DELETE, only task creator or board owner can delete.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        board = obj.board
        user = request.user
        
        if request.method == 'DELETE':
            return bool(user and (user == obj.created_by or user == board.owner))
        
        return bool(user and (user == board.owner or user in board.members.all()))


class IsCommentBoardMember(BasePermission):
    """
    Permission class for comment access.
    Allows access if user is the board owner or a member of the board.
    For DELETE, only comment author can delete.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        board = obj.task.board
        user = request.user
        
        if request.method == 'DELETE':
            return bool(user and user == obj.author)
        
        return bool(user and (user == board.owner or user in board.members.all()))
