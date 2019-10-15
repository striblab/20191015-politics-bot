from django.db import models

class NewCandidate(models.Model):
    entity_full_name = models.CharField(max_length=255)
    entity_id = models.CharField(max_length=10)
    party_name = models.CharField(max_length=100)
    office_sought = models.CharField(max_length=100)
    district = models.CharField(max_length=10, blank=True)
    registration_date = models.DateField()
    termination_date = models.DateField(null=True)
    bool_alert_sent = models.BooleanField(default=False)
    ingestion_date = models.DateTimeField(auto_now_add=True)
