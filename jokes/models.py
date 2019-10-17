from django.db import models


class JokeTeller(models.Model):
    username = models.CharField(max_length=10)
    step = models.IntegerField(default=0)
    channel = models.CharField(max_length=50)


class JokeResponder(models.Model):
    username = models.CharField(max_length=10)
    step = models.IntegerField(default=0)
    channel = models.CharField(max_length=50)
    which_joke = models.IntegerField(default=0)
