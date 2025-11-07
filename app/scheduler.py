# app/scheduler.py
import os
import uuid
from datetime import datetime, timedelta

class VisitScheduler:
    """
    Handles scheduling of property site visits and generates .ics calendar files.
    """

    def __init__(self, output_dir: str = "data/schedules"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def schedule_visit(self, client_name: str, property_name: str, date_time: datetime) -> str:
        """
        Creates an ICS file for the site visit appointment.
        Returns the file path.
        """
        event_id = str(uuid.uuid4())
        file_path = os.path.join(self.output_dir, f"visit_{event_id}.ics")

        dt_start = date_time.strftime("%Y%m%dT%H%M%S")
        dt_end = (date_time + timedelta(hours=1)).strftime("%Y%m%dT%H%M%S")

        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//RealEstateAgenticAI//EN
BEGIN:VEVENT
UID:{event_id}
DTSTAMP:{datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")}
DTSTART:{dt_start}
DTEND:{dt_end}
SUMMARY:Site Visit - {property_name}
DESCRIPTION:Scheduled site visit for {client_name} to view property: {property_name}
LOCATION:Property Location
END:VEVENT
END:VCALENDAR
"""

        with open(file_path, "w") as f:
            f.write(ics_content)

        print(f"[Scheduler] Visit scheduled: {file_path}")
        return file_path

    def schedule_from_text(self, query_data: dict) -> str:
        """
        Example convenience function to auto-schedule based on NLU output.
        """
        client_name = query_data.get("client_name", "Client")
        property_name = query_data.get("entities", {}).get("property", "Selected Property")

        # Default: schedule 24 hours from now
        visit_time = datetime.now() + timedelta(days=1)
        return self.schedule_visit(client_name, property_name, visit_time)


# Example usage test
if __name__ == "__main__":
    scheduler = VisitScheduler()
    scheduler.schedule_visit("Rahul Sharma", "Sunshine Villa, Noida", datetime.now() + timedelta(days=2, hours=3))
