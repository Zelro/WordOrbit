# ==================== Wordapp/models.py ====================

from django.db import models
from django.contrib.auth.models import User

class Word(models.Model):
    """Model for storing words used in the game"""
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    word = models.CharField(max_length=50, unique=True)
    definition = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    usage_example = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['word']
    
    def __str__(self):
        return f"{self.word} ({self.difficulty})"

class GameSession(models.Model):
    """Model for tracking individual game sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_sessions')
    difficulty = models.CharField(max_length=10)
    grid_size = models.IntegerField()
    words_found = models.IntegerField(default=0)
    total_words = models.IntegerField()
    score = models.IntegerField(default=0)
    time_taken = models.IntegerField(help_text="Time in seconds")
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.difficulty} - Score: {self.score}"
    
    @property
    def completion_percentage(self):
        if self.total_words == 0:
            return 0
        return round((self.words_found / self.total_words) * 100, 2)
    
    @property
    def formatted_time(self):
        minutes = self.time_taken // 60
        seconds = self.time_taken % 60
        return f"{minutes:02d}:{seconds:02d}"

class UserProfile(models.Model):
    """Extended user profile for game statistics"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    total_games = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    highest_score = models.IntegerField(default=0)
    words_discovered = models.IntegerField(default=0)
    achievements = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

     
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def average_score(self):
        if self.total_games == 0:
            return 0
        return round(self.total_score / self.total_games, 2)

class Achievement(models.Model):
    """Model for tracking user achievements"""
    ACHIEVEMENT_TYPES = [
        ('first_game', 'First Game'),
        ('word_master', 'Word Master'),
        ('high_scorer', 'High Scorer'),
        ('speed_demon', 'Speed Demon'),
        ('dedicated_player', 'Dedicated Player'),
        ('streak_master', 'Streak Master'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    name = models.CharField(max_length=100)
    description = models.TextField()
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES, default='first_game')
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-earned_at']
        verbose_name = 'Achievement'
        verbose_name_plural = 'Achievements'
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"

class Feedback(models.Model):
    """Model for user feedback and contact messages"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='feedbacks')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    admin_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"

class WordHistory(models.Model):
    """Track words found by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='word_history')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='found_by')
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='words_found_in_session')
    found_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-found_at']
    
    def __str__(self):
        return f"{self.user.username} found {self.word.word}"