from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.booking import Booking
from app.models.studio import Studio
from app import db
from datetime import datetime

bp = Blueprint('booking', __name__)

@bp.route('/studios')
def studios():
    studios = Studio.query.filter_by(is_available=True).all()
    return render_template('booking/studios.html', studios=studios)

@bp.route('/book/<int:studio_id>', methods=['GET', 'POST'])
@login_required
def book_studio(studio_id):
    studio = Studio.query.get_or_404(studio_id)
    
    if request.method == 'POST':
        start_time = datetime.strptime(request.form.get('start_time'), '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(request.form.get('end_time'), '%Y-%m-%dT%H:%M')
        booking_type = request.form.get('booking_type')
        
        # Check for conflicts
        conflicts = Booking.query.filter(
            Booking.studio_id == studio_id,
            Booking.status != 'cancelled',
            ((Booking.start_time <= start_time) & (Booking.end_time > start_time)) |
            ((Booking.start_time < end_time) & (Booking.end_time >= end_time))
        ).first()
        
        if conflicts:
            flash('This time slot is already booked', 'danger')
            return redirect(url_for('booking.book_studio', studio_id=studio_id))
            
        # Calculate total amount
        duration = (end_time - start_time).total_seconds() / 3600  # hours
        if booking_type == 'hourly':
            total_amount = studio.hourly_rate * duration
        elif booking_type == 'half_day':
            total_amount = studio.half_day_rate
        else:
            total_amount = studio.full_day_rate
            
        booking = Booking(
            user_id=current_user.id,
            studio_id=studio_id,
            start_time=start_time,
            end_time=end_time,
            booking_type=booking_type,
            total_amount=total_amount
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return redirect(url_for('booking.payment', booking_id=booking.id))
        
    return render_template('booking/book.html', studio=studio)


@bp.route('/payment/<int:booking_id>')
@login_required
def payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        flash('You do not have permission to access this payment', 'danger')
        return redirect(url_for('user.bookings'))
    
    if booking.payment_status != 'pending':
        flash('This booking has already been paid for', 'info')
        return redirect(url_for('user.bookings'))
    
    return render_template('booking/payment.html', booking=booking)