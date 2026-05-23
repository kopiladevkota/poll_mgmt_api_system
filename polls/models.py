from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils import timezone

User = get_user_model()

class Poll(models.Model):
    """Poll model with professional validation"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(5)],
        help_text="Poll question/title"
    )
    description = models.TextField(blank=True, null=True)
    
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='polls',
        null=True,
        blank=True
    )
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='draft'
    )
    
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    
    is_public = models.BooleanField(default=True)
    allow_multiple_votes = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['created_by']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def total_votes(self):
        return self.choices.aggregate(total=models.Sum('vote_count'))['total'] or 0
    
    @property
    def is_active(self):
        now = timezone.now()
        return (
            self.status == 'active' and 
            self.start_date <= now and 
            (not self.end_date or self.end_date > now)
        )
    
    def close(self):
        """Close the poll"""
        self.status = 'closed'
        self.save()
    
    def archive(self):
        """Archive the poll"""
        self.status = 'archived'
        self.save()


class Choice(models.Model):
    """Choice/option for a poll"""
    
    poll = models.ForeignKey(
        Poll, 
        on_delete=models.CASCADE, 
        related_name='choices'
    )
    choice_text = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(1)]
    )
    # CHANGED: Renamed from 'votes' to 'vote_count' to avoid conflict
    vote_count = models.PositiveIntegerField(default=0, help_text="Number of votes for this choice")
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'id']
        unique_together = ['poll', 'choice_text']
    
    def __str__(self):
        return f"{self.choice_text} ({self.vote_count} votes)"


class Vote(models.Model):
    """Track individual votes with user info"""
    
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes')
    choice = models.ForeignKey(
        Choice, 
        on_delete=models.CASCADE, 
        related_name='votes_received'  # CHANGED: Added custom related_name
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='votes',
        null=True,
        blank=True
    )
    session_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    voted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['poll', 'user']
        indexes = [
            models.Index(fields=['poll', 'user']),
            models.Index(fields=['voted_at']),
        ]
    
    def __str__(self):
        return f"Vote for {self.choice.choice_text} at {self.voted_at}"