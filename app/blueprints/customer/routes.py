from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from app import db
from app.blueprints.customer import customer
from app.utility import customer_login_required, validate_pincode

from app.models import ServiceRequest, Customer
from app.enums import ServiceRequestStatus


@customer.route('/customer-dashboard')
@customer_login_required
def customer_dashboard():
    cust_id = int(current_user.get_id()[2:])
    customer = Customer.query.get_or_404(cust_id)
    return render_template('customer_dashboard.html', 
                           customer=customer,
                           request_status=ServiceRequestStatus, 
                           service_requests=customer.service_requests)


@customer.route('/customer-dashboard/update-profile', methods=["GET", "POST"])
@customer_login_required
def update_customer():
    cust_id = int(current_user.get_id()[2:])
    customer = Customer.query.get_or_404(cust_id)
    if request.method == "POST":
        new_customer_name = request.form.get("customerName")
        new_customer_pincode = int(request.form.get("customerPincode"))
        
        if validate_pincode(new_customer_pincode) is True:
            customer.name = new_customer_name
            customer.pincode = new_customer_pincode
            db.session.commit()
            flash("Details Updated Successfully", 'success')
            return redirect(url_for('customer_dashboard'))
        
        elif validate_pincode(new_customer_pincode) is False:
            flash("Invalid Pincode. Please Put Your Correct Pincode", 'danger')
        else:
            flash("Internal Issue Occurred! Please Try Again Later.", 'warning')
            
    return render_template('update_customer.html', 
                           customer=customer)


@customer.route('/customer-dashboard/<int:request_id>/rate')
@customer_login_required
def rate_service(request_id):
    
    existing_service_request = ServiceRequest.query.filter_by(id=request_id).first()
    if not existing_service_request:
        flash('Service Request Does Not Exist', 'danger')
        return redirect(url_for('customer_dashboard'))

    if existing_service_request.status == ServiceRequestStatus.REQUESTED:
        flash("The request is in REQUESTED state. Please wait till the further update 🙂", "info")
        return redirect(url_for('customer_dashboard'))
    else:
        return render_template('rating.html', 
                               request_id=request_id)


@customer.route('/customer-dashboard/<int:request_id>/close', methods=["POST"])
@customer_login_required
def close_request(request_id):
    rating = request.form.get('rating')
    
    existing_service_request = ServiceRequest.query.get_or_404(request_id)
    existing_service_request.rating = int(rating)
    existing_service_request.status = ServiceRequestStatus.CLOSED
    db.session.commit()
    flash('Service Request Closed. Thank You For Rating Our Service Professional', 'success')
    return redirect(url_for('customer_dashboard'))