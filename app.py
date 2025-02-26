from flask import Flask, request, jsonify, render_template, make_response, redirect, url_for, session
from jose import jwt
import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from models import init_db, get_or_create_user, User, db
import qrcode
import base64
from io import BytesIO
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from requests_oauthlib import OAuth2Session
import json
import secrets
import requests

load_dotenv()
app = Flask(__name__)

#debug 
print("Client Secret:", os.getenv("LINKEDIN_CLIENT_SECRET"))

# Generate a secure secret key for the session
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(16))

# Ensure data directory exists
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(data_dir, exist_ok=True)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(data_dir, "users.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)

# Configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')

# LinkedIn OAuth Settings
LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID', '')
LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET', '')
LINKEDIN_REDIRECT_URI = os.getenv('LINKEDIN_REDIRECT_URI', 'http://localhost:8080/callback')
LINKEDIN_SCOPE = ['openid', 'profile', 'email']
LINKEDIN_AUTHORIZATION_URL = 'https://www.linkedin.com/oauth/v2/authorization'
LINKEDIN_TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
LINKEDIN_USER_INFO_URL = 'https://api.linkedin.com/v2/userinfo'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_linkedin_oauth():
    return OAuth2Session(
        LINKEDIN_CLIENT_ID,
        redirect_uri=LINKEDIN_REDIRECT_URI,
        scope=LINKEDIN_SCOPE
    )

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    linkedin = get_linkedin_oauth()
    authorization_url, state = linkedin.authorization_url(LINKEDIN_AUTHORIZATION_URL)
    
    # Store the state for later validation
    session['oauth_state'] = state
    
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    try:
        # Extract the authorization code from the callback URL
        code = request.args.get('code')
        if not code:
            return "Authorization code not received", 400

        # Use the authorization code to get the access token
        token_payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': LINKEDIN_REDIRECT_URI,
            'client_id': LINKEDIN_CLIENT_ID,
            'client_secret': LINKEDIN_CLIENT_SECRET
        }

        token_response = requests.post(LINKEDIN_TOKEN_URL, data=token_payload)
        
        if token_response.status_code != 200:
            print(f"Token error: {token_response.status_code}, {token_response.text}")
            return "Failed to obtain access token", 500
            
        token = token_response.json()
        
        # Get user info using the access token
        headers = {'Authorization': f"Bearer {token['access_token']}"}
        user_info_response = requests.get(LINKEDIN_USER_INFO_URL, headers=headers)
        
        if user_info_response.status_code != 200:
            print(f"User info error: {user_info_response.status_code}, {user_info_response.text}")
            return "Failed to obtain user information", 500
            
        user_info = user_info_response.json()
        
        # Extract user data
        email = user_info.get('email')
        linkedin_id = user_info.get('sub')
        first_name = user_info.get('given_name')
        last_name = user_info.get('family_name')
        picture = user_info.get('picture')
        
        if not email:
            return "Email information not available", 400
        
        # Create or update user in database
        user = get_or_create_user(
            email=email,
            linkedin_id=linkedin_id,
            first_name=first_name,
            last_name=last_name,
            profile_picture=picture
        )
        
        # Log in the user with Flask-Login
        login_user(user)
        
        return redirect(url_for('home'))
    
    except Exception as e:
        print(f"Callback error: {str(e)}")
        return f"Error during authentication: {str(e)}", 500

@app.route('/logout')
def logout():
    logout_user()
    # Clear session
    session.clear()
    return redirect(url_for('home'))

@app.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('home.html', email=current_user.email, user=current_user)
    
    return render_template('home.html')

@app.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    return jsonify(current_user.to_dict())

@app.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    try:
        data = request.get_json()
        updateable_fields = ['full_name', 'phone', 'title', 'company', 'website', 'address', 'notes']
        
        for field in updateable_fields:
            if field in data:
                setattr(current_user, field, data[field])
        
        db.session.commit()
        return jsonify(current_user.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/edit-card')
@login_required
def edit_card():
    return render_template('edit_card.html', email=current_user.email, user=current_user)

@app.route('/api/preview-card')
@login_required
def preview_card_data():
    try:
        return jsonify({
            "email": current_user.email,
            "user": current_user.to_dict()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/preview-card')
@login_required
def preview_card():
    return render_template('preview_card.html', email=current_user.email, user=current_user)

@app.route('/download-vcf')
@login_required
def download_vcf():
    try:
        user = current_user
        if not user:
            return "User not found", 404
            
        # Generate VCF content
        vcf_content = f"""BEGIN:VCARD
VERSION:3.0
FN:{user.full_name or f"{user.first_name} {user.last_name}".strip()}
N:{user.last_name or ""};{user.first_name or ""};;;
TITLE:{user.title or ""}
ORG:{user.company or ""}
TEL;TYPE=WORK,VOICE:{user.phone or ""}
URL:{user.website or ""}
ADR;TYPE=WORK:;;{user.address or ""};;;;
NOTE:{user.notes or ""}
EMAIL:{user.email}
END:VCARD"""
        
        # Create response with VCF content
        response = make_response(vcf_content)
        response.headers['Content-Type'] = 'text/vcard'
        response.headers['Content-Disposition'] = f'attachment; filename="{(user.full_name or f"{user.first_name} {user.last_name}").replace(" ", "_")}.vcf"'
        return response
        
    except Exception as e:
        return str(e), 400

@app.route('/qr-code')
@login_required
def qr_code():
    try:
        user = current_user
        if not user:
            return render_template('qr_code.html', error="User not found")
        
        # Generate VCF content
        vcf_content = f"""BEGIN:VCARD
VERSION:3.0
FN:{user.full_name or f"{user.first_name} {user.last_name}".strip()}
N:{user.last_name or ""};{user.first_name or ""};;;
TITLE:{user.title or ""}
ORG:{user.company or ""}
TEL;TYPE=WORK,VOICE:{user.phone or ""}
URL:{user.website or ""}
ADR;TYPE=WORK:;;{user.address or ""};;;;
NOTE:{user.notes or ""}
EMAIL:{user.email}
END:VCARD"""
        
        # Generate QR code with VCF content directly
        qr = qrcode.QRCode(
            version=None,  # Will automatically determine size
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(vcf_content)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert image to base64 for embedding in HTML
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_image = base64.b64encode(buffered.getvalue()).decode()
            
        return render_template('qr_code.html', email=user.email, user=user, qr_image=qr_image)
    
    except Exception as e:
        return render_template('qr_code.html', error=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)