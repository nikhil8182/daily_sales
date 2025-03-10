from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, TCActivity
from datetime import datetime, date

bp = Blueprint('tc', __name__, url_prefix='/tc')

@bp.route('/')
def index():
    activities = TCActivity.query.order_by(TCActivity.date.desc()).all()
    return render_template('tc/index.html', activities=activities)

@bp.route('/new', methods=['GET', 'POST'])
def new_activity():
    if request.method == 'POST':
        activity = TCActivity(
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
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
        return redirect(url_for('tc.index'))
    
    return render_template('tc/new.html', today=date.today().strftime('%Y-%m-%d'))

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_activity(id):
    activity = TCActivity.query.get_or_404(id)
    
    if request.method == 'POST':
        activity.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        activity.telecaller_name = request.form['telecaller_name']
        activity.manager_incharge = request.form['manager_incharge']
        activity.calls_made = int(request.form.get('calls_made', 0))
        activity.visits_booked = int(request.form.get('visits_booked', 0))
        activity.visits_confirmed = int(request.form.get('visits_confirmed', 0))
        activity.leads_acquired = int(request.form.get('leads_acquired', 0))
        activity.bucket_leads = int(request.form.get('bucket_leads', 0))
        
        db.session.commit()
        return redirect(url_for('tc.index'))
    
    return render_template('tc/edit.html', activity=activity)

@bp.route('/delete/<int:id>', methods=['POST'])
def delete_activity(id):
    activity = TCActivity.query.get_or_404(id)
    db.session.delete(activity)
    db.session.commit()
    return redirect(url_for('tc.index'))