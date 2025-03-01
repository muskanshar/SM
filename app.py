from flask import Flask, request, jsonify, session, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_pic = db.Column(db.String(255), nullable=True)
    profession = db.Column(db.String(120), nullable=True)
    aadhaar_verified = db.Column(db.Boolean, default=False)
    bio = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    interests = db.Column(db.String(500), nullable=True)  # Comma-separated values
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    match_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending, accepted, rejected

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=False)
    limited = db.Column(db.Boolean, default=True)  # Chat is limited until request is accepted

# Landing Page (Sign Page)
@app.route("/")
def home():
    return render_template("signup.html")

# Register a new user
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data:
        return jsonify({"error": "Missing request data"}), 400
    
    hashed_password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')
    new_user = User(
        username=data.get('username'), email=data.get('email'), password=hashed_password,
        profile_pic=data.get('profile_pic'), profession=data.get('profession'),
        aadhaar_verified=data.get('aadhaar_verified', False),
        bio=data.get('bio', ''), location=data.get('location', ''),
        interests=",".join(data.get('interests', [])), age=data.get('age', 18),
        gender=data.get('gender', '')
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

# Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user and bcrypt.check_password_hash(user.password, data.get('password')):
        session['user_id'] = user.id
        return jsonify({"message": "Login successful", "user_id": user.id}), 200
    return jsonify({"error": "Invalid credentials"}), 401

# Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logged out successfully"}), 200

# Get Suggested Profiles
@app.route('/suggested_profiles', methods=['GET'])
def suggested_profiles():
    current_user = session.get('user_id')
    if not current_user:
        return jsonify({"error": "Unauthorized"}), 401

    users = User.query.filter(User.id != current_user).all()  # Exclude current user
    profiles = [
        {
            "id": u.id, "username": u.username, "profile_pic": u.profile_pic,
            "profession": u.profession, "location": u.location,
            "age": u.age, "gender": u.gender, "bio": u.bio
        }
        for u in users
    ]
    return jsonify({"profiles": profiles})

# Get Profile Details
@app.route('/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "username": user.username, "email": user.email, "profession": user.profession,
        "profile_pic": user.profile_pic, "aadhaar_verified": user.aadhaar_verified,
        "bio": user.bio, "location": user.location, "interests": user.interests.split(","),
        "age": user.age, "gender": user.gender
    })

# Interested Action
@app.route('/interested/<int:user_id>', methods=['POST'])
def interested(user_id):
    current_user = session.get('user_id')
    if not current_user:
        return jsonify({"error": "Unauthorized"}), 401

    existing_match = Match.query.filter_by(user_id=current_user, match_id=user_id).first()
    if not existing_match:
        new_match = Match(user_id=current_user, match_id=user_id)
        db.session.add(new_match)
        db.session.commit()
    
    return jsonify({"message": "Interest sent!"})

# Accept Interest (Unlock Chat)
@app.route('/accept/<int:user_id>', methods=['POST'])
def accept_interest(user_id):
    current_user = session.get('user_id')
    if not current_user:
        return jsonify({"error": "Unauthorized"}), 401

    match = Match.query.filter_by(user_id=user_id, match_id=current_user).first()
    if match:
        match.status = "accepted"
        db.session.commit()
        return jsonify({"message": "Interest accepted. Chat unlocked!"})
    return jsonify({"error": "No pending request found"}), 404

# Not Interested Action
@app.route('/not_interested/<int:user_id>', methods=['POST'])
def not_interested(user_id):
    current_user = session.get('user_id')
    if not current_user:
        return jsonify({"error": "Unauthorized"}), 401

    Match.query.filter_by(user_id=current_user, match_id=user_id).delete()
    db.session.commit()
    return jsonify({"message": "Profile removed from suggestions!"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
