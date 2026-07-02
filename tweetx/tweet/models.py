from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=400)
    photo = models.ImageField(upload_to='photos/', blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.text[0:20]}'


    @property
    def total_likes(self):
        return self.likes.count()
    
    @property
    def total_comments(self):
        return self.comments.count()

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'tweet')

    def __str__(self):
        return f'{self.user.username} - {self.tweet.text[0:20]}'

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField(max_length=400)
    created_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'{self.user.username} - {self.comment[0:10]}'

    
