from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from .models import Theater, WeeklySchedule, WeeklyUnavailability
import json

# Create your views here.
class TheaterAvailabilityView(View):
    def post(self, request, id):
        data = request.json()

        # Parse and save weekly schedule and unavailability
        weekly_schedule = data.get("weekly_schedule", {})
        weekly_unavailability = data.get("weekly_unavailability", {})

        theater = get_object_or_404(Theater, id=id)

        # Clear previous configurations
        WeeklySchedule.objects.filter(theater=theater).delete()
        WeeklyUnavailability.objects.filter(theater=theater).delete()

        # Save new configurations
        for day, times in weekly_schedule.items():
            WeeklySchedule.objects.create(
                theater=theater,
                day_of_week=day,
                open_time=times['open'],
                close_time=times['close']
            )

        for day, times_list in weekly_unavailability.items():
            for times in times_list:
                WeeklyUnavailability.objects.create(
                    theater=theater,
                    day_of_week=day,
                    start_time=times['start'],
                    end_time=times['end']
                )

        return JsonResponse({"message": "Availability configured successfully."})

class CustomUnavailabilityView(View):
    def post(self, request, id):
        try:
            data = json.loads(request.body)

            # Parse payload
            screen_id = data.get("screen_id")
            unavailable_slots = data.get("unavailable_slots", [])
            unavailable_dates = data.get("unavailable_dates", [])

            # Fetch the theater and screen
            theater = get_object_or_404(Theater, id=id)
            screen = get_object_or_404(Screen, id=screen_id, theater=theater)

            # Save unavailable slots
            for slot in unavailable_slots:
                CustomUnavailability.objects.create(
                    screen=screen,
                    date=slot['date'],
                    start_time=slot['start'],
                    end_time=slot['end']
                )

            # Save unavailable dates (entire day unavailable)
            for date in unavailable_dates:
                CustomUnavailability.objects.create(
                    screen=screen,
                    date=date
                )

            return JsonResponse({"message": "Custom unavailability configured successfully."}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

            
class AvailableSlotsView(View):
    def get(self, request, id):
        screen_id = request.GET.get('screen_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        theater = get_object_or_404(Theater, id=id)
        screen = get_object_or_404(Screen, id=screen_id, theater=theater)

        weekly_schedule = list(WeeklySchedule.objects.filter(theater=theater).values())
        weekly_unavailability = list(WeeklyUnavailability.objects.filter(theater=theater).values())
        custom_unavailability = list(CustomUnavailability.objects.filter(screen=screen).values())

        slots = generate_slots(weekly_schedule, weekly_unavailability, custom_unavailability, start_date, end_date, screen_id)

        return JsonResponse({"available_slots": slots})
