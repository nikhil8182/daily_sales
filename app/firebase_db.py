import firebase_admin
from firebase_admin import credentials, firestore
import os
import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Initialize Firebase
try:
    cred = credentials.Certificate(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fb_key_1.json'))
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    
    # Test connection to detect if database exists
    db.collection('test').limit(1).get()
    
except Exception as e:
    if "The database (default) does not exist" in str(e):
        logger.error("""
=======================================================================
ERROR: Firestore database does not exist for your Firebase project.

Please follow these steps to set up Firestore:
1. Go to https://console.cloud.google.com/datastore/setup?project=fir-5575e
2. Select "Native" mode (not "Datastore" mode)
3. Choose a location for your database (us-central is a good default)
4. Click "Create Database"
5. Wait for the database to be provisioned (may take a few minutes)
6. Restart this application
=======================================================================
""")
    else:
        logger.error(f"Firebase initialization error: {str(e)}")
    
    raise RuntimeError("Firebase initialization failed. Application requires Firebase to run.")

# Collection names
PR_VISITS_COLLECTION = 'pr_visits'
TC_ACTIVITIES_COLLECTION = 'tc_activities'
TEAM_MEMBERS_COLLECTION = 'team_members'
FOLLOWUPS_COLLECTION = 'followups'

# Helper function to convert Firestore timestamps to datetime objects
def convert_timestamp(timestamp):
    if timestamp is None:
        return None
    return timestamp.astimezone(datetime.timezone.utc)

# Helper function to convert datetime objects to Firestore timestamps
def to_timestamp(dt):
    if dt is None:
        return None
    if isinstance(dt, str):
        dt = datetime.datetime.strptime(dt, "%H:%M")
    return firestore.SERVER_TIMESTAMP if dt is None else dt

# Helper function to handle Firestore document serialization
def document_to_dict(doc):
    if not doc.exists:
        return None
    
    data = doc.to_dict()
    data['id'] = doc.id
    return data

# Initialize default data if collections are empty
def initialize_default_data():
    # Check if team members collection is empty
    team_members = list(db.collection(TEAM_MEMBERS_COLLECTION).limit(1).stream())
    if not team_members:
        logger.info("Initializing default team members...")
        # Add default team members
        default_members = [
            {"name": "John Smith", "role": "PR", "active": True},
            {"name": "Jane Doe", "role": "TC", "active": True},
            {"name": "Mike Johnson", "role": "SM", "active": True},
        ]
        for member in default_members:
            member['created_at'] = firestore.SERVER_TIMESTAMP
            db.collection(TEAM_MEMBERS_COLLECTION).add(member)
        logger.info("Default team members added.")

# Try to initialize default data
try:
    initialize_default_data()
except Exception as e:
    logger.error(f"Error initializing default data: {str(e)}")

# TeamMember operations
def get_all_team_members():
    members = []
    docs = db.collection(TEAM_MEMBERS_COLLECTION).stream()
    for doc in docs:
        member = document_to_dict(doc)
        if member is not None:  # Add a check to ensure member is not None
            members.append(member)
    return members

def get_team_members_by_role(role):
    members = []
    try:
        docs = db.collection(TEAM_MEMBERS_COLLECTION).where('role', '==', role).where('active', '==', True).stream()
        for doc in docs:
            member = document_to_dict(doc)
            if member is not None:  # Add a check to ensure member is not None
                members.append(member)
    except Exception as e:
        logger.error(f"Error getting team members by role '{role}': {str(e)}")
        # If querying fails, get all members and filter manually as fallback
        try:
            all_members = get_all_team_members()
            members = [m for m in all_members if m and m.get('role') == role and m.get('active', True)]
        except Exception as inner_e:
            logger.error(f"Fallback filtering also failed: {str(inner_e)}")
    return members

def add_team_member(name, role):
    data = {
        'name': name,
        'role': role,
        'active': True,
        'created_at': firestore.SERVER_TIMESTAMP
    }
    doc_ref = db.collection(TEAM_MEMBERS_COLLECTION).add(data)
    return doc_ref[1].id

def toggle_team_member_status(member_id):
    doc_ref = db.collection(TEAM_MEMBERS_COLLECTION).document(member_id)
    doc = doc_ref.get()
    if doc.exists:
        member = doc.to_dict()
        doc_ref.update({'active': not member.get('active', True)})
        return True
    return False

def delete_team_member(member_id):
    db.collection(TEAM_MEMBERS_COLLECTION).document(member_id).delete()
    return True

# PRVisit operations
def get_todays_pr_visits():
    today = datetime.datetime.now().date()
    start_time = datetime.datetime.combine(today, datetime.time.min)
    end_time = datetime.datetime.combine(today, datetime.time.max)
    
    visits = []
    docs = db.collection(PR_VISITS_COLLECTION).where(
        'created_at', '>=', start_time
    ).where(
        'created_at', '<=', end_time
    ).stream()
    
    for doc in docs:
        visit = document_to_dict(doc)
        # Convert timestamps to datetime objects
        if 'visit_start_time' in visit and visit['visit_start_time']:
            visit['visit_start_time'] = convert_timestamp(visit['visit_start_time'])
        if 'created_at' in visit and visit['created_at']:
            visit['created_at'] = convert_timestamp(visit['created_at'])
        if 'updated_at' in visit and visit['updated_at']:
            visit['updated_at'] = convert_timestamp(visit['updated_at'])
        visits.append(visit)
    
    return visits

def add_pr_visit(pr_name, visit_start_time, client_name, manager_incharge, visit_status, notes):
    data = {
        'pr_name': pr_name,
        'visit_start_time': to_timestamp(visit_start_time),
        'client_name': client_name,
        'manager_incharge': manager_incharge,
        'visit_status': visit_status,
        'notes': notes,
        'created_at': firestore.SERVER_TIMESTAMP,
        'updated_at': firestore.SERVER_TIMESTAMP
    }
    doc_ref = db.collection(PR_VISITS_COLLECTION).add(data)
    return doc_ref[1].id

def update_pr_visit_status(visit_id, new_status):
    doc_ref = db.collection(PR_VISITS_COLLECTION).document(visit_id)
    doc_ref.update({
        'visit_status': new_status,
        'updated_at': firestore.SERVER_TIMESTAMP
    })
    return True

def delete_pr_visit(visit_id):
    db.collection(PR_VISITS_COLLECTION).document(visit_id).delete()
    return True

# TCActivity operations
def get_todays_tc_activities():
    today = datetime.datetime.now().date()
    start_time = datetime.datetime.combine(today, datetime.time.min)
    end_time = datetime.datetime.combine(today, datetime.time.max)
    
    activities = []
    docs = db.collection(TC_ACTIVITIES_COLLECTION).where(
        'created_at', '>=', start_time
    ).where(
        'created_at', '<=', end_time
    ).stream()
    
    for doc in docs:
        activity = document_to_dict(doc)
        # Convert timestamps to datetime objects
        if 'created_at' in activity and activity['created_at']:
            activity['created_at'] = convert_timestamp(activity['created_at'])
        if 'updated_at' in activity and activity['updated_at']:
            activity['updated_at'] = convert_timestamp(activity['updated_at'])
        activities.append(activity)
    
    return activities

def add_tc_activity(telecaller_name, manager_incharge, calls_made, visits_booked, visits_confirmed, leads_acquired, bucket_leads):
    data = {
        'telecaller_name': telecaller_name,
        'manager_incharge': manager_incharge,
        'calls_made': int(calls_made),
        'visits_booked': int(visits_booked),
        'visits_confirmed': int(visits_confirmed),
        'leads_acquired': int(leads_acquired),
        'bucket_leads': int(bucket_leads),
        'created_at': firestore.SERVER_TIMESTAMP,
        'updated_at': firestore.SERVER_TIMESTAMP
    }
    doc_ref = db.collection(TC_ACTIVITIES_COLLECTION).add(data)
    return doc_ref[1].id

def delete_tc_activity(activity_id):
    db.collection(TC_ACTIVITIES_COLLECTION).document(activity_id).delete()
    return True

# Followup operations
def add_followup(item_id, item_type, contact_name, contact_details, followup_date, followup_time, notes, manager_incharge):
    # Convert date and time strings to a combined datetime object
    followup_datetime = None
    try:
        if isinstance(followup_date, str) and isinstance(followup_time, str):
            followup_datetime = datetime.datetime.strptime(f"{followup_date} {followup_time}", "%Y-%m-%d %H:%M")
    except ValueError:
        logger.error(f"Invalid date or time format: {followup_date} {followup_time}")
    
    data = {
        'item_id': item_id,
        'item_type': item_type,
        'contact_name': contact_name,
        'contact_details': contact_details,
        'followup_date': followup_date if isinstance(followup_date, datetime.datetime) else followup_datetime,
        'followup_time': followup_time,
        'notes': notes,
        'manager_incharge': manager_incharge,
        'status': 'pending',
        'created_at': firestore.SERVER_TIMESTAMP,
        'updated_at': firestore.SERVER_TIMESTAMP
    }
    
    doc_ref = db.collection(FOLLOWUPS_COLLECTION).add(data)
    return doc_ref[1].id

def get_all_followups():
    followups = []
    docs = db.collection(FOLLOWUPS_COLLECTION).stream()
    
    for doc in docs:
        followup = document_to_dict(doc)
        # Convert timestamps to datetime objects
        if 'followup_date' in followup and followup['followup_date']:
            followup['followup_date'] = convert_timestamp(followup['followup_date'])
        if 'created_at' in followup and followup['created_at']:
            followup['created_at'] = convert_timestamp(followup['created_at'])
        if 'updated_at' in followup and followup['updated_at']:
            followup['updated_at'] = convert_timestamp(followup['updated_at'])
        followups.append(followup)
    
    return followups

def update_followup_status(followup_id, new_status):
    doc_ref = db.collection(FOLLOWUPS_COLLECTION).document(followup_id)
    doc_ref.update({
        'status': new_status,
        'updated_at': firestore.SERVER_TIMESTAMP
    })
    return True

def update_followup(followup_id, contact_name, contact_details, followup_date, followup_time, notes, manager_incharge):
    # Convert date and time strings to a combined datetime object
    followup_datetime = None
    try:
        if isinstance(followup_date, str) and isinstance(followup_time, str):
            followup_datetime = datetime.datetime.strptime(f"{followup_date} {followup_time}", "%Y-%m-%d %H:%M")
    except ValueError:
        logger.error(f"Invalid date or time format: {followup_date} {followup_time}")
    
    data = {
        'contact_name': contact_name,
        'contact_details': contact_details,
        'followup_date': followup_date if isinstance(followup_date, datetime.datetime) else followup_datetime,
        'followup_time': followup_time,
        'notes': notes,
        'manager_incharge': manager_incharge,
        'updated_at': firestore.SERVER_TIMESTAMP
    }
    
    doc_ref = db.collection(FOLLOWUPS_COLLECTION).document(followup_id)
    doc_ref.update(data)
    return True

def delete_followup(followup_id):
    db.collection(FOLLOWUPS_COLLECTION).document(followup_id).delete()
    return True