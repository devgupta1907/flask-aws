from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from app import db
from app.blueprints.main import main
from app.models import Category, Service, ServiceRequest, Professional
from app.enums import ProfessionalStatus
from app.utility import customer_login_required, search_by_name


@main.route("/")
def home():
    all_services = Service.query.limit(3).all()
    service_results = search_by_name(Service)
    if service_results:
        return render_template('home.html', services=service_results)
    return render_template('home.html', services=all_services)


@main.route("/services")
def services():
    all_services = Service.query.all()
    service_results = search_by_name(Service)
    if service_results:
        return render_template("services.html", services=service_results)
    return render_template("services.html", services=all_services)


@main.route("/services/<int:service_id>/professionals")
@customer_login_required
def get_professionals_of_service(service_id):
    service = Service.query.filter_by(id=service_id).first()
    if service:
        desired_professionals = Professional.query.filter_by(
            service_id=service.id,
            status=ProfessionalStatus.ACTIVE).all()
        if desired_professionals:
            return render_template("get_professionals_of_service.html",
                                   desired_professionals=desired_professionals,
                                   service=service)
        flash('No Professionals Available For This Service', 'info')
        return redirect(url_for('main.services'))
    return redirect(url_for('main.home'))


@main.route("/services/<int:service_id>/professionals/<int:professional_id>/create",
            methods=['POST'])
@customer_login_required
def create_service_request(service_id, professional_id):
    cust_id = int(current_user.get_id()[2:])
    service = Service.query.get_or_404(service_id)
    professional = Professional.query.get_or_404(professional_id)
    service_request = ServiceRequest(service_id=service_id,
                                     customer_id=cust_id,
                                     professional_id=professional_id)
    db.session.add(service_request)
    db.session.commit()
    flash(f'Request Created For {service.name} With {professional.name}!', 'success')
    return redirect(url_for('main.services'))


@main.route('/categories')
def categories():
    all_categories = Category.query.all()
    category_results = search_by_name(Category)
    if category_results:
        return render_template('categories.html', categories=category_results)
    return render_template('categories.html', categories=all_categories)


@main.route('/categories/<int:category_id>/services')
def get_services_of_category(category_id):
    category = Category.query.filter_by(id=category_id).first()
    if category:
        available_services = category.services
        if available_services:
            return render_template('services.html',
                                   services=available_services,
                                   category=category.name)
        flash("No Services Available Under This Category", 'info')
    return redirect(url_for('main.categories'))