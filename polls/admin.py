from django.contrib import admin
from django.utils.html import format_html
from .models import Poll, Choice, Vote

# Simplified admin site without complex copying
class PollAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'total_votes_display', 'created_at')
    list_filter = ('status', 'is_public', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Poll Information', {
            'fields': ('title', 'description', 'created_by')
        }),
        ('Status Settings', {
            'fields': ('status', 'start_date', 'end_date')
        }),
        ('Privacy Settings', {
            'fields': ('is_public', 'allow_multiple_votes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_votes_display(self, obj):
        return obj.total_votes
    total_votes_display.short_description = 'Total Votes'

class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice_text', 'poll', 'vote_count', 'order')
    list_filter = ('poll',)
    search_fields = ('choice_text',)
    readonly_fields = ('vote_count',)

class VoteAdmin(admin.ModelAdmin):
    list_display = ('poll', 'choice', 'user', 'voted_at')
    list_filter = ('voted_at', 'poll')
    readonly_fields = ('voted_at',)

# Register models
admin.site.register(Poll, PollAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Vote, VoteAdmin)

# Add copyright footer
admin.site.site_header = "Poll API - Developed by Kopila Devkota"
admin.site.site_title = "Poll Management System"
admin.site.index_title = "Dashboard"

# Add copyright footer via CSS
from django.contrib.admin import AdminSite
AdminSite.index_template = None