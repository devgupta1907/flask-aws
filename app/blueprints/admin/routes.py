from flask import render_template, request, redirect, url_for, flash, send_from_directory
from app import db
from app.blueprints.admin import admin
from app.utility import admin_login_required
from app.utility import search_by_name, search_by_name_and_email
from app.utility import chart_for_professional_services, chart_for_category_services
from app.models import Category, Service, ServiceRequest, Customer, Professional
from app.enums import CustomerStatus, ProfessionalStatus, ServiceRequestStatus
from app.utils.s3 import generate_resume_url



@admin.route("/admin")
@admin_login_required
def admin_dashboard():
    professionals_in_service_graph = chart_for_professional_services()
    services_in_category_graph = chart_for_category_services()
    
    service_count = Service.query.count()
    customer_count = Customer.query.count()
    professional_count = Professional.query.filter_by(status=ProfessionalStatus.ACTIVE).count()
    sr_closed_count = ServiceRequest.query.filter_by(status=ServiceRequestStatus.CLOSED).count()
    return render_template("admin_dashboard.html", 
                           prof_chart=professionals_in_service_graph,
                           service_chart=services_in_category_graph,
                           service_count=service_count,
                           customer_count=customer_count,
                           professional_count=professional_count,
                           sr_closed_count=sr_closed_count)


@admin.route("/admin/services")
@admin_login_required
def admin_services():
    all_services = Service.query.all()
    service_results = search_by_name(Service)
    if service_results:
        return render_template("services_admin.html", 
                               services=service_results)
    return render_template("services_admin.html", 
                           services=all_services)


@admin.route("/admin/services/add_service", methods=['GET', 'POST'])
@admin_login_required
def add_service():
    if request.method == "POST":
        service_name = request.form.get("serviceName")
        service_price = request.form.get("servicePrice")
        service_category = request.form.get("serviceCategory")
        service_description = request.form.get("serviceDescription")
        
        existing_service = Service.query.filter_by(name=service_name).first()
        if existing_service:
            flash(f'Error Adding Service. service Already Exists.', 'danger')
            return redirect(url_for('admin.add_service'))
            
        new_service = Service(name=service_name, 
                              price=service_price, 
                              description=service_description,
                              category_id=service_category)
        db.session.add(new_service)
        db.session.commit()
        flash("Service Added Successfully!", "success")
        return redirect(url_for('admin.admin_services'))
    all_categories = Category.query.all()
    return render_template("add_service.html", categories=all_categories)


@admin.route("/admin/service/<int:service_id>/update", methods=['GET', 'POST'])
@admin_login_required
def update_service(service_id):
    service = Service.query.get_or_404(service_id)
    if request.method == "POST":
        service_name = request.form.get("serviceName")
        service_price = request.form.get("servicePrice")
        service_description = request.form.get("serviceDescription")
        
        existing_service = Service.query.filter(Service.name == service_name, 
                                                Service.id != service_id).first()
        if existing_service:
            flash(f'A Service With This Name Already Exists. Please Choose Different Name', 'danger')
            return redirect(url_for('admin.update_service', service_id=service_id))
        
        service.name = service_name
        service.price = service_price
        service.description = service_description
        db.session.commit()
        
        flash("Service Updated Successfully!", "success")
        return redirect(url_for('admin.admin_services'))
    return render_template("update_service.html", service=service)


@admin.route("/admin/service/<int:service_id>/delete", methods=['POST'])
@admin_login_required
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    if len(service.professionals) == 0:
        db.session.delete(service)
        db.session.commit()
        flash("Service Deleted Successfully", 'success')
        return redirect(url_for('admin.admin_services'))
    return redirect(url_for('admin.admin_services'))


@admin.route("/admin/professionals")
@admin_login_required
def admin_professionals():
    all_professionals = Professional.query.all()
    professional_results = search_by_name_and_email(Professional)
    if professional_results:
        return render_template("professionals_admin.html", 
                               professionals=professional_results,
                               professional_status=ProfessionalStatus)
    return render_template("professionals_admin.html", 
                           professionals=all_professionals,
                           professional_status=ProfessionalStatus)

# @admin.route("/static/resume/<filename>")
# def get_professional_resume(filename):
#     return send_from_directory(admin.config["RESUME_FOLDER"], filename)
@admin.route("/resume/<path:s3_key>")
@admin_login_required
def get_professional_resume(s3_key):
    url = generate_resume_url(s3_key)
    return redirect(url)


@admin.route('/admin/professional/<int:professional_id>/activate', methods=['POST'])
@admin_login_required
def activate_professional(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    professional.status = ProfessionalStatus.ACTIVE
    db.session.commit()
    return redirect(url_for('admin.admin_professionals'))


@admin.route('/admin/professional/<int:professional_id>/block', methods=['POST'])
@admin_login_required
def block_professional(professional_id):
    professional = Professional.query.get_or_404(professional_id)
    professional.status = ProfessionalStatus.BLOCKED
    db.session.commit()
    return redirect(url_for('admin.admin_professionals'))


@admin.route('/admin/customers')
@admin_login_required
def admin_customers():
    all_customers = Customer.query.all()
    customer_results = search_by_name_and_email(Customer)
    if customer_results:
        return render_template("customers_admin.html", 
                               customers=customer_results,
                               customer_status=CustomerStatus)
    return render_template("customers_admin.html", 
                           customers=all_customers,
                           customer_status=CustomerStatus)


@admin.route('/admin/customer/<int:customer_id>/block', methods=['POST'])
@admin_login_required
def block_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    customer.status = CustomerStatus.BLOCKED
    db.session.commit()
    return redirect(url_for('admin.admin_customers'))


@admin.route('/admin/customer/<int:customer_id>/unblock', methods=['POST'])
@admin_login_required
def unblock_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    customer.status = CustomerStatus.ACTIVE
    db.session.commit()
    return redirect(url_for('admin.admin_customers'))


@admin.route("/admin/categories/add_category", methods=["GET", "POST"])
@admin_login_required
def add_category():
    if request.method == "POST":
        category_name = request.form.get("category_name")
        
        existing_category = Category.query.filter_by(name=category_name).first()
        if existing_category:
            flash(f'Error Adding Category. Category Already Exists.', 'danger')
            return redirect(url_for('admin.add_category'))
        
        new_category = Category(name=category_name)
        db.session.add(new_category)
        db.session.commit()
        flash("Category added successfully!", "success")
        return redirect(url_for('admin.add_category'))
    all_categories = Category.query.all()
    return render_template("add_category.html", 
                           categories=all_categories,
                           update=False)

@admin.route("/admin/category/<int:category_id>/update", methods=["GET", "POST"])
@admin_login_required
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    if request.method == "POST":
        category_name = request.form.get("category_name")
        
        existing_category = Category.query.filter(Category.id != category_id, Category.name == category_name).first()
        if existing_category:
            flash(f'Error Adding Category. Category Already Exists.', 'danger')
            return redirect(url_for('admin.add_category'))
        
        category.name = category_name
        db.session.commit()
        flash("Category updated successfully!", "success")
        return redirect(url_for('admin.add_category'))
    return render_template("add_category.html",
                           category=category,
                           update=True)