from django.contrib.auth.models import AbstractUser
from django.db import models
import json

class User(AbstractUser):
    USER_TYPES = (
        ('user', 'Utilisateur'),
        ('coach', 'Coach'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='user')
    
    # Résoudre les conflits de reverse accessor
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        verbose_name='user permissions',
    )
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

class Coach(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='coach_profile')
    experience = models.TextField(default='[]')  # Stockage JSON de la liste
    
    def set_experience(self, experience_list):
        """Définir la liste d'expériences"""
        self.experience = json.dumps(experience_list)
    
    def get_experience(self):
        """Récupérer la liste d'expériences"""
        try:
            return json.loads(self.experience)
        except:
            return []
    
    def add_experience(self, new_experience):
        """Ajouter une expérience"""
        experiences = self.get_experience()
        experiences.append(new_experience)
        self.set_experience(experiences)
        self.save()
    
    def __str__(self):
        return f"Coach {self.user.username}"
