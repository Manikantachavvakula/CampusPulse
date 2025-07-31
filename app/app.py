from flask import Flask
from models import db, User
from routes import init_routes
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hostel_feedback.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
init_routes(app)

def migrate_database():
    """Add new columns to existing database"""
    try:
        with app.app_context():
            # Check if new columns exist, if not add them
            try:
                db.engine.execute('ALTER TABLE feedback ADD COLUMN admin_response TEXT')
            except:
                pass
            try:
                db.engine.execute('ALTER TABLE feedback ADD COLUMN resolved_by INTEGER')
            except:
                pass
            try:
                db.engine.execute('ALTER TABLE feedback ADD COLUMN resolved_at DATETIME')
            except:
                pass
            try:
                db.engine.execute('ALTER TABLE feedback ADD COLUMN is_anonymous BOOLEAN DEFAULT 0')
            except:
                pass
            try:
                db.engine.execute('ALTER TABLE user ADD COLUMN roll_number VARCHAR(20)')
            except:
                pass
            # Create ratings table if it doesn't exist
            try:
                db.engine.execute('''
                    CREATE TABLE IF NOT EXISTS rating (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        facility VARCHAR(50) NOT NULL,
                        rating INTEGER NOT NULL,
                        review TEXT,
                        is_anonymous BOOLEAN DEFAULT 0,
                        created_at DATETIME,
                        FOREIGN KEY (user_id) REFERENCES user (id)
                    )
                ''')
            except:
                pass
            print("Database migration completed successfully!")
    except Exception as e:
        print(f"Migration note: {e}")

@app.before_first_request
def create_tables():
    db.create_all()
    
    # Run migration for new columns
    migrate_database()
    
    # Create admin user if doesn't exist
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@hostel.com', roll_number='ADMIN001', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)