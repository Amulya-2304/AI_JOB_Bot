from app.models.saved_job import SavedJob
from flask import Flask, render_template, request, flash, session, redirect, url_for
from dotenv import load_dotenv
import os
from app.db import db
from app.models.user import User
from werkzeug.utils import secure_filename
import fitz
import docx
from app.utils.cv_parser import extract_cv_data
from app.utils.job_scraper import fetch_google_jobs


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.secret_key = 'cv-upload-secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///test.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix='/api/users')

    UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    @app.route('/')
    def index():
        return {'message': 'Flask AI Job Application Bot is running!'}

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']

            existing_user_by_email = User.query.filter_by(email=email).first()
            existing_user_by_username = User.query.filter_by(username=username).first()

            if existing_user_by_email or existing_user_by_username:
                return "⚠️ Already registered Username or Email ID", 400

            user = User(username=username, email=email)
            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id
            return redirect(url_for('profile'))

        return render_template('login.html')

    @app.route('/profile', methods=['GET', 'POST'])
    def profile():
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))

        user = User.query.get(user_id)

        if request.method == 'POST':
            file = request.files['cv_file']
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                user.cv_filename = filename
                db.session.commit()

        cv_text = ""
        parsed_data = {}

        if user.cv_filename:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], user.cv_filename)
            if os.path.exists(filepath):
                if user.cv_filename.lower().endswith('.pdf'):
                    with fitz.open(filepath) as pdf:
                        for page in pdf:
                            cv_text += page.get_text()
                elif user.cv_filename.lower().endswith('.docx'):
                    doc = docx.Document(filepath)
                    for para in doc.paragraphs:
                        cv_text += para.text + "\n"
                parsed_data = extract_cv_data(cv_text)

        return render_template('profile.html', user=user,
                               cv_text=cv_text,
                               skills=parsed_data.get('skills', []),
                               entities=parsed_data.get('entities', []))

    @app.route('/skip_cv', methods=['POST'])
    def skip_cv():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return redirect(url_for('home'))

    @app.route('/home', methods=['GET'])
    def home():
        return render_template('home.html')

    @app.route('/search_jobs', methods=['GET'])
    def search_jobs():
        """Fetch jobs using SerpAPI based on search filters"""
        keyword = request.args.get('keyword', '')
        location = request.args.get('location', '')
        status = request.args.get('status')

        try:
            jobs = fetch_google_jobs(keyword, location)
        except Exception as e:
            return f"Error fetching jobs: {e}", 500

        return render_template('job_results.html', keyword=keyword, jobs=jobs, status=status)

    @app.route('/save_job', methods=['POST'])
    def save_job():
        """Save a job to the current user's saved list"""
        if 'user_id' not in session:
            return redirect(url_for('login'))

        user_id = session['user_id']
        title = request.form.get('title')
        company = request.form.get('company')
        location = request.form.get('location')
        link = request.form.get('link')
        description = request.form.get('description', '')

        new_job = SavedJob(
            user_id=user_id,
            title=title,
            company=company,
            location=location,
            link=link,
            description=description
        )
        db.session.add(new_job)
        db.session.commit()

        flash('Job saved successfully!')
        return redirect(url_for('home'))


    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)