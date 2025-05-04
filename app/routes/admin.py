from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.booking import Booking
from app.models.studio import Studio
from app.models.user import User
from app.models.review import Review
from app import db
from datetime import datetime, timedelta
from functools import wraps

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get statistics
    stats = {
        'total_bookings': Booking.query.count(),
        'total_revenue': sum(booking.total_amount for booking in Booking.query.all()),
        'active_users': User.query.filter_by(is_verified=True).count(),
        'pending_reviews': Review.query.filter_by(is_approved=False).count()
    }
    
    # Get recent bookings
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', stats=stats, recent_bookings=recent_bookings)

@bp.route('/studios', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_studios():
    if request.method == 'POST':
        studio = Studio(
            name=request.form.get('name'),
            description=request.form.get('description'),
            hourly_rate=float(request.form.get('hourly_rate')),
            half_day_rate=float(request.form.get('half_day_rate')),
            full_day_rate=float(request.form.get('full_day_rate')),
            equipment=request.form.get('equipment')
        )
        db.session.add(studio)
        db.session.commit()
        flash('Studio added successfully', 'success')
        return redirect(url_for('admin.manage_studios'))
        
    studios = Studio.query.all()
    return render_template('admin/studios.html', studios=studios)

@bp.route('/bookings')
@login_required
@admin_required
def manage_bookings():
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings)

@bp.route('/booking/<int:booking_id>/status', methods=['POST'])
@login_required
@admin_required
def update_booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    new_status = request.form.get('status')
    if new_status in ['confirmed', 'cancelled']:
        booking.status = new_status
        db.session.commit()
        flash(f'Booking status updated to {new_status}', 'success')
    return redirect(url_for('admin.manage_bookings'))

@bp.route('/reviews')
@login_required
@admin_required
def manage_reviews():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('admin/reviews.html', reviews=reviews)

@bp.route('/review/<int:review_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_review(review_id):
    review = Review.query.get_or_404(review_id)
    review.is_approved = True
    db.session.commit()
    flash('Review approved successfully', 'success')
    return redirect(url_for('admin.manage_reviews'))

@bp.route('/studio/<int:studio_id>/status', methods=['POST'])
@login_required
@admin_required
def update_studio_status(studio_id):
    studio = Studio.query.get_or_404(studio_id)
    data = request.get_json()
    
    try:
        studio.is_available = data.get('is_available', False)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/manage_users')
@login_required
def manage_users():
    # Check if user is admin
    if not current_user.is_administrator:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get all users with optional filters
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = User.query
    if search:
        query = query.filter(
            or_(
                User.email.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%')
            )
        )
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('admin/manage_users.html', users=users, search=search)

@bp.route('/manage_users/<int:user_id>', methods=['POST'])
@login_required
def update_user_status(user_id):
    if not current_user.is_administrator:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    action = request.form.get('action')
    
    if action == 'verify':
        user.is_verified = True
        flash(f'User {user.email} has been verified.', 'success')
    elif action == 'unverify':
        user.is_verified = False
        flash(f'User {user.email} has been unverified.', 'success')
    elif action == 'make_admin':
        user.role = 'admin'
        user.is_admin = True
        flash(f'User {user.email} has been made an admin.', 'success')
    elif action == 'remove_admin':
        user.role = 'user'
        user.is_admin = False
        flash(f'Admin privileges removed from {user.email}.', 'success')
    
    db.session.commit()
    return redirect(url_for('admin.manage_users'))