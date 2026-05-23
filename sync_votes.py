import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poll_api.settings')
django.setup()

from polls.models import Poll, Choice, Vote
from django.db.models import Count

print("=" * 60)
print("SYNCING VOTE COUNTS")
print("=" * 60)

# Update all choices with actual vote counts
for choice in Choice.objects.all():
    actual_votes = Vote.objects.filter(choice=choice).count()
    
    if choice.vote_count != actual_votes:
        print(f"\n📊 Choice: {choice.choice_text}")
        print(f"   Poll: {choice.poll.title}")
        print(f"   Current vote_count: {choice.vote_count}")
        print(f"   Actual votes in Vote table: {actual_votes}")
        print(f"   ✓ Updating to {actual_votes}")
        choice.vote_count = actual_votes
        choice.save()
    else:
        print(f"\n✓ {choice.choice_text}: {choice.vote_count} votes (already correct)")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

for poll in Poll.objects.all():
    total = poll.total_votes
    print(f"\n📋 Poll: {poll.title}")
    print(f"   Total Votes: {total}")
    for choice in poll.choices.all():
        print(f"   • {choice.choice_text}: {choice.vote_count} votes")

print("\n✅ Sync completed!")