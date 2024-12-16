def generate_slots(weekly_schedule, weekly_unavailability, custom_unavailability, start_date, end_date, screen_id):
    """
    Generate available slots for the given theater and screen within the specified date range.
    """ 
    slots = []
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    current_date = start_date

    while current_date <= end_date:
        day_name = current_date.strftime('%A')

        # Get weekly schedule for the day
        day_schedule = next((schedule for schedule in weekly_schedule if schedule['day_of_week'] == day_name), None)

        if day_schedule:
            open_time = datetime.combine(current_date, day_schedule['open_time'])
            close_time = datetime.combine(current_date, day_schedule['close_time'])

            # Adjust for weekly unavailability
            day_unavailabilities = [u for u in weekly_unavailability if u['day_of_week'] == day_name]

            # Generate slots between open_time and close_time, avoiding unavailability
            current_time = open_time

            while current_time + timedelta(hours=2) <= close_time:
                next_time = current_time + timedelta(hours=2)

                # Check if the slot is unavailable due to weekly or custom unavailability
                slot_available = True

                for unavailability in day_unavailabilities:
                    unavailability_start = datetime.combine(current_date, unavailability['start_time'])
                    unavailability_end = datetime.combine(current_date, unavailability['end_time'])

                    if not (next_time <= unavailability_start or current_time >= unavailability_end):
                        slot_available = False
                        break

                # Check for custom unavailability
                custom_unavailabilities = [u for u in custom_unavailability if u['screen_id'] == screen_id]

                for custom in custom_unavailabilities:
                    if custom['date'] == current_date.date():
                        if custom['start_time'] and custom['end_time']:
                            custom_start = datetime.combine(current_date, custom['start_time'])
                            custom_end = datetime.combine(current_date, custom['end_time'])

                            if not (next_time <= custom_start or current_time >= custom_end):
                                slot_available = False
                                break
                        elif not custom['start_time'] and not custom['end_time']:
                            slot_available = False
                            break

                if slot_available:
                    slots.append({
                        'screen_id': screen_id,
                        'start': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'end': next_time.strftime('%Y-%m-%d %H:%M:%S')
                    })

                current_time = next_time

        current_date += timedelta(days=1)

    return slots