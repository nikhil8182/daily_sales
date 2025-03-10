from flask import Blueprint, render_template, request, redirect, url_for, jsonify, Response
from app.models import db, PRVisit, TCActivity, TeamMember
from datetime import datetime
import subprocess
import os
import hmac
import hashlib

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        
        if form_type == 'pr':
            visit = PRVisit(
                pr_name=request.form['pr_name'],
                visit_start_time=datetime.strptime(request.form['visit_start_time'], '%H:%M'),
                client_name=request.form['client_name'],
                manager_response=request.form.get('manager_response', 'Pending'),
                visit_status=request.form['visit_status'],
                notes=request.form.get('notes', '')
            )
            db.session.add(visit)
            
        elif form_type == 'tc':
            activity = TCActivity(
                telecaller_name=request.form['telecaller_name'],
                manager_incharge=request.form['manager_incharge'],
                calls_made=int(request.form.get('calls_made', 0)),
                visits_booked=int(request.form.get('visits_booked', 0)),
                visits_confirmed=int(request.form.get('visits_confirmed', 0)),
                leads_acquired=int(request.form.get('leads_acquired', 0)),
                bucket_leads=int(request.form.get('bucket_leads', 0))
            )
            db.session.add(activity)
        
        db.session.commit()
        return redirect(url_for('main.index'))
    
    today = datetime.now().date()
    today_str = today.strftime('%Y-%m-%d')
    current_year = today.year
    
    # Get PR team members first
    pr_team = TeamMember.query.filter_by(role='PR', active=True).order_by(TeamMember.name).all()
    
    # Get today's PR visits
    pr_visits_raw = PRVisit.query.filter(
        db.func.date(PRVisit.created_at) == today
    ).order_by(PRVisit.visit_start_time).all()
    
    # Organize PR visits by PR name
    pr_visits_by_name = {}
    for visit in pr_visits_raw:
        if visit.pr_name not in pr_visits_by_name:
            pr_visits_by_name[visit.pr_name] = []
        pr_visits_by_name[visit.pr_name].append(visit)
    
    # Get TC activities
    tc_activities = TCActivity.query.filter(
        db.func.date(TCActivity.created_at) == today
    ).all()
    
    # For telecaller team and sales managers (for dropdowns)
    tc_team = TeamMember.query.filter_by(role='TC', active=True).all()
    sales_managers = TeamMember.query.filter_by(role='SM', active=True).all()
    
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

@bp.route('/delete/pr/<int:id>', methods=['POST'])
def delete_pr_visit(id):
    visit = PRVisit.query.get_or_404(id)
    db.session.delete(visit)
    db.session.commit()
    return redirect(url_for('main.index'))

@bp.route('/delete/tc/<int:id>', methods=['POST'])
def delete_tc_activity(id):
    activity = TCActivity.query.get_or_404(id)
    db.session.delete(activity)
    db.session.commit()
    return redirect(url_for('main.index'))

@bp.route('/update-pr-status/<int:id>', methods=['POST'])
def update_pr_status(id):
    visit = PRVisit.query.get_or_404(id)
    new_status = request.form.get('visit_status')
    if new_status:
        visit.visit_status = new_status
        db.session.commit()
    return redirect(url_for('main.index'))

@bp.route('/add-pr-visit', methods=['GET', 'POST'])
def add_pr_visit():
    if request.method == 'POST':
        visit = PRVisit(
            pr_name=request.form['pr_name'],
            visit_start_time=datetime.strptime(request.form['visit_start_time'], '%H:%M'),
            client_name=request.form['client_name'],
            manager_incharge=request.form['manager_incharge'],
            visit_status=request.form['visit_status'],
            notes=request.form.get('notes', '')
        )
        db.session.add(visit)
        db.session.commit()
        return redirect(url_for('main.index'))
    
    pr_team = TeamMember.query.filter_by(role='PR', active=True).order_by(TeamMember.name).all()
    sales_managers = TeamMember.query.filter_by(role='SM', active=True).all()
    current_time = datetime.now().strftime('%H:%M')
    
    return render_template('add_pr_visit.html',
                          pr_team=pr_team,
                          sales_managers=sales_managers,
                          current_time=current_time)

@bp.route('/add-tc-activity', methods=['GET', 'POST'])
def add_tc_activity():
    if request.method == 'POST':
        activity = TCActivity(
            telecaller_name=request.form['telecaller_name'],
            manager_incharge=request.form['manager_incharge'],
            calls_made=int(request.form.get('calls_made', 0)),
            visits_booked=int(request.form.get('visits_booked', 0)),
            visits_confirmed=int(request.form.get('visits_confirmed', 0)),
            leads_acquired=int(request.form.get('leads_acquired', 0)),
            bucket_leads=int(request.form.get('bucket_leads', 0))
        )
        db.session.add(activity)
        db.session.commit()
        return redirect(url_for('main.index'))
    
    tc_team = TeamMember.query.filter_by(role='TC', active=True).all()
    sales_managers = TeamMember.query.filter_by(role='SM', active=True).all()
    
    return render_template('add_tc_activity.html',
                          tc_team=tc_team,
                          sales_managers=sales_managers)

@bp.route('/team', methods=['GET', 'POST'])
def team():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            member = TeamMember(
                name=request.form['name'],
                role=request.form['role'],
                active=True
            )
            db.session.add(member)
            
        elif action == 'toggle':
            member_id = int(request.form['member_id'])
            member = TeamMember.query.get_or_404(member_id)
            member.active = not member.active
            
        elif action == 'delete':
            member_id = int(request.form['member_id'])
            member = TeamMember.query.get_or_404(member_id)
            db.session.delete(member)
        
        db.session.commit()
        return redirect(url_for('main.team'))
    
    today = datetime.now().date()
    today_str = today.strftime('%Y-%m-%d')
    current_year = datetime.now().year
    
    pr_team = TeamMember.query.filter_by(role='PR').order_by(TeamMember.name).all()
    tc_team = TeamMember.query.filter_by(role='TC').order_by(TeamMember.name).all()
    sales_managers = TeamMember.query.filter_by(role='SM').order_by(TeamMember.name).all()
    
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