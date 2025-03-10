from flask import Blueprint, render_template, request, redirect, url_for, jsonify, Response
from datetime import datetime
import subprocess
import os
import hmac
import hashlib
from app.firebase_db import (
    get_team_members_by_role, get_all_team_members, add_team_member,
    toggle_team_member_status, delete_team_member, get_todays_pr_visits,
    add_pr_visit, update_pr_visit_status, delete_pr_visit,
    get_todays_tc_activities, add_tc_activity, delete_tc_activity
)

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        
        if form_type == 'pr':
            add_pr_visit(
                pr_name=request.form['pr_name'],
                visit_start_time=request.form['visit_start_time'],
                client_name=request.form['client_name'],
                manager_incharge=request.form.get('manager_incharge', ''),
                visit_status=request.form['visit_status'],
                notes=request.form.get('notes', '')
            )
            
        elif form_type == 'tc':
            add_tc_activity(
                telecaller_name=request.form['telecaller_name'],
                manager_incharge=request.form['manager_incharge'],
                calls_made=request.form.get('calls_made', 0),
                visits_booked=request.form.get('visits_booked', 0),
                visits_confirmed=request.form.get('visits_confirmed', 0),
                leads_acquired=request.form.get('leads_acquired', 0),
                bucket_leads=request.form.get('bucket_leads', 0)
            )
        
        return redirect(url_for('main.index'))
    
    today = datetime.now().date()
    today_str = today.strftime('%Y-%m-%d')
    current_year = today.year
    
    # Get PR team members
    pr_team = get_team_members_by_role('PR')
    
    # Get today's PR visits
    pr_visits_raw = get_todays_pr_visits()
    
    # Organize PR visits by PR name with defensive programming
    pr_visits_by_name = {}
    for visit in pr_visits_raw:
        if visit and 'pr_name' in visit:
            pr_name = visit['pr_name']
            if pr_name not in pr_visits_by_name:
                pr_visits_by_name[pr_name] = []
            pr_visits_by_name[pr_name].append(visit)
    
    # Get TC activities and team members
    tc_activities = get_todays_tc_activities()
    tc_team = get_team_members_by_role('TC')
    sales_managers = get_team_members_by_role('SM')
    
    return render_template('index.html', 
                          pr_visits_raw=pr_visits_raw,
                          pr_visits_by_name=pr_visits_by_name,
                          tc_activities=tc_activities,
                          pr_team=pr_team,
                          tc_team=tc_team,
                          sales_managers=sales_managers,
                          today=today_str,
                          current_year=current_year,
                          current_time=datetime.now().strftime('%H:%M'))

@bp.route('/delete/pr/<string:id>', methods=['POST'])
def delete_pr_visit(id):
    delete_pr_visit(id)
    return redirect(url_for('main.index'))

@bp.route('/delete/tc/<string:id>', methods=['POST'])
def delete_tc_activity(id):
    delete_tc_activity(id)
    return redirect(url_for('main.index'))

@bp.route('/update-pr-status/<string:id>', methods=['POST'])
def update_pr_status(id):
    new_status = request.form.get('visit_status')
    if new_status:
        update_pr_visit_status(id, new_status)
    return redirect(url_for('main.index'))

@bp.route('/add-pr-visit', methods=['GET', 'POST'])
def add_pr_visit_route():
    if request.method == 'POST':
        add_pr_visit(
            pr_name=request.form['pr_name'],
            visit_start_time=request.form['visit_start_time'],
            client_name=request.form['client_name'],
            manager_incharge=request.form['manager_incharge'],
            visit_status=request.form['visit_status'],
            notes=request.form.get('notes', '')
        )
        return redirect(url_for('main.index'))
    
    pr_team = get_team_members_by_role('PR')
    sales_managers = get_team_members_by_role('SM')
    current_time = datetime.now().strftime('%H:%M')
    
    return render_template('add_pr_visit.html',
                          pr_team=pr_team,
                          sales_managers=sales_managers,
                          current_time=current_time)

@bp.route('/add-tc-activity', methods=['GET', 'POST'])
def add_tc_activity_route():
    if request.method == 'POST':
        add_tc_activity(
            telecaller_name=request.form['telecaller_name'],
            manager_incharge=request.form['manager_incharge'],
            calls_made=request.form.get('calls_made', 0),
            visits_booked=request.form.get('visits_booked', 0),
            visits_confirmed=request.form.get('visits_confirmed', 0),
            leads_acquired=request.form.get('leads_acquired', 0),
            bucket_leads=request.form.get('bucket_leads', 0)
        )
        return redirect(url_for('main.index'))
    
    tc_team = get_team_members_by_role('TC')
    sales_managers = get_team_members_by_role('SM')
    
    return render_template('add_tc_activity.html',
                          tc_team=tc_team,
                          sales_managers=sales_managers)

@bp.route('/team', methods=['GET', 'POST'])
def team():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            add_team_member(
                name=request.form['name'],
                role=request.form['role']
            )
            
        elif action == 'toggle':
            member_id = request.form['member_id']
            toggle_team_member_status(member_id)
            
        elif action == 'delete':
            member_id = request.form['member_id']
            delete_team_member(member_id)
        
        return redirect(url_for('main.team'))
    
    today = datetime.now().date()
    today_str = today.strftime('%Y-%m-%d')
    current_year = datetime.now().year
    
    # Filter members by role manually
    all_members = get_all_team_members()
    
    # Use defensive programming to handle potential missing 'role' keys
    pr_team = [m for m in all_members if m and m.get('role') == 'PR']
    tc_team = [m for m in all_members if m and m.get('role') == 'TC']
    sales_managers = [m for m in all_members if m and m.get('role') == 'SM']
    
    # Sort members by name with error handling
    try:
        if pr_team:
            pr_team.sort(key=lambda x: x.get('name', ''))
        if tc_team:
            tc_team.sort(key=lambda x: x.get('name', ''))
        if sales_managers:
            sales_managers.sort(key=lambda x: x.get('name', ''))
    except Exception as e:
        import logging
        logging.error(f"Error sorting team members: {str(e)}")
    
    return render_template('team.html',
                          pr_team=pr_team,
                          tc_team=tc_team,
                          sales_managers=sales_managers,
                          today=today_str,
                          current_year=current_year)
                          
@bp.route('/webhook', methods=['POST'])
def webhook():
    """
    Webhook endpoint to handle Git pull requests.
    This can be triggered by GitHub, GitLab, or other Git providers.
    """
    # For security, you would typically validate the request
    # using a secret key or token, but for simplicity we'll
    # omit that step in this example
    
    try:
        # Get project directory
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Run git pull
        result = subprocess.run(
            ['git', 'pull'],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Return the result
        return jsonify({
            'success': True,
            'message': 'Git pull executed successfully',
            'details': {
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        }), 200
        
    except subprocess.CalledProcessError as e:
        return jsonify({
            'success': False,
            'message': 'Git pull failed',
            'details': {
                'stdout': e.stdout,
                'stderr': e.stderr,
                'return_code': e.returncode
            }
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500