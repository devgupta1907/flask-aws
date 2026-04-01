from flask import render_template, redirect, url_for
from flask_login import current_user
from app import db
from app.blueprints.professional import professional
from app.models import Professional, ServiceRequest
from app.enums import ProfessionalStatus, ServiceRequestStatus
from app.utility import professional_login_required


@professional.route('/professional-dashboard')
@professional_login_required
def professional_dashboard():
    prof_id = int(current_user.get_id()[2:])
    prof = Professional.query.get_or_404(prof_id)
    return render_template('professionals_dashboard.html',
                           professional=prof,
                           professional_status=ProfessionalStatus,
                           service_requests=prof.service_requests,
                           request_status=ServiceRequestStatus)


@professional.route('/professional-dashboard/<int:request_id>/accept', methods=["POST"])
@professional_login_required
def accept_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    service_request.status = ServiceRequestStatus.ACCEPTED
    db.session.commit()
    return redirect(url_for('professional.professional_dashboard'))


@professional.route('/professional-dashboard/<int:request_id>/reject', methods=["POST"])
@professional_login_required
def reject_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    service_request.status = ServiceRequestStatus.REJECTED
    service_request.rating = 0
    db.session.commit()
    return redirect(url_for('professional.professional_dashboard'))