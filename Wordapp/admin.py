# ==================== Wordapp/admin.py ====================

from django.contrib import admin
from .models import Word, GameSession, UserProfile, Achievement, Feedback, WordHistory

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ['word', 'difficulty', 'created_at']
    list_filter = ['difficulty', 'created_at']
    search_fields = ['word', 'definition']
    ordering = ['word']
    list_per_page = 50
    
    fieldsets = (
        ('Word Information', {
            'fields': ('word', 'difficulty')
        }),
        ('Details', {
            'fields': ('definition', 'usage_example')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        obj.word = obj.word.upper()
        super().save_model(request, obj, form, change)

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'difficulty', 'score', 'words_found', 'total_words', 'completion_percentage', 'completed', 'formatted_time', 'created_at']
    list_filter = ['difficulty', 'completed', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'completion_percentage', 'formatted_time']
    ordering = ['-created_at']
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Player Information', {
            'fields': ('user',)
        }),
        ('Game Details', {
            'fields': ('difficulty', 'grid_size', 'words_found', 'total_words', 'completed')
        }),
        ('Score & Time', {
            'fields': ('score', 'time_taken', 'formatted_time')
        }),
        ('Statistics', {
            'fields': ('completion_percentage', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def completion_percentage(self, obj):
        return f"{obj.completion_percentage}%"
    completion_percentage.short_description = 'Completion %'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_games', 'total_score', 'highest_score', 'words_discovered', 'average_score', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    ordering = ['-highest_score']
    readonly_fields = ['created_at', 'updated_at', 'average_score']
    list_per_page = 50
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'bio', 'avatar')
        }),
        ('Game Statistics', {
            'fields': ('total_games', 'total_score', 'highest_score', 'words_discovered', 'average_score')
        }),
        ('Achievements', {
            'fields': ('achievements',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def average_score(self, obj):
        return f"{obj.average_score:.2f}"
    average_score.short_description = 'Avg Score'

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'achievement_type', 'earned_at']
    list_filter = ['achievement_type', 'earned_at']
    search_fields = ['user__username', 'name', 'description']
    ordering = ['-earned_at']
    readonly_fields = ['earned_at']
    list_per_page = 50
    date_hierarchy = 'earned_at'
    
    fieldsets = (
        ('Achievement Information', {
            'fields': ('user', 'name', 'achievement_type')
        }),
        ('Details', {
            'fields': ('description', 'earned_at')
        }),
    )

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('user', 'name', 'email')
        }),
        ('Feedback Details', {
            'fields': ('subject', 'message', 'is_read')
        }),
        ('Admin Response', {
            'fields': ('admin_response',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} feedback(s) marked as read.")
    mark_as_read.short_description = "Mark selected as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f"{queryset.count()} feedback(s) marked as unread.")
    mark_as_unread.short_description = "Mark selected as unread"

@admin.register(WordHistory)
class WordHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'word', 'game_session', 'found_at']
    list_filter = ['found_at', 'word__difficulty']
    search_fields = ['user__username', 'word__word']
    ordering = ['-found_at']
    readonly_fields = ['found_at']
    list_per_page = 50
    date_hierarchy = 'found_at'
    
    fieldsets = (
        ('Word Found', {
            'fields': ('user', 'word', 'game_session')
        }),
        ('Timestamp', {
            'fields': ('found_at',)
        }),
    )