from django.db import models

from django.conf import settings
from django.utils.text import slugify
import uuid
from django.contrib.auth.models import AbstractUser



class JobOffre(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    expiration_date = models.CharField(max_length=100)
    description = models.TextField()
    domain = models.CharField(max_length=100, blank=True, null=True)  # Vide pour le moment
    url = models.URLField()

    def __str__(self):
        return f"{self.title} at {self.company}"


class CV(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fichier = models.FileField(upload_to='cvs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    pdf_slug = models.SlugField(unique=True, blank=True)

    # 🔥 Relation avec DomainCV
    domains = models.ManyToManyField("DomainCV", related_name="cvs", blank=True)

    def save(self, *args, **kwargs):
        if not self.pdf_slug:
            self.pdf_slug = slugify(f"{self.user.username}-{uuid.uuid4()}")
        super().save(*args, **kwargs)



class MatchingScore(models.Model):
    cv = models.ForeignKey('CV', on_delete=models.CASCADE)
    job_offer = models.ForeignKey('JobOffre', on_delete=models.CASCADE)
    score = models.FloatField()
    correspend = models.TextField(blank=True, null=True)
    manque = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('cv', 'job_offer')  # pour éviter les doublons

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('jobseeker', 'Chercheur d\'emploi'),
        ('recruiter', 'Recruteur'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='jobseeker')

class DomainCV(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class DescriptionJobOffer(models.Model):
    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField()
    domain = models.ForeignKey("DomainCV", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Offre {self.id} - Domaine {self.domain.name}"


class MatchingScore2(models.Model):
    job_offer_desc = models.ForeignKey('DescriptionJobOffer', on_delete=models.CASCADE)
    cv = models.ForeignKey('CV', on_delete=models.CASCADE)
    score = models.FloatField()
    correspend = models.TextField(blank=True, null=True)
    manque = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('job_offer_desc', 'cv')  # éviter doublons
