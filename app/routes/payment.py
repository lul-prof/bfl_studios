from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.booking import Booking
from app.models.payment import Payment
from app import db

bp = Blueprint('payment', __name__)

@bp.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def process_payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user owns the booking
    if booking.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('user.bookings'))
    
    # Check if payment already exists
    if booking.payment and booking.payment.status == 'completed':
        flash('Payment already completed', 'info')
        return redirect(url_for('user.bookings'))
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        
        # Create or update payment
        if not booking.payment:
            payment = Payment(
                booking_id=booking_id,
                amount=booking.total_amount,
                payment_method=payment_method
            )
            db.session.add(payment)
        else:
            booking.payment.payment_method = payment_method
            booking.payment.status = 'pending'
        
        try:
            # Here you would integrate with actual payment gateway
            # For now, we'll simulate successful payment
            booking.payment.status = 'completed'
            booking.status = 'confirmed'
            db.session.commit()
            flash('Payment processed successfully', 'success')
            return redirect(url_for('user.bookings'))
        except Exception as e:
            db.session.rollback()
            flash('Payment processing failed', 'danger')
    
    return render_template('payment/process.html', booking=booking)