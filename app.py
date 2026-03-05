from flask import Flask, request, session, redirect, url_for, render_template
from models import db, User, Student, Company, Drive

app = Flask(__name__)
app.secret_key = "placement_portal_secret"

# SQLite configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement_portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)

@app.route("/")
def home():
    return "Placement Portal Backend Running"

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register():

    username = request.form.get("username")
    password = request.form.get("password")
    role = request.form.get("role")

    # Check if username already exists
    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return "Username already exists"

    # Create user
    new_user = User(username=username, password=password, role=role)
    db.session.add(new_user)
    db.session.commit()

    # Create role-specific record
    if role == "student":

        name = request.form.get("name")
        department = request.form.get("department")

        student = Student(
            name=name,
            department=department,
            user_id=new_user.id
        )

        db.session.add(student)

    elif role == "company":

        name = request.form.get("name")
        description = request.form.get("description")

        company = Company(
            name=name,
            description=description,
            user_id=new_user.id
        )

        db.session.add(company)

    db.session.commit()

    return "Registration successful"

@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=username).first()

    if not user:
        return "User does not exist"

    if user.password != password:
        return "Incorrect password"

    # Start session
    session["user_id"] = user.id
    session["role"] = user.role

    # Role based redirection
    if user.role == "admin":
        return redirect("/admin_dashboard")

    elif user.role == "company":
        return redirect("/company_dashboard")

    elif user.role == "student":
        return redirect("/student_dashboard")
    
@app.route("/admin_dashboard")
def admin_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied"

    return render_template("admin_dashboard.html")

@app.route("/company_dashboard")
def company_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "company":
        return "Access Denied"

    return render_template("company_dashboard.html")

@app.route("/student_dashboard")
def student_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "student":
        return "Access Denied"

    return "Welcome Student"

@app.route("/admin/companies")
def view_companies():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied"

    companies = Company.query.all()

    return render_template("admin_companies.html", companies=companies)

@app.route("/admin/approve_company/<int:company_id>")
def approve_company(company_id):

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied"

    company = Company.query.get(company_id)

    company.status = "approved"

    db.session.commit()

    return redirect("/admin/companies")

@app.route("/admin/blacklist_company/<int:company_id>")
def blacklist_company(company_id):

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied"

    company = Company.query.get(company_id)

    company.status = "blacklisted"

    db.session.commit()

    return redirect("/admin/companies")

@app.route("/company/create_drive", methods=["GET"])
def create_drive_page():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "company":
        return "Access Denied"

    return render_template("create_drive.html")

@app.route("/company/create_drive", methods=["POST"])
def create_drive():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "company":
        return "Access Denied"

    job_title = request.form.get("job_title")
    job_description = request.form.get("job_description")
    application_deadline = request.form.get("application_deadline")

    # Find the company linked to this logged-in user
    company = Company.query.filter_by(user_id=session["user_id"]).first()

    new_drive = Drive(
        job_title=job_title,
        job_description=job_description,
        application_deadline=application_deadline,
        company_id=company.id
    )

    db.session.add(new_drive)
    db.session.commit()

    return "Drive created successfully"

@app.route("/company/drives")
def company_drives():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "company":
        return "Access Denied"

    company = Company.query.filter_by(user_id=session["user_id"]).first()

    drives = Drive.query.filter_by(company_id=company.id).all()

    return render_template("company_drives.html", drives=drives)

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # Create default admin if not exists
        admin = User.query.filter_by(username="admin").first()

        if not admin:
            admin_user = User(
                username="admin",
                password="admin123",
                role="admin"
            )
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True)