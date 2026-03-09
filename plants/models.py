from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserPlant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plant_name = models.CharField(max_length=100)
    experience = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'plant_name')

    def __str__(self):
        return f"{self.user.username} - {self.plant_name} ({self.experience} xp)"