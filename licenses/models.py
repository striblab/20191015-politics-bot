from django.db import models


class AgendaItem(models.Model):
    committee_name = models.CharField(max_length=255)
    meeting_id = models.IntegerField()
    meeting_link = models.CharField(max_length=255)
    item_title = models.CharField(max_length=255)
    item_link = models.CharField(max_length=255)
    item_description = models.TextField()
    action_type = models.CharField(max_length=50)
    action_taken = models.CharField(max_length=255)
    bool_alert_sent = models.BooleanField(default=False)
    ingestion_date = models.DateTimeField(auto_now_add=True)
