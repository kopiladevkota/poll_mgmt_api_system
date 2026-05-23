from django.db.models import Sum
from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Poll, Choice, Vote
from .serializers import (
    PollListSerializer, PollDetailSerializer, PollCreateSerializer,
    PollResultsSerializer, VoteCreateSerializer
)

class PollListCreateView(generics.ListCreateAPIView):
    """
    List all polls or create a new poll
    GET: Returns paginated list of polls
    POST: Creates a new poll with choices
    """
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_public']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'total_votes', 'title']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PollCreateSerializer
        return PollListSerializer
    
    def get_queryset(self):
        """Filter polls based on user and status"""
        queryset = Poll.objects.all()
        
        # Show only active/public polls to non-authenticated users
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status='active', is_public=True)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by active status
        active_only = self.request.query_params.get('active_only', 'false').lower() == 'true'
        if active_only:
            now = timezone.now()
            queryset = queryset.filter(
                status='active',
                start_date__lte=now
            ).exclude(end_date__lt=now)
        
        return queryset.prefetch_related('choices')
    
    def perform_create(self, serializer):
        """Set the creator when creating a poll"""
        serializer.save(created_by=self.request.user if self.request.user.is_authenticated else None)


class PollDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a poll
    GET: Returns detailed poll information with choices
    PUT/PATCH: Update poll details (owner only)
    DELETE: Delete poll (owner only)
    """
    
    queryset = Poll.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PollCreateSerializer
        return PollDetailSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_update(self, serializer):
        """Check ownership before update"""
        poll = self.get_object()
        if poll.created_by and poll.created_by != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to edit this poll")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Check ownership before delete"""
        if instance.created_by and instance.created_by != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to delete this poll")
        instance.delete()


class VoteView(APIView):
    """
    Post a vote for a poll choice
    POST: Record a vote for a specific choice in a poll
    """
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    
    def post(self, request, poll_id):
        """Record a vote"""
        poll = get_object_or_404(Poll, id=poll_id)
        
        # Check if poll is active
        if not poll.is_active:
            return Response(
                {'error': 'This poll is not active or has ended'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate vote data
        serializer = VoteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        choice_id = serializer.validated_data['choice_id']
        choice = get_object_or_404(Choice, id=choice_id, poll=poll)
        
        # Check for duplicate votes (if not allowing multiple votes)
        if not poll.allow_multiple_votes:
            existing_vote = None
            if request.user.is_authenticated:
                existing_vote = Vote.objects.filter(
                    poll=poll, user=request.user
                ).first()
            else:
                # For anonymous users, check by session/ip
                session_id = request.session.session_key
                if session_id:
                    existing_vote = Vote.objects.filter(
                        poll=poll, session_id=session_id
                    ).first()
            
            if existing_vote:
                return Response(
                    {'error': 'You have already voted in this poll'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create vote record
        vote = Vote.objects.create(
            poll=poll,
            choice=choice,
            user=request.user if request.user.is_authenticated else None,
            session_id=request.session.session_key,
            ip_address=self.get_client_ip(request)
        )
        
        # Increment choice vote count
        choice.vote_count += 1
        choice.save()
        
        return Response({
            'message': 'Vote recorded successfully',
            'vote_id': vote.id,
            'choice': choice.choice_text,
            'choice_id': choice.id,
            'poll_id': poll.id,
            'poll_title': poll.title,
            'voted_at': vote.voted_at
        }, status=status.HTTP_201_CREATED)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PollResultsView(APIView):
    """
    Get poll results with detailed statistics
    GET: Returns poll results with percentage calculations
    """
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request, poll_id):
        """Get results for a specific poll"""
        poll = get_object_or_404(Poll, id=poll_id)
        
        # Check if results should be public
        if poll.status == 'draft':
            if not request.user.is_authenticated or poll.created_by != request.user:
                return Response(
                    {'error': 'Results are not available for this poll'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = PollResultsSerializer(poll)
        
        # Add metadata
        data = serializer.data
        data['is_active'] = poll.is_active
        data['ends_in'] = self.get_time_remaining(poll)
        
        return Response(data)
    
    def get_time_remaining(self, poll):
        """Calculate time remaining for active poll"""
        if poll.end_date and poll.end_date > timezone.now():
            remaining = poll.end_date - timezone.now()
            return {
                'days': remaining.days,
                'hours': remaining.seconds // 3600,
                'minutes': (remaining.seconds % 3600) // 60
            }
        return None


class PollStatsView(APIView):
    """
    Get overall statistics for all polls
    GET: Returns aggregated statistics
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get dashboard statistics"""
        from django.db.models import Count, Sum, Avg
        
        stats = {
            'total_polls': Poll.objects.count(),
            'active_polls': Poll.objects.filter(status='active').count(),
            'total_votes': Vote.objects.count(),
            'total_choices': Choice.objects.count(),
            'avg_votes_per_poll': Vote.objects.aggregate(avg=Avg('poll'))['avg'] or 0,
            'most_popular_poll': self.get_most_popular_poll(),
            'recent_activity': self.get_recent_activity()
        }
        
        return Response(stats)
    
    def get_most_popular_poll(self):
        """Get poll with most votes"""
        poll = Poll.objects.annotate(
            vote_count=Sum('choices__votes')
        ).order_by('-vote_count').first()
        
        if poll:
            return {
                'id': poll.id,
                'title': poll.title,
                'total_votes': poll.total_votes
            }
        return None
    
    def get_recent_activity(self):
        """Get recent votes"""
        recent_votes = Vote.objects.select_related(
            'poll', 'choice'
        ).order_by('-voted_at')[:10]
        
        return [{
            'poll_title': vote.poll.title,
            'choice_text': vote.choice.choice_text,
            'voted_at': vote.voted_at
        } for vote in recent_votes]