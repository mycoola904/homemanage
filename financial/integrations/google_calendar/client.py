from financial.services.billpay_calendar import BillPayEventSpec

class GoogleCalendarClient:
    def __init__(self):
        self._service = None  # placeholder until next step

    def insert_event(self, calendar_id: str, payload: dict) -> tuple[str, str | None]:
        raise NotImplementedError("GoogleCalendarClient.insert_event is not implemented yet")
        
    def patch_event(self, calendar_id: str, event_id: str, payload: dict) -> tuple[str, str | None]:
        raise NotImplementedError("GoogleCalendarClient.patch_event is not implemented yet")
    
    def delete_event(self, calendar_id: str, event_id: str) -> None:
        raise NotImplementedError("GoogleCalendarClient.delete_event is not implemented yet")

def build_google_event_payload(spec: BillPayEventSpec) -> dict:
    """
    Builds a Google Calendar event payload from a BillPayEventSpec.

    Args:
        spec: A BillPayEventSpec containing the details of the event.        

    Returns:
        A dictionary representing the Google Calendar event payload.
    """
    payload = {
        "summary": spec.summary,
        "description": spec.description,
        "start": {"date": spec.start_date.isoformat()},
        "end": {"date": spec.end_date.isoformat()},
        "extendedProperties": {"private": spec.extended_properties},
    }
    return payload