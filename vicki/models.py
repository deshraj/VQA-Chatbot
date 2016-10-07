from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse

# Create your models here.
class UserDetail(models.Model):
    uuid = models.CharField(max_length=1000, blank=True, null=True)
    name = models.CharField(max_length=1000, blank=True, null=True)
    target_image = models.CharField(max_length=1000, blank=True, null=True)
    start_time = models.DateTimeField("Start Time", null=True, auto_now=True)
    end_time = models.DateTimeField("End Time", null=True, auto_now=True)


class Prediction(models.Model):
    user = models.ForeignKey(UserDetail)
    predicted_image = models.CharField(max_length=1000, blank=True, null=True)
    time = models.DateTimeField("Time of Prediction", null=True, auto_now_add=True)


class QuestionAnswer(models.Model):
    user = models.ForeignKey(UserDetail)
    question = models.CharField(max_length=1000, blank=True, null=True)
    question_time = models.DateTimeField("Question Time", null=True, auto_now_add=True)
    bot_answer = models.CharField(max_length=1000, blank=True, null=True)
    bot_answer_time = models.DateTimeField("Bot Answer Time", null=True, auto_now=True)
