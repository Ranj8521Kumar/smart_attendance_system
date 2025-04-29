from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify
from app.models.analytics import Analytics

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Render the analytics dashboard
    """
    if 'teacher_id' not in session:
        return redirect(url_for('auth.home'))
    
    # Get filter options
    batches = Analytics.get_batches()
    branches = Analytics.get_branches()
    subjects = Analytics.get_subjects()
    
    # Get analytics data without any filters
    batch_data = Analytics.get_batch_analytics()
    
    return render_template(
        'analytics.html',
        batches=batches,
        branches=branches,
        subjects=subjects,
        batch_data=batch_data,
        active_filters={}
    )

@analytics_bp.route('/filter', methods=['GET'])
def filter_analytics():
    """
    Filter analytics based on selected criteria
    """
    if 'teacher_id' not in session:
        return redirect(url_for('auth.home'))
    
    # Get filter parameters
    batch = request.args.get('batch')
    branch = request.args.get('branch')
    subject = request.args.get('subject')
    
    # Get filter options for dropdowns
    batches = Analytics.get_batches()
    branches = Analytics.get_branches()
    subjects = Analytics.get_subjects()
    
    # Store active filters
    active_filters = {}
    if batch:
        active_filters['batch'] = batch
    if branch:
        active_filters['branch'] = branch
    if subject:
        active_filters['subject'] = subject
        
    # Get data based on filters
    if batch and branch and subject:
        # Filter by batch, branch, and subject - show student attendance
        students = Analytics.get_student_analytics(batch, branch, subject)
        attendance_data = Analytics.get_student_attendance(subject)
        
        return render_template(
            'analytics_student_attendance.html',
            batches=batches,
            branches=branches,
            subjects=subjects,
            students=students,
            attendance_data=attendance_data,
            active_filters=active_filters
        )
    
    elif batch and branch:
        # Filter by batch and branch - show subject analytics
        subject_data = Analytics.get_subject_analytics(batch, branch)
        
        return render_template(
            'analytics_subjects.html',
            batches=batches,
            branches=branches,
            subjects=subjects,
            subject_data=subject_data,
            active_filters=active_filters
        )
    
    elif batch:
        # Filter by batch - show branch analytics
        branch_data = Analytics.get_branch_analytics(batch)
        
        return render_template(
            'analytics_branches.html',
            batches=batches,
            branches=branches,
            subjects=subjects,
            branch_data=branch_data,
            active_filters=active_filters
        )
    
    else:
        # No filters - show batch analytics
        batch_data = Analytics.get_batch_analytics()
        
        return render_template(
            'analytics.html',
            batches=batches,
            branches=branches,
            subjects=subjects,
            batch_data=batch_data,
            active_filters=active_filters
        )
