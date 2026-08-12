"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },

    # Sports-related activities
    "Soccer Team": {
        "description": "Competitive soccer team practices and matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 18,
        "participants": ["alex@mergington.edu"]
    },
    "Swimming Club": {
        "description": "Lap swimming and technique coaching",
        "schedule": "Mondays and Wednesdays, 5:00 PM - 6:30 PM",
        "max_participants": 16,
        "participants": []
    },

    # Artistic activities
    "Drama Club": {
        "description": "Theater rehearsals and stage productions",
        "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["lily@mergington.edu"]
    },
    "Art Studio": {
        "description": "Open studio time for drawing, painting, and mixed media",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["noah@mergington.edu"]
    },

    # Intellectual activities
    "Debate Team": {
        "description": "Competitive debate practice and tournaments",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["chris@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Hands-on science challenges and competition preparation",
        "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
        "max_participants": 24,
        "participants": ["ava@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity.

    Prevent duplicate registrations by normalizing emails and checking
    existing participants. Also enforce max_participants.
    """
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Basic email validation/normalization
    if not email or not isinstance(email, str):
        raise HTTPException(status_code=400, detail="Invalid email provided")
    email_normalized = email.strip().lower()
    if not email_normalized:
        raise HTTPException(status_code=400, detail="Invalid email provided")

    # Get the specific activity
    activity = activities[activity_name]

    # Enforce capacity
    if len(activity.get("participants", [])) >= activity.get("max_participants", float("inf")):
        raise HTTPException(status_code=400, detail="Activity is full")

    # Prevent duplicate registrations (compare normalized emails)
    normalized_participants = [p.strip().lower() for p in activity.get("participants", [])]
    if email_normalized in normalized_participants:
        raise HTTPException(status_code=400, detail="Student already registered for this activity")

    # Add student (store normalized email to avoid future duplicates)
    activity.setdefault("participants", []).append(email_normalized)
    return {"message": f"Signed up {email_normalized} for {activity_name}"}


@app.delete("/activities/{activity_name}/signup")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity.

    Accepts email as a query parameter. Normalizes the email and removes it
    from the participants list if present.
    """
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    if not email or not isinstance(email, str):
        raise HTTPException(status_code=400, detail="Invalid email provided")
    email_normalized = email.strip().lower()

    activity = activities[activity_name]
    participants = activity.get("participants", [])
    normalized_participants = [p.strip().lower() for p in participants]

    if email_normalized not in normalized_participants:
        raise HTTPException(status_code=404, detail="Student not registered for this activity")

    # Remove first matching participant (normalized)
    for i, p in enumerate(participants):
        if p.strip().lower() == email_normalized:
            participants.pop(i)
            break

    return {"message": f"Unregistered {email_normalized} from {activity_name}"}
