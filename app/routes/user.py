from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models.booking import Booking
from app.models.review import Review
from app import db
import os
from werkzeug.utils import secure_filename
from datetime import datetime

bp = Blueprint('user', __name__, url_prefix='/user')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@bp.route('/dashboard')
@login_required
def dashboard():
    # Get user's upcoming bookings
    upcoming_bookings = Booking.query.filter(
        Booking.user_id == current_user.id,
        Booking.status != 'cancelled',
        Booking.start_time > datetime.utcnow()
    ).order_by(Booking.start_time).all()
    
    return render_template('user/dashboard.html', upcoming_bookings=upcoming_bookings)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.phone = request.form.get('phone')
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{current_user.id}_{file.filename}")
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profile_pics', filename)
                file.save(file_path)
                current_user.profile_picture = filename
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('user.dashboard'))
        
    return render_template('user/profile.html')

@bp.route('/bookings')
@login_required
def bookings():
    all_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    return render_template('user/bookings.html', bookings=all_bookings)

@bp.route('/booking/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        flash('You do not have permission to cancel this booking', 'danger')
        return redirect(url_for('user.bookings'))
        
    if booking.status == 'confirmed':
        flash('Cannot cancel a confirmed booking', 'danger')
        return redirect(url_for('user.bookings'))
        
    booking.status = 'cancelled'
    db.session.commit()
    flash('Booking cancelled successfully', 'success')
    return redirect(url_for('user.bookings'))

@bp.route('/booking/<int:booking_id>/review', methods=['GET', 'POST'])
@login_required
def add_review(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        flash('You do not have permission to review this booking', 'danger')
        return redirect(url_for('user.bookings'))
        
    if request.method == 'POST':
        review = Review(
            booking_id=booking_id,
            user_id=current_user.id,
            rating=int(request.form.get('rating')),
            comment=request.form.get('comment')
        )
        db.session.add(review)
        db.session.commit()
        flash('Review submitted successfully and pending approval', 'success')
        return redirect(url_for('user.bookings'))
        
    return render_template('user/review.html', booking=booking)