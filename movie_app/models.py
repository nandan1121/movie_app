from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from django.db import models

class Theater(models.Model):
    name = models.CharField(max_length=255)

class Screen(models.Model):
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

class WeeklySchedule(models.Model):
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10)
    open_time = models.TimeField()
    close_time = models.TimeField()

class WeeklyUnavailability(models.Model):
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()

class CustomUnavailability(models.Model):
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)  # Date for the unavailability
    start_time = models.TimeField(null=True, blank=True)  # Start time (if time-specific)
    end_time = models.TimeField(null=True, blank=True)  # End time (if time-specific)

    def __str__(self):
        return f"{self.screen.name} - {self.date} ({self.start_time} to {self.end_time})"
