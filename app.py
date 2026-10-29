from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

import os
from werkzeug.utils import secure_filename

from flask import send_file
import pandas as pd

from datetime import datetime, date

app = Flask(__name__)

app.secret_key = "placement123"

app.config.from_object("config.Config")

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# ===================================
# Student Model
# ===================================

class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    rollno = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    resume = db.Column(db.String(255))
    gender = db.Column(db.String(20))
    dob = db.Column(db.String(20))
    skills = db.Column(db.Text)
    
    year_of_passing = db.Column(db.String(10))

   
# ===================================
# Company Model
# ===================================

class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
     
    company_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    package = db.Column(db.String(50), nullable=False)
    eligibility = db.Column(db.String(50), nullable=False)
    
    location = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    deadline = db.Column(db.Date)
    
    department = db.Column(db.String(100), nullable=False)
    posted_date = db.Column(db.Date)
    
    vacancies = db.Column(db.Integer, default=1)

    employment_type = db.Column(db.String(50), default="Full Time")

    work_mode = db.Column(db.String(50), default="On-site")

    experience = db.Column(db.String(50), default="Freshers")

    skills_required = db.Column(db.Text)

    job_description = db.Column(db.Text)
    

# ===================================
# Application Model
# ===================================

class Application(db.Model):
    __tablename__ = "applications"
    
   # student_id = db.Column(db.Integer)

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer,db.ForeignKey("companies.id"),nullable=False)
    
    student_name = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default="Pending")
    
    applied_date = db.Column(db.Date)
    rejection_reason = db.Column(db.Text)

# ===================================
# Recruiter Model
# ===================================
class Recruiter(db.Model):
    __tablename__ = "recruiters"

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    recruiter_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default="Pending")
    
# ===================================
# Recruitment Stages Model
# ===================================
class RecruitmentStage(db.Model):
    __tablename__ = "recruitment_stages"

    id = db.Column(db.Integer, primary_key=True)

    job_id = db.Column(
        db.Integer,
        db.ForeignKey("companies.id"),
        nullable=False
    )

    stage_name = db.Column(
        db.String(100),
        nullable=False
    )

    stage_order = db.Column(
        db.Integer,
        nullable=False
    )
    
# ===================================
# ApplicationProgress Model
# ===================================
class ApplicationProgress(db.Model):

    __tablename__ = "application_progress"

    id = db.Column(db.Integer, primary_key=True)

    application_id = db.Column(db.Integer, nullable=False)

    stage_id = db.Column(db.Integer, nullable=False)

    status = db.Column(db.String(30),default="Pending")

    updated_at = db.Column(db.DateTime,default=datetime.utcnow)
    
    remarks = db.Column(db.String(255),default="")
    
    job_id = db.Column(db.Integer, nullable=False)
    
# ===================================
# Home
# ===================================

@app.route("/")
def home():
    return render_template("index.html")

# ===================================
# Student Register
# ===================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        existing_roll = Student.query.filter_by(
            rollno=request.form["rollno"]
        ).first()

        if existing_roll:
            return "Roll Number already exists!"

        existing_email = Student.query.filter_by(
            email=request.form["email"]
        ).first()

        if existing_email:
            return "Email already registered!"

        student = Student(
            rollno=request.form["rollno"],
            name=request.form["name"],
            department=request.form["department"],
            cgpa=float(request.form["cgpa"]),
            email=request.form["email"],
            phone=request.form["phone"],
            password=request.form["password"],
            gender = request.form["gender"],
            dob = request.form["dob"],
            year_of_passing=request.form["year_of_passing"]
        )

        db.session.add(student)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


# ===================================
# Student Login
# ===================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        student = Student.query.filter_by(
            email=email,
            password=password
        ).first()

        if student:

            session["student_id"] = student.id
            session["student_name"] = student.name

            return redirect('/student/dashboard')

        return "Invalid Email or Password"

    return render_template("login.html")

# ===================================
# Student Profile
# ===================================

@app.route("/profile")
def profile():

    student = Student.query.get(
        session["student_id"]
    )

    return render_template(
        "student/profile.html",
        student=student
    )

# ===================================
# Student Dashboard
# ===================================

@app.route('/student/dashboard')
def student_dashboard():

    student_id = session.get('student_id')

    # Student details
    student = Student.query.get(student_id)
    
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")

    jobs_posted_on_date = None
    jobs_applied_on_date = None

    # Count only eligible jobs that are currently open

    today = date.today()

    available_jobs = 0

    all_companies = Company.query.all()

    for company in all_companies:

        # Check department eligibility
        if company.department:

            departments = [d.strip() for d in company.department.split(",")]

            # Count only if:
            # 1. Student department is eligible
            # 2. Application has started
            # 3. Application deadline is not over

            if (
                    student.department in departments
                    and company.start_date <= today
                    and company.deadline >= today
                ):
                    available_jobs += 1

    # Applied jobs count
    applied_jobs = Application.query.filter_by(
        student_name=session["student_name"]
    ).count()

    resume_uploaded = True if student.resume else False
    
    if from_date and to_date:

        from_date_obj = datetime.strptime(
            from_date,
            "%Y-%m-%d"
        ).date()

        to_date_obj = datetime.strptime(
            to_date,
            "%Y-%m-%d"
        ).date()

        jobs_posted_on_date = 0

        companies = Company.query.filter(
            Company.posted_date >= from_date_obj,
            Company.posted_date <= to_date_obj
        ).all()

        today = date.today()

        for company in companies:

            departments = company.department.split(",")

            if (
                student.department in departments
                and company.start_date <= today
                and company.deadline >= today
            ):
                jobs_posted_on_date += 1

        jobs_applied_on_date = Application.query.filter(
            Application.student_name == session["student_name"],
            Application.applied_date >= from_date_obj,
            Application.applied_date <= to_date_obj
        ).count()

    return render_template(
        'student/dashboard.html',
        available_jobs=available_jobs,
        applied_jobs=applied_jobs,
        resume_uploaded=resume_uploaded,
        student=student,
        from_date=from_date,
        to_date=to_date,
        jobs_posted_on_date=jobs_posted_on_date,
        jobs_applied_on_date=jobs_applied_on_date,
    )
# ===================================
# Admin Login
# ===================================

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            
            return redirect("/admin")

        return "Invalid Admin Login"

    return render_template("admin_login.html")

# ===================================
# Recruiter Register
# ===================================

@app.route("/recruiter_register", methods=["GET", "POST"])
def recruiter_register():

    if request.method == "POST":

        recruiter = Recruiter(
            company_name=request.form["company_name"],
            recruiter_name=request.form["recruiter_name"],
            email=request.form["email"],
            password=request.form["password"],
            status="Pending"
        )

        db.session.add(recruiter)
        db.session.commit()

        return "Registration Successful. Waiting for Admin Approval."

    return render_template("recruiter_register.html")

# ===================================
# Recruiter Login
# ===================================

@app.route("/recruiter_login", methods=["GET", "POST"])
def recruiter_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        recruiter = Recruiter.query.filter_by(
            email=email,
            password=password
        ).first()

        if recruiter:

            if recruiter.status == "Approved":

                session["recruiter_id"] = recruiter.id
                session["company_name"] = recruiter.company_name

                return redirect("/recruiter_dashboard")

            else:
                return "Waiting for Admin Approval"

        return "Invalid Email or Password"

    return render_template("recruiter_login.html")

# ===================================
# Recruiter Dashboard
# ===================================

@app.route("/recruiter_dashboard")
def recruiter_dashboard():

    if "recruiter_id" not in session:
        return redirect("/recruiter_login")

    companies = Company.query.filter_by(
        company_name=session["company_name"]
    ).all()

    applications = Application.query.filter_by(
        company_name=session["company_name"]
    ).all()

    selected = Application.query.filter_by(
        company_name=session["company_name"],
        status="Selected"
    ).all()

    rejected = Application.query.filter_by(
        company_name=session["company_name"],
        status="Rejected"
    ).all()

    return render_template(
        "recruiter/dashboard.html",
        company_name=session["company_name"],
        companies=companies,
        total_drives=len(companies),
        total_applications=len(applications),
        selected_count=len(selected),
        rejected_count=len(rejected)
    )

@app.route("/recruiter_applications")
def recruiter_applications():

    if "company_name" not in session:
        return redirect("/recruiter_login")

    applications = Application.query.filter_by(
        company_name=session["company_name"]
    ).all()

    return render_template(
        "recruiter/applications.html",
        applications=applications
    )
    
    
@app.route("/selected_students")
def selected_students():

    if "company_name" not in session:
        return redirect("/recruiter_login")

    applications = Application.query.filter_by(
        company_name=session["company_name"],
        status="Selected"
    ).all()

    return render_template(
        "recruiter/selected_students.html",
        applications=applications
    )
    
@app.route("/rejected_students")
def rejected_students():

    if "company_name" not in session:
        return redirect("/recruiter_login")

    applications = Application.query.filter_by(
        company_name=session["company_name"],
        status="Rejected"
    ).all()

    return render_template(
        "recruiter/rejected_students.html",
        applications=applications
    )

# ===================================
# Students Profile (Recruiter side)
# ===================================
@app.route("/view_student/<student_name>")
def view_student(student_name):

    if "company_name" not in session:
        return redirect("/recruiter_login")

    student = Student.query.filter_by(
        name=student_name
    ).first()

    return render_template(
        "recruiter/student_profile.html",
        student=student
    )

# ===================================
# Add Placement Drive
# ===================================

@app.route("/add_drive", methods=["GET", "POST"])
def add_drive():

    if request.method == "POST":

        departments = request.form.getlist("department")
        
        vacancies = int(request.form["vacancies"])

        employment_type = request.form["employment_type"]

        work_mode = request.form["work_mode"]

        experience = request.form["experience"]

        skills_required = request.form["skills_required"]

        job_description = request.form["job_description"]
        
        
        if not departments:
            return "Please select at least one eligible department."

        department = ",".join(departments)

        company = Company(
        company_name=session["company_name"],
        role=request.form["role"],
        package=request.form["package"],
        eligibility=request.form["eligibility"],
        location=request.form["location"],
        
        vacancies=vacancies,
        employment_type=employment_type,
        work_mode=work_mode,
        experience=experience,
        skills_required=skills_required,
        job_description=job_description,

        start_date=datetime.strptime(
            request.form["start_date"],
            "%Y-%m-%d"
        ).date(),

        deadline=datetime.strptime(
            request.form["deadline"],
            "%Y-%m-%d"
        ).date(),

        department=department,

        posted_date=date.today()
    )

        db.session.add(company)
        db.session.commit()

        return redirect("/recruiter_dashboard")

    return render_template("recruiter/add_drive.html")


# ===================================
# Edit Profile
# ===================================
@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():

    if "student_id" not in session:
        return redirect("/login")

    student = Student.query.get(session["student_id"])

    if request.method == "POST":

        student.name = request.form["name"]
        student.department = request.form["department"]
        student.cgpa = request.form["cgpa"]
        student.email = request.form["email"]
        student.phone = request.form["phone"]
        student.gender = request.form["gender"]
        student.dob = request.form["dob"]
        student.skills = request.form["skills"]

        resume = request.files.get("resume")

        if resume and resume.filename != "":

            filename = secure_filename(resume.filename)

            resume.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

            student.resume = filename

        db.session.commit()

        return redirect("/profile")


    return render_template(
        "student/edit_profile.html",
        student=student
    )
    


# ===================================
# Admin Dashboard
# ===================================

@app.route("/admin")
def admin_dashboard():

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    jobs_posted_on_date = None
    students_applied_on_date = None

    if start_date and end_date:

        start_date_obj = datetime.strptime(
            start_date,
            "%Y-%m-%d"
        ).date()

        end_date_obj = datetime.strptime(
            end_date,
            "%Y-%m-%d"
        ).date()

        jobs_posted_on_date = Company.query.filter(
            Company.posted_date.between(start_date_obj, end_date_obj)
        ).count()

        students_applied_on_date = Application.query.filter(
            Application.applied_date.between(start_date_obj, end_date_obj)
        ).count()

    return render_template(
        "admin/dashboard.html",
        start_date=start_date,
        end_date=end_date,
        jobs_posted_on_date=jobs_posted_on_date,
        students_applied_on_date=students_applied_on_date
    )
# ===================================
# Add Company
# ===================================

@app.route("/add_company", methods=["GET", "POST"])
def add_company():

    if request.method == "POST":

        company = Company(
            company_name=request.form["company_name"],
            role=request.form["role"],
            package=request.form["package"],
            eligibility=request.form["eligibility"]
        )

        db.session.add(company)
        db.session.commit()

        return redirect("/companies")

    return render_template("admin/add_company.html")


# ===================================
# View Students
# ===================================

@app.route("/students")
def students():

    students = Student.query.all()

    return render_template(
        "admin/students.html",
        students=students
    )


# ===================================
# View Companies
# ===================================

@app.route("/companies")
def companies():

    if "student_id" not in session:
        return redirect("/login")

    student = Student.query.get(session["student_id"])

    all_companies = Company.query.all()

    eligible_companies = []

    for company in all_companies:

        # Skip old records with no department
        if not company.department:
            continue

        departments = company.department.split(",")

        if student.department in departments:
            eligible_companies.append(company)

    return render_template(
    "student/companies.html",
    companies=eligible_companies,
    today=date.today()
)

# ===================================
# Apply Job
# ===================================

@app.route("/apply/<int:id>")
def apply(id):

    if "student_name" not in session:
        return redirect("/student_login")

    company = Company.query.get_or_404(id)

    # Check if already applied
    existing_application = Application.query.filter_by(
        student_name=session["student_name"],
        company_name=company.company_name,
        role=company.role
    ).first()

    if existing_application:
        return """
        <h3 style='color:red; text-align:center; margin-top:50px;'>
            You have already applied for this job!
        </h3>
        <div style='text-align:center; margin-top:20px;'>
            <a href='/companies'>Back to Available Jobs</a>
        </div>
        """

    # -----------------------------
    # Create Application
    # -----------------------------

    application = Application(
        job_id=company.id,
        student_name=session["student_name"],
        company_name=company.company_name,
        role=company.role,
        status="Pending",
        applied_date=date.today()
    )

    db.session.add(application)
    db.session.commit()

    # -----------------------------
    # Create Recruitment Progress
    # -----------------------------

    stages = RecruitmentStage.query.filter_by(
        job_id=company.id
    ).order_by(
        RecruitmentStage.stage_order
    ).all()
    
    #extra added start
    print("Job ID:", company.id)
    print("Stages Found:", len(stages))

    for s in stages:
        print(s.stage_name)
    #end
    
    for index, stage in enumerate(stages):

        progress = ApplicationProgress(
            application_id=application.id,
            stage_id=stage.id,
            job_id=company.id,
            status="Current" if index == 0 else "Pending",
            remarks=""
        )

        db.session.add(progress)
        # extra added line (print)
    print("Creating Progress:", progress.application_id, progress.stage_id)

    db.session.commit()

    return redirect("/applications")
# ===================================
# My Applications
# ===================================

@app.route("/applications")
def applications():

    applications = Application.query.filter_by(
        student_name=session.get("student_name")
    ).all()

    return render_template(
        "student/applications.html",
        applications=applications
    )


# ===================================
# All Applications
# ===================================

@app.route("/all_applications")
def all_applications():

    applications = Application.query.all()

    return render_template(
        "admin/all_applications.html",
        applications=applications
    )


# ===================================
# Update Status
# ===================================

@app.route("/update_status/<int:id>/<status>")
def update_status(id, status):

    application = Application.query.get(id)

    if application:
        application.status = status
        db.session.commit()

    return redirect("/all_applications")


# ===================================
# Reports
# ===================================

@app.route("/reports")
def reports():

    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_applications = Application.query.count()
    
    selected_count = Application.query.filter_by(status="Selected").count()

    pending_count = Application.query.filter_by(status="Pending").count()

    rejected_count = Application.query.filter_by(status="Rejected").count()

    return render_template(
        "admin/reports.html",
        total_students=total_students,
        total_companies=total_companies,
        total_applications=total_applications,
        
        selected_count=selected_count,
        pending_count=pending_count,
        rejected_count=rejected_count
    )

# ===================================
# Manage Recruiters
# ===================================

@app.route("/admin_recruiters")
def admin_recruiters():

    recruiters = Recruiter.query.all()

    return render_template(
        "admin_recruiters.html",
        recruiters=recruiters
    )
 
# ===================================
# Approve Recruiter  
# ===================================
@app.route("/approve_recruiter/<int:id>")
def approve_recruiter(id):

    recruiter = Recruiter.query.get(id)

    recruiter.status = "Approved"

    db.session.commit()

    return redirect("/admin_recruiters")

# ===================================
# Reject Recruiter  
# ===================================
@app.route("/reject_recruiter/<int:id>")
def reject_recruiter(id):

    recruiter = Recruiter.query.get(id)

    recruiter.status = "Rejected"

    db.session.commit()

    return redirect("/admin_recruiters")

# ===================================
# Recruitment Process
# ===================================
@app.route("/recruitment_process")
def recruitment_process():

    if "recruiter_id" not in session:
        return redirect("/recruiter_login")

    jobs = Company.query.filter_by(
        company_name=session["company_name"]
    ).all()

    return render_template(
        "recruiter/recruitment_process.html",
        jobs=jobs
    )
    
# ===================================
# Manage Stages
# ===================================
@app.route("/manage_stages/<int:job_id>", methods=["GET", "POST"])
def manage_stages(job_id):

    if "recruiter_id" not in session:
        return redirect("/recruiter_login")

    job = Company.query.get_or_404(job_id)

    if request.method == "POST":

        stage_name = request.form["stage_name"]

        # Get the last stage for this job
        last_stage = RecruitmentStage.query.filter_by(
            job_id=job_id
        ).order_by(
            RecruitmentStage.stage_order.desc()
        ).first()

        if last_stage:
            next_order = last_stage.stage_order + 1
        else:
            next_order = 1

        new_stage = RecruitmentStage(
            job_id=job_id,
            stage_name=stage_name,
            stage_order=next_order
        )

        db.session.add(new_stage)
        db.session.commit()

        return redirect(f"/manage_stages/{job_id}")

    stages = RecruitmentStage.query.filter_by(
        job_id=job_id
    ).order_by(
        RecruitmentStage.stage_order
    ).all()

    return render_template(
        "recruiter/manage_stages.html",
        job=job,
        stages=stages
    )
# ===================================
# Add Stage
# ===================================
@app.route("/add_stage/<int:job_id>", methods=["GET", "POST"])
def add_stage(job_id):

    if "recruiter_id" not in session:
        return redirect("/recruiter_login")

    job = Company.query.get_or_404(job_id)

    if request.method == "POST":

        stage = RecruitmentStage(

            job_id=job_id,

            stage_name=request.form["stage_name"],

            stage_order=request.form["stage_order"]

        )

        db.session.add(stage)
        db.session.commit()

        return redirect(f"/manage_stages/{job_id}")

    return render_template(
        "recruiter/stage_form.html",
        job=job
    )

# ===================================
# Edit Stage
# ===================================
@app.route("/edit_stage/<int:stage_id>", methods=["GET", "POST"])
def edit_stage(stage_id):

    if "recruiter_id" not in session:
        return redirect("/recruiter_login")

    stage = RecruitmentStage.query.get_or_404(stage_id)

    if request.method == "POST":

        stage.stage_name = request.form["stage_name"]

        db.session.commit()

        return redirect(f"/manage_stages/{stage.job_id}")

    return render_template(
        "recruiter/edit_stage.html",
        stage=stage
    )
    
# ===================================
# Delete Stage
# ===================================
@app.route("/delete_stage/<int:stage_id>")
def delete_stage(stage_id):

    if "recruiter_id" not in session:
        return redirect("/recruiter_login")

    stage = RecruitmentStage.query.get_or_404(stage_id)
    job_id = stage.job_id

    db.session.delete(stage)
    db.session.commit()

    # Reorder remaining stages
    stages = RecruitmentStage.query.filter_by(job_id=job_id)\
                                   .order_by(RecruitmentStage.stage_order).all()

    for index, stage in enumerate(stages, start=1):
        stage.stage_order = index

    db.session.commit()

    return redirect(f"/manage_stages/{job_id}")


# ===================================
# View Recruitment Progress
# ===================================

@app.route("/view_progress/<int:application_id>")
def view_progress(application_id):

    if "recruiter_id" not in session:
        return redirect("/recruiter_login")

    application = Application.query.get_or_404(application_id)

    student = Student.query.filter_by(
        name=application.student_name
        ).first()

    progress = ApplicationProgress.query.filter_by(
        application_id=application.id
    ).order_by(
        ApplicationProgress.id
    ).all()

    progress_data = []

    for item in progress:

        stage = RecruitmentStage.query.get(item.stage_id)

        progress_data.append({
            "id": item.id,
            "stage_name": stage.stage_name,
            "status": item.status,
            "remarks": item.remarks
        })

    # Calculate progress
    total_stages = len(progress)

    completed_stages = len([
        p for p in progress
        if p.status == "Completed"
    ])

    if total_stages > 0:
        progress_percentage = int((completed_stages / total_stages) * 100)
    else:
        progress_percentage = 0

    return render_template(
    "recruiter/view_progress.html",
    application=application,
    student=student,
    progress_data=progress_data,
    progress_percentage=progress_percentage
)

# ===================================
# Complete Stage
# ===================================
@app.route("/complete_stage/<int:progress_id>", methods=["POST"])
def complete_stage(progress_id):

    if "recruiter_id" not in session:
        return redirect("/recruiter_login")

    current = ApplicationProgress.query.get_or_404(progress_id)

    remarks = request.form.get("remarks")
    current.remarks = remarks

    current.status = "Completed"

    db.session.commit()

    next_stage = ApplicationProgress.query.filter(
        ApplicationProgress.application_id == current.application_id,
        ApplicationProgress.id > current.id
    ).order_by(
        ApplicationProgress.id
    ).first()

    if next_stage:
        next_stage.status = "Current"
    else:
        application = Application.query.get(current.application_id)
        application.status = "Selected"

    db.session.commit()

    return redirect(f"/view_progress/{current.application_id}")

# ===================================
# Student Application Status
# ===================================

@app.route("/application_status/<int:application_id>")
def application_status(application_id):

    if "student_name" not in session:
        return redirect("/student_login")

    # Get only the selected application of the logged-in student
    application = Application.query.filter_by(
        id=application_id,
        student_name=session["student_name"]
    ).first()

    if not application:
        flash("Application not found.", "danger")
        return redirect(url_for("applications"))

    # Get all recruitment stages for this application
    progress = ApplicationProgress.query.filter_by(
        application_id=application.id
    ).order_by(ApplicationProgress.id).all()

    stage_list = []
    completed = 0
    total = len(progress)

    for item in progress:

        stage = RecruitmentStage.query.get(item.stage_id)

        if stage:

            stage_list.append({
                "stage_name": stage.stage_name,
                "status": item.status,
                "remarks": item.remarks
            })

            if item.status == "Completed":
                completed += 1

    # Calculate Progress Percentage
    if total > 0:
        progress_percentage = int((completed / total) * 100)
    else:
        progress_percentage = 0

    return render_template(
        "student/application_status.html",
        application=application,
        stages=stage_list,
        progress_percentage=progress_percentage
    )
# ===================================
# Reject Candidate
# ===================================

@app.route("/reject_candidate/<int:application_id>", methods=["GET", "POST"])
def reject_candidate(application_id):

    if "recruiter_id" not in session:
        return redirect("/recruiter_login")

    application = Application.query.get_or_404(application_id)

    if request.method == "POST":

        application.status = "Rejected"

        application.rejection_reason = request.form.get("reason")

        db.session.commit()

        return redirect("/recruiter_applications")

    return render_template(
        "recruiter/reject_candidate.html",
        application=application
    )


# ===================================
# Reject Current Stage
# ===================================

@app.route("/reject_stage/<int:progress_id>", methods=["POST"])
def reject_stage(progress_id):

    if "recruiter_id" not in session:
        return redirect("/recruiter_login")

    current = ApplicationProgress.query.get_or_404(progress_id)

    remarks = request.form.get("remarks")

    # Reject current stage
    current.status = "Rejected"
    current.remarks = remarks

    # Reject whole application
    application = Application.query.get(current.application_id)

    application.status = "Rejected"
    application.rejection_reason = remarks

    db.session.commit()

    return redirect(f"/view_progress/{application.id}")

# ===================================
# selected_students_report
# ===================================
@app.route("/selected_students_report")
def selected_students_report():

    selected_applications = Application.query.filter_by(
        status="Selected"
    ).all()

    selected_students = []

    for application in selected_applications:

        student = Student.query.filter_by(
            name=application.student_name
        ).first()

        if student:

            selected_students.append({

                "rollno": student.rollno,
                "name": student.name,
                "department": student.department,
                "company_name": application.company_name,
                "role": application.role,
                "email": student.email,
                "phone": student.phone

            })

    return render_template(
        "admin/selected_students_report.html",
        students=selected_students
    )
    
    
# ===================================
# Export Students 
# ===================================
@app.route("/export_students")
def export_students():

    students = Student.query.all()

    data = []

    for student in students:
        data.append({
            "Id": student.id,
            "Roll No": student.rollno,
            "Name": student.name,
            "Department": student.department,
            "CGPA": student.cgpa,
            "Year of Passing": student.year_of_passing,
            "Email": student.email,
            "Phone": student.phone,
            "DOB": student.dob,
            "Gender": student.gender,
            "Skills": student.skills
        })

    df = pd.DataFrame(data)

    filename = "students.xlsx"

    df.to_excel(filename, index=False)

    return send_file(
        filename,
        as_attachment=True
    )
    
# ===================================
# Logout
# ===================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")
    
# ===================================
# Main
# ===================================

if __name__ == "__main__":

    with app.app_context():
        db.create_all()
        print("Database Created Successfully")

    app.run(debug=True)

