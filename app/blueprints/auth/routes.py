from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from app import db
from app.blueprints.auth import auth
from app.models import Customer, Professional, Admin, Service
from app.enums import CustomerStatus, ProfessionalStatus
from app.utility import validate_pincode, allowed_file
from app.utils.s3 import upload_resume_to_s3
import os


@auth.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("Email")
        password = request.form.get('Password')
        admin = Admin.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.password, password):
            login_user(admin)
            flash(f"Welcome Back, {admin.name}!", "success")
            return redirect(url_for('admin.admin_dashboard'))
        flash("Wrong Admin Email or Password", 'danger')
    return render_template('login.html', usertype="admin")


@auth.route("/professional-login", methods=["GET", "POST"])
def professional_login():
    if request.method == "POST":
        email = request.form.get("Email")
        password = request.form.get('Password')
        professional = Professional.query.filter_by(email=email).first()
        if professional and check_password_hash(professional.password, password):
            if professional.status == ProfessionalStatus.BLOCKED:
                flash("Access Denied! You Are Blocked By The Admin", "danger")
                return redirect(url_for('main.home'))
            login_user(professional)
            flash("You Are Now Logged In!", "success")
            return redirect(url_for('professional.professional_dashboard'))
        flash("Error. Please Check Your Credentials ", "danger")
    return render_template('login.html', usertype="professional")


@auth.route("/customer-login", methods=["GET", "POST"])
def customer_login():
    if request.method == "POST":
        email = request.form.get("Email")
        password = request.form.get('Password')
        customer = Customer.query.filter_by(email=email).first()
        if customer and check_password_hash(customer.password, password):
            if customer.status == CustomerStatus.BLOCKED:
                flash("Access Denied! You Are Blocked By The Admin", "danger")
                return redirect(url_for('main.home'))
            login_user(customer)
            flash("You Are Now Logged In!", "success")
            return redirect(url_for('main.home'))
        flash("Error. Please Check Your Credentials ", "danger")
    return render_template('login.html', usertype="customer")


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You Have Been Logged Out.', 'info')
    return redirect(url_for('main.home'))


@auth.route('/professional-register', methods=['GET', 'POST'])
def professional_register():
    if request.method == 'POST':
        name = request.form.get('professionalName')
        email = request.form.get('professionalEmail')
        password = request.form.get('professionalPassword')
        work_exp = request.form.get('professionalExp')
        resume = request.files['professionalResume']
        service_id = request.form.get('professionalService')

        existing_professional = Professional.query.filter_by(email=email).first()
        if existing_professional:
            flash('Email Already Registered. Please Use A Different Email Address.', 'danger')
            return redirect(url_for('auth.professional_register'))

        # resume_filename = None
        s3_key = None
        if resume and allowed_file(resume.filename):
            # resume_filename = f"{email}_resume.pdf"
            s3_key = upload_resume_to_s3(resume, email)
            # resume.save(os.path.join(current_app.config['RESUME_FOLDER'], resume_filename))

        new_professional = Professional(name=name,
                                        email=email,
                                        work_exp=work_exp,
                                        resume=s3_key,
                                        service_id=service_id)
        new_professional.set_password(password)
        db.session.add(new_professional)
        db.session.commit()

        flash('Great! Your Details Has Been Passed To The Admin.', 'success')
        return redirect(url_for('auth.professional_login'))

    all_services = Service.query.all()
    return render_template('professional_registration.html', services=all_services)


@auth.route("/customer-register", methods=["GET", "POST"])
def customer_register():
    if request.method == "POST":
        name = request.form.get('customerName')
        email = request.form.get('customerEmail')
        pincode = int(request.form.get('customerPincode'))
        password = request.form.get('customerPassword')

        existing_customer = Customer.query.filter_by(email=email).first()
        if existing_customer:
            flash('Email Already Registered. Please Use Different Email Address.', 'danger')
            return redirect(url_for('auth.customer_register'))

        if validate_pincode(pincode) is True:
            new_customer = Customer(name=name, email=email, pincode=pincode)
            new_customer.set_password(password)
            db.session.add(new_customer)
            db.session.commit()
            flash("Your Account Has Been Created!", "success")
            return redirect(url_for('auth.customer_login'))
        elif validate_pincode(pincode) is False:
            flash("Invalid Pincode.", 'danger')
        else:
            flash("Internal Issue Occurred!", 'warning')
        return redirect(url_for('auth.customer_register'))

    return render_template('customer_registration.html')