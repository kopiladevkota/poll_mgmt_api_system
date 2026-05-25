from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    # Voting Interface UI - Add this line
    path('ui/', TemplateView.as_view(template_name='polls/voting_ui.html'), name='voting-ui'),
    
    # API endpoints
    path('polls/', views.PollListCreateView.as_view(), name='poll-list'),
    path('polls/<int:pk>/', views.PollDetailView.as_view(), name='poll-detail'),
    path('polls/<int:poll_id>/vote/', views.VoteView.as_view(), name='vote'),
    path('polls/<int:poll_id>/results/', views.PollResultsView.as_view(), name='results'),
    path('stats/', views.PollStatsView.as_view(), name='stats'),
    path('polls/bulk/create/', views.BulkPollCreateView.as_view(), name='bulk-poll-create'),
    path('polls/<int:poll_id>/bulk-vote/', views.BulkVoteView.as_view(), name='bulk-vote'),  
    path('vote/bulk/', views.MultiPollVoteView.as_view(), name='multi-poll-vote'),
]