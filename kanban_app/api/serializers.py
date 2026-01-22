from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from kanban_app.models import KanbanBoard, Task

class BoardSerializer(serializers.ModelSerializer):
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
    fullname = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']
    
    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class TaskSerializer(serializers.ModelSerializer):
    assignee = UserDataSerializer(read_only=True)
    reviewer = UserDataSerializer(source='reviewer_id', read_only=True)
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'assignee', 'reviewer', 'due_date', 'comments_count']
    
    def get_comments_count(self, obj):
        return obj.task_comments.count()

        
class BoardDetailSerializer(serializers.ModelSerializer):
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
    owner_data = UserDataSerializer(source='owner', read_only=True)
    members_data = UserDataSerializer(many=True, source='members', read_only=True)
    members_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=User.objects.all(), 
        source='members',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = KanbanBoard
        fields = ['id', 'title', 'owner_data', 'members_data', 'members_ids']