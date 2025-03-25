from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Quiz, QuizAttempt
from .forms import LoginForm, RegisterForm, QuizForm
from sqlalchemy import func
from datetime import datetime

db = None



def calculate_score(form_data, quiz_id):
    """Calculate the user's score based on submitted answers"""
    quiz = Quiz.query.get_or_404(quiz_id)
    correct = 0
    
    # Compare submitted answers with correct answers
    for question in quiz.questions:
        submitted_answer = form_data.get(f'question_{question.id}')
        if submitted_answer == question.correct_answer:
            correct += 1
    
    return correct

def get_question_count(quiz_id):
    """Get the total number of questions for a quiz"""
    return Quiz.query.get_or_404(quiz_id).questions.count()

def calculate_time(start_time):
    """Calculate time taken to complete quiz in minutes"""
    time_taken = (datetime.utcnow() - start_time).total_seconds()
    return round(time_taken / 60, 1)  # Convert to minutes with 1 decimal place

def calculate_earnings(teacher_id):
    """Calculate total earnings and quiz statistics for a teacher"""
    quizzes = Quiz.query.filter_by(author_id=teacher_id).all()
    quiz_stats = []
    total_earnings = 0.0
    
    for quiz in quizzes:
        attempts = QuizAttempt.query.filter_by(quiz_id=quiz.id).count()
        earnings = attempts * quiz.price
        quiz_stats.append({
            'title': quiz.title,
            'purchase_count': attempts,
            'earnings': earnings
        })
        total_earnings += earnings
    
    return total_earnings, quiz_stats

def get_recent_attempts(user_id, limit=5):
    """Get recent quiz attempts for a user"""
    return QuizAttempt.query.filter_by(
        user_id=user_id
    ).order_by(
        QuizAttempt.completed_at.desc()
    ).limit(limit).all()



def init_app(app, database):
    global db
    db = database
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.password == form.password.data:
                login_user(user)
                flash('Logged in successfully!', 'success')
                return redirect(url_for('dashboard'))
            flash('Invalid email or password', 'error')
        return render_template('auth/login.html', form=form)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data, password=form.password.data, role=form.role.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        return render_template('auth/register.html', form=form)

    @app.route('/dashboard')
    @login_required
    def dashboard():
        if current_user.role == 'teacher':
            return render_template('teacher/dashboard.html')
        elif current_user.role == 'student':
            recent_attempts = QuizAttempt.query.filter_by(
                user_id=current_user.id
            ).order_by(QuizAttempt.completed_at.desc()).limit(5).all()
            return render_template('student/dashboard.html', recent_attempts=recent_attempts)
        elif current_user.role == 'admin':
            return render_template('admin/dashboard.html')

    @app.route('/create_quiz', methods=['GET', 'POST'])
    @login_required   
    def create_quiz():
        if current_user.role != 'teacher':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('dashboard'))

        form = QuizForm()
        if form.validate_on_submit():
            quiz = Quiz(title=form.title.data, subject=form.subject.data, price=form.price.data, author_id=current_user.id)
            db.session.add(quiz)
            db.session.commit()
            flash('Quiz created successfully!', 'success')
            return redirect(url_for('dashboard'))
        return render_template('teacher/create_quiz.html', form=form)

    @app.route('/browse_quizzes')
    @login_required
    def browse_quizzes():
        if current_user.role != 'student':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('dashboard'))

        quizzes = Quiz.query.filter_by(is_published=True).all()
        return render_template('student/browse_quizzes.html', quizzes=quizzes)
    

    @app.route('/quiz/<int:quiz_id>')
    def quiz_details(quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        return render_template('quiz_details.html', quiz=quiz)

    
    @app.route('/quiz_result/<int:quiz_id>')
    @login_required
    def quiz_result(quiz_id):
        # Get quiz from database
        quiz = Quiz.query.get_or_404(quiz_id)
    
        # Get the user's quiz attempt (you'll need to implement this model)
        attempt = QuizAttempt.query.filter_by(
            quiz_id=quiz_id,
            user_id=current_user.id
        ).first_or_404()
    
        # Calculate percentage score
        score = round((attempt.correct_answers / attempt.total_questions) * 100, 1) if attempt.total_questions > 0 else 0
    
        return render_template('student/quiz_result.html',
                               quiz=quiz,
                               score=score,  # Rounded to 1 decimal place
                               correct=attempt.correct_answers,
                               total=attempt.total_questions,
                               time_taken=attempt.time_taken_minutes,
                               attempt = attempt
                               )
    
    @app.route('/teacher/manage-quizzes')  # Simple route without blueprint
    @login_required
    def manage_quizzes():
        if current_user.role != 'teacher':
            abort(403)
        quizzes = Quiz.query.filter_by(author_id=current_user.id).all()
        return render_template('teacher/manage_quizzes.html', quizzes=quizzes)

    @app.route('/logout')
    @login_required    
    def logout():
        logout_user()
        flash('Logged out successfully!', 'success')
        return redirect(url_for('home'))
    
    @app.route('/debug-routes')
    def debug_routes():
        return '<br>'.join(sorted(str(rule) for rule in app.url_map.iter_rules()))
    
    @app.route('/teacher/earnings')
    @login_required
    def earnings():
        if current_user.role != 'teacher':
            abort(403)

        # Calculate total earnings and per-quiz stats
        quizzes = Quiz.query.filter_by(author_id=current_user.id).all()
        quiz_stats = []

        for quiz in quizzes:
            attempts = QuizAttempt.query.filter_by(quiz_id=quiz.id).count()
            quiz_stats.append({
                'title': quiz.title,
                'purchase_count': attempts,
                'earnings': attempts * quiz.price
            })

        total_earnings = sum(q['earnings'] for q in quiz_stats)

        return render_template('teacher/earnings.html',
                            total_earnings=total_earnings,
                            quizzes=quiz_stats)


    @app.route('/submit_quiz/<int:quiz_id>', methods=['POST'])
    @login_required
    def submit_quiz(quiz_id):
        # Process submission and create attempt
        attempt = QuizAttempt(
            quiz_id=quiz_id,
            user_id=current_user.id,
            correct_answers=calculate_score(request.form),
            total_questions=get_question_count(quiz_id),
            time_taken=calculate_time()
        )
        db.session.add(attempt)
        db.session.commit()

        return redirect(url_for('quiz_result', quiz_id=quiz_id))
    
    @app.route('/student/results')
    @login_required
    def student_results():
        if current_user.role != 'student':
            abort(403)
        attempts = QuizAttempt.query.filter_by(
            user_id=current_user.id
        ).order_by(QuizAttempt.completed_at.desc()).all()
        return render_template('student/results.html', attempts=attempts)
    
    @app.route('/admin/manage-users')
    @login_required
    def manage_users():
        if current_user.role != 'admin':
            abort(403)
        users = User.query.order_by(User.username).all()
        return render_template('admin/manage_users.html', users=users)