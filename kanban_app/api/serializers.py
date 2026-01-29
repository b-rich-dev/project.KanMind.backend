from django.contrib.auth.models import User

from rest_framework import serializers

from kanban_app.models import KanbanBoard, Task, Comment


class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer for listing and creating Kanban boards.  
    Provides summary statistics including member count, ticket count,
    tasks in 'to do' status, and high priority tasks.
    """
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False, write_only=True)
    
    class Meta:
        model = KanbanBoard
        fields = ['id', 'title', 'members', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id']
        read_only_fields = ['id', 'owner_id']
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_ticket_count(self, obj):
        return obj.board_tasks.count()
    
    def get_tasks_to_do_count(self, obj):
        return obj.board_tasks.filter(status='to_do').count()
    
    def get_tasks_high_prio_count(self, obj):
        return obj.board_tasks.filter(priority='high').count()
        
        
class UserDataSerializer(serializers.ModelSerializer):
    """
    Serializer for user data representation.   
    Combines first_name and last_name into a single fullname field.
    Falls back to username if no name is provided.
    """
    fullname = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']
    
    def get_fullname(self, obj):
        """Return full name or username as fallback."""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for listing and creating tasks.   
    Validates that assignee and reviewer are members of the board.
    Provides read-only user data for assignee and reviewer.
    """
    assignee = UserDataSerializer(read_only=True)
    reviewer = UserDataSerializer(source='reviewer_id', read_only=True)
    comments_count = serializers.SerializerMethodField()
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        write_only=True,
        required=False,
        allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority', 'assignee', 'assignee_id', 'reviewer', 'reviewer_id', 'due_date', 'comments_count']
        read_only_fields = ['id', 'comments_count']
    
    def validate(self, data):
        board = data.get('board')
        assignee = data.get('assignee')
        reviewer = data.get('reviewer_id')
        
        board_members = board.members.all()
        
        if assignee and assignee not in board_members:
            raise serializers.ValidationError({"assignee_id": "Assignee must be a member of the board."})
        
        if reviewer and reviewer not in board_members:
            raise serializers.ValidationError({"reviewer_id": "Reviewer must be a member of the board."})
        
        return data
    
    def get_comments_count(self, obj):
        return obj.task_comments.count()


class TaskDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving and updating task details.   
    Board field is read-only to prevent moving tasks between boards.
    Validates that assignee and reviewer are members of the board.
    """
    assignee = UserDataSerializer(read_only=True)
    reviewer = UserDataSerializer(source='reviewer_id', read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        write_only=True,
        required=False,
        allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'assignee', 'assignee_id', 'reviewer', 'reviewer_id', 'due_date']
        read_only_fields = ['id', 'board']
    
    def validate(self, data):
        board = self.instance.board if self.instance else data.get('board')
        assignee = data.get('assignee')
        reviewer = data.get('reviewer_id')
        
        if not board:
            return data
        
        board_members = board.members.all()
        
        if assignee and assignee not in board_members:
            raise serializers.ValidationError({"assignee_id": "Assignee must be a member of the board."})
        
        if reviewer and reviewer not in board_members:
            raise serializers.ValidationError({"reviewer_id": "Reviewer must be a member of the board."})
        
        return data
    
        
class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed board view.   
    Includes full member data and all associated tasks.
    """
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = UserDataSerializer(many=True, read_only=True)
    members_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=User.objects.all(), 
        source='members',
        write_only=True,
        required=False
    )
    tasks = TaskSerializer(many=True, source='board_tasks', read_only=True)
    
    class Meta:
        model = KanbanBoard
        fields = ['id', 'title', 'owner_id', 'members', 'members_ids', 'tasks']


class BoardUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating board details.   
    Allows updating title and members. Owner cannot be changed.
    """
    owner_data = UserDataSerializer(source='owner', read_only=True)
    members_data = UserDataSerializer(many=True, source='members', read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=User.objects.all(), 
        write_only=True,
        required=False
    )
    
    class Meta:
        model = KanbanBoard
        fields = ['id', 'title', 'owner_data', 'members_data', 'members']
        
        
class TaskCommentsSerializer(serializers.ModelSerializer):
    """
    Serializer for task comments.   
    Author is automatically set from authenticated user.
    Author field returns full name or username.
    """
    author = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'author', 'created_at']
    
    def get_author(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.username
    