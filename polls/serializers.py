from rest_framework import serializers
from .models import Poll, Choice, Vote
from django.utils import timezone

class ChoiceSerializer(serializers.ModelSerializer):
    """Serializer for poll choices"""
    
    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'vote_count', 'order']  # Changed 'votes' to 'vote_count'
        read_only_fields = ['vote_count']


class ChoiceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating choices"""
    
    class Meta:
        model = Choice
        fields = ['choice_text', 'order']


class VoteSerializer(serializers.ModelSerializer):
    """Serializer for votes"""
    
    class Meta:
        model = Vote
        fields = ['choice_id', 'poll_id', 'voted_at']
        read_only_fields = ['voted_at']


class VoteCreateSerializer(serializers.Serializer):
    """Serializer for vote creation"""
    
    choice_id = serializers.IntegerField()
    
    def validate_choice_id(self, value):
        """Validate choice exists and poll is active"""
        try:
            choice = Choice.objects.get(id=value)
            poll = choice.poll
            
            if not poll.is_active:
                raise serializers.ValidationError("This poll is not active")
            
            if poll.end_date and poll.end_date < timezone.now():
                raise serializers.ValidationError("This poll has ended")
                
        except Choice.DoesNotExist:
            raise serializers.ValidationError("Choice does not exist")
        
        return value


class PollListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list view"""
    
    total_votes = serializers.IntegerField(read_only=True)
    choices_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Poll
        fields = ['id', 'title', 'status', 'total_votes', 'choices_count', 
                  'created_at', 'is_active']
    
    def get_choices_count(self, obj):
        return obj.choices.count()


class PollDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single poll"""
    
    choices = ChoiceSerializer(many=True, read_only=True)
    total_votes = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    user_has_voted = serializers.SerializerMethodField()
    
    class Meta:
        model = Poll
        fields = ['id', 'title', 'description', 'status', 'choices', 
                  'total_votes', 'created_at', 'updated_at', 'start_date',
                  'end_date', 'is_public', 'allow_multiple_votes', 
                  'is_active', 'user_has_voted']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_user_has_voted(self, obj):
        """Check if current user has voted"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Vote.objects.filter(poll=obj, user=request.user).exists()
        return False


class PollCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating polls with choices"""
    
    choices = ChoiceCreateSerializer(many=True, write_only=True)
    
    class Meta:
        model = Poll
        fields = ['title', 'description', 'choices', 'end_date', 
                  'is_public', 'allow_multiple_votes']
    
    def validate_choices(self, value):
        """Validate at least 2 choices"""
        if len(value) < 2:
            raise serializers.ValidationError("Poll must have at least 2 choices")
        return value
    
    def create(self, validated_data):
        choices_data = validated_data.pop('choices')
        poll = Poll.objects.create(**validated_data)
        
        for order, choice_data in enumerate(choices_data):
            Choice.objects.create(poll=poll, order=order, **choice_data)
        
        return poll


class PollResultsSerializer(serializers.ModelSerializer):
    """Serializer for poll results with percentages"""
    
    choices = serializers.SerializerMethodField()
    total_votes = serializers.IntegerField(read_only=True)
    participation_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Poll
        fields = ['id', 'title', 'total_votes', 'choices', 
                  'participation_rate', 'status']
    
    def get_choices(self, obj):
        """Calculate percentages for each choice"""
        total = obj.total_votes
        choices_data = []
        
        for choice in obj.choices.all():
            percentage = (choice.vote_count / total * 100) if total > 0 else 0  # Changed 'votes' to 'vote_count'
            choices_data.append({
                'id': choice.id,
                'text': choice.choice_text,
                'votes': choice.vote_count,  # Changed 'votes' to 'vote_count'
                'percentage': round(percentage, 2),
                'order': choice.order
            })
        
        return choices_data
    
    def get_participation_rate(self, obj):
        """Calculate participation rate (dummy for now)"""
        return 0