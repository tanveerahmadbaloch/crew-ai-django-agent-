from django.db import models
from django.contrib.auth.models import User

class Content(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, default='pending', 
                             choices=[('pending', 'Pending'), 
                                     ('processing', 'Processing'),
                                     ('completed', 'Completed'),
                                     ('failed', 'Failed')])
    task_id = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.title

