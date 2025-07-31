from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from models import db, User, Feedback, Rating

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def init_routes(app):
    
    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('dashboard'))
            else:
                flash('Invalid credentials')
        
        return render_template('login.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            roll_number = request.form['roll_number']
            password = request.form['password']
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists')
                return render_template('register.html')
            
            if User.query.filter_by(roll_number=roll_number).first():
                flash('Roll number already registered')
                return render_template('register.html')
            
            user = User(username=username, email=email, roll_number=roll_number)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful')
            return redirect(url_for('login'))
        
        return render_template('register.html')
    
    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user_feedbacks = Feedback.query.filter_by(user_id=session['user_id']).order_by(Feedback.created_at.desc()).limit(5).all()
        return render_template('dashboard.html', feedbacks=user_feedbacks)
    
    @app.route('/submit_feedback', methods=['GET', 'POST'])
    def submit_feedback():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            category = request.form['category']
            comments = request.form['comments']
            rating = request.form.get('rating')
            is_anonymous = 'anonymous' in request.form
            
            feedback = Feedback(
                user_id=None if is_anonymous else session['user_id'],
                category=category,
                comments=comments,
                rating=int(rating) if rating else None,
                is_anonymous=is_anonymous
            )
            
            if category == 'Food':
                days = request.form.getlist('days')
                quality = request.form.get('quality')
                feedback.days = ','.join(days)
                feedback.quality = quality
            
            # Handle image upload
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = timestamp + filename
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    feedback.image_path = filename
            
            db.session.add(feedback)
            db.session.commit()
            
            flash('Feedback submitted successfully!')
            return redirect(url_for('dashboard'))
        
        return render_template('submit_feedback.html')
    
    @app.route('/track_feedback')
    def track_feedback():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        # Show both named and anonymous feedbacks for this user
        feedbacks = Feedback.query.filter(
            (Feedback.user_id == session['user_id']) |
            (Feedback.is_anonymous == True)
        ).order_by(Feedback.created_at.desc()).all()
        
        # Filter to show only user's own anonymous feedbacks (those submitted while logged in)
        user_feedbacks = Feedback.query.filter_by(user_id=session['user_id']).order_by(Feedback.created_at.desc()).all()
        
        return render_template('track_feedback.html', feedbacks=user_feedbacks)
    
    @app.route('/admin_dashboard')
    def admin_dashboard():
        if 'user_id' not in session or session.get('role') != 'admin':
            return redirect(url_for('login'))
        
        category_filter = request.args.get('category', '')
        status_filter = request.args.get('status', '')
        
        query = Feedback.query
        
        if category_filter:
            query = query.filter_by(category=category_filter)
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        feedbacks = query.order_by(Feedback.created_at.desc()).all()
        
        return render_template('admin_dashboard.html', feedbacks=feedbacks, 
                             category_filter=category_filter, status_filter=status_filter)
    
    @app.route('/update_status/<int:feedback_id>', methods=['GET', 'POST'])
    def update_status(feedback_id):
        if 'user_id' not in session or session.get('role') != 'admin':
            return redirect(url_for('login'))
        
        feedback = Feedback.query.get(feedback_id)
        if not feedback:
            flash('Feedback not found')
            return redirect(url_for('admin_dashboard'))
        
        if request.method == 'POST':
            status = request.form.get('status')
            admin_response = request.form.get('admin_response', '')
            
            if status in ['pending', 'resolved', 'rejected']:
                feedback.status = status
                if admin_response:
                    feedback.admin_response = admin_response
                
                if status in ['resolved', 'rejected']:
                    feedback.resolved_by = session['user_id']
                    feedback.resolved_at = datetime.utcnow()
                
                db.session.commit()
                flash(f'Feedback status updated to {status}')
            
            return redirect(url_for('admin_dashboard'))
        
        # GET request - show the form
        return render_template('update_status.html', feedback=feedback)
    
    @app.route('/analytics')
    def analytics():
        if 'user_id' not in session or session.get('role') != 'admin':
            return redirect(url_for('login'))
        
        return render_template('analytics.html')
    
    @app.route('/api/analytics_data')
    def analytics_data():
        if 'user_id' not in session or session.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Category distribution
        categories = db.session.query(
            Feedback.category, 
            db.func.count(Feedback.id)
        ).group_by(Feedback.category).all()
        
        category_data = {
            'labels': [cat[0] for cat in categories],
            'data': [cat[1] for cat in categories]
        }
        
        # Status distribution
        statuses = db.session.query(
            Feedback.status, 
            db.func.count(Feedback.id)
        ).group_by(Feedback.status).all()
        
        status_data = {
            'labels': [stat[0].title() for stat in statuses],
            'data': [stat[1] for stat in statuses]
        }
        
        # Food complaints by day
        food_feedbacks = Feedback.query.filter_by(category='Food').all()
        day_counts = {'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 'Thursday': 0, 
                     'Friday': 0, 'Saturday': 0, 'Sunday': 0}
        
        for feedback in food_feedbacks:
            if feedback.days:
                for day in feedback.days.split(','):
                    if day in day_counts:
                        day_counts[day] += 1
        
        food_day_data = {
            'labels': list(day_counts.keys()),
            'data': list(day_counts.values())
        }
        
        return jsonify({
            'categories': category_data,
            'statuses': status_data,
            'food_days': food_day_data
        })
    
    @app.route('/rate_facilities', methods=['GET', 'POST'])
    def rate_facilities():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            facility = request.form['facility']
            rating_value = request.form['rating']
            review = request.form.get('review', '')
            is_anonymous = 'anonymous' in request.form
            
            # Check if user already rated this facility (for non-anonymous)
            if not is_anonymous:
                existing_rating = Rating.query.filter_by(
                    user_id=session['user_id'], 
                    facility=facility,
                    is_anonymous=False
                ).first()
                
                if existing_rating:
                    flash(f'You have already rated {facility}. Only one rating per facility allowed.')
                    return render_template('rate_facilities.html')
            
            rating = Rating(
                user_id=None if is_anonymous else session['user_id'],
                facility=facility,
                rating=int(rating_value),
                review=review,
                is_anonymous=is_anonymous
            )
            
            db.session.add(rating)
            db.session.commit()
            
            flash(f'Thank you for rating {facility}!')
            return redirect(url_for('facility_ratings'))
        
        return render_template('rate_facilities.html')
    
    @app.route('/facility_ratings')
    def facility_ratings():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        return render_template('facility_ratings.html')
    
    @app.route('/api/facility_ratings_data')
    def facility_ratings_data():
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get average ratings for each facility
        facilities = ['Canteen', 'Library', 'Sports Ground', 'Computer Lab', 'Hostel Rooms']
        
        facility_data = []
        for facility in facilities:
            ratings = Rating.query.filter_by(facility=facility).all()
            if ratings:
                avg_rating = sum([r.rating for r in ratings]) / len(ratings)
                total_ratings = len(ratings)
            else:
                avg_rating = 0
                total_ratings = 0
            
            facility_data.append({
                'facility': facility,
                'average': round(avg_rating, 1),
                'total': total_ratings
            })
        
        # Get rating distribution (1-5 stars)
        rating_distribution = {}
        for i in range(1, 6):
            count = Rating.query.filter_by(rating=i).count()
            rating_distribution[f'{i} Star'] = count
        
        # Recent reviews
        recent_reviews = Rating.query.filter(
            Rating.review.isnot(None), 
            Rating.review != ''
        ).order_by(Rating.created_at.desc()).limit(10).all()
        
        review_data = []
        for review in recent_reviews:
            review_data.append({
                'facility': review.facility,
                'rating': review.rating,
                'review': review.review[:100] + ('...' if len(review.review) > 100 else ''),
                'student': 'Anonymous' if review.is_anonymous else (review.user.username if review.user else 'Unknown'),
                'date': review.created_at.strftime('%d %b %Y')
            })
        
        return jsonify({
            'facilities': facility_data,
            'distribution': rating_distribution,
            'recent_reviews': review_data
        })
    
    @app.route('/anonymous_feedbacks')
    def anonymous_feedbacks():
        if 'user_id' not in session or session.get('role') != 'admin':
            return redirect(url_for('login'))
        
        anonymous_feedbacks = Feedback.query.filter_by(is_anonymous=True).order_by(Feedback.created_at.desc()).all()
        return render_template('anonymous_feedbacks.html', feedbacks=anonymous_feedbacks)
    
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))