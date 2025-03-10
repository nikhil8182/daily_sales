from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, PRVisit
from datetime import datetime

bp = Blueprint('pr', __name__, url_prefix='/pr')

@bp.route('/')
def index():
    visits = PRVisit.query.order_by(PRVisit.visit_start_time.desc()).all()
    return render_template('pr/index.html', visits=visits)

@bp.route('/new', methods=['GET', 'POST'])
def new_visit():
    if request.method == 'POST':
        visit = PRVisit(
            visit_start_time=datetime.strptime(request.form['visit_start_time'], '%Y-%m-%dT%H:%M'),
            client_name=request.form['client_name'],
            pr_name=request.form['pr_name'],
            manager_response=request.form.get('manager_response', ''),
            visit_status=request.form['visit_status'],
            visit_update=request.form.get('visit_update', ''),
            notes=request.form.get('notes', '')
        )
        db.session.add(visit)
        db.session.commit()
        return redirect(url_for('pr.index'))
    
    return render_template('pr/new.html')

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_visit(id):
    visit = PRVisit.query.get_or_404(id)
    
    if request.method == 'POST':
        visit.visit_start_time = datetime.strptime(request.form['visit_start_time'], '%Y-%m-%dT%H:%M')
        visit.client_name = request.form['client_name']
        visit.pr_name = request.form['pr_name']
        visit.manager_response = request.form.get('manager_response', '')
        visit.visit_status = request.form['visit_status']
        visit.visit_update = request.form.get('visit_update', '')
        visit.notes = request.form.get('notes', '')
        
        db.session.commit()
        return redirect(url_for('pr.index'))
    
    return render_template('pr/edit.html', visit=visit)

@bp.route('/delete/<int:id>', methods=['POST'])
def delete_visit(id):
    visit = PRVisit.query.get_or_404(id)
    db.session.delete(visit)
    db.session.commit()
    return redirect(url_for('pr.index'))