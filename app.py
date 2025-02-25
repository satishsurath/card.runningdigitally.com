from flask import Flask, request, jsonify, render_template, make_response
from jose import jwt
import os
from dotenv import load_dotenv
from models import init_db, get_or_create_user, User, db

load_dotenv()

app = Flask(__name__)

# Ensure data directory exists
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(data_dir, exist_ok=True)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(data_dir, "users.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)

# Configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
EXPECTED_AUD = os.getenv('CF_ACCESS_AUD', 'default-development-aud')

print(f"Starting app with FLASK_ENV={FLASK_ENV}")
print(f"Expected AUD configured as: {EXPECTED_AUD}")

# Development mode mock token
DEV_MODE_TOKEN = jwt.encode(
    {
        'email': 'dev@example.com',
        'aud': EXPECTED_AUD
    },
    'dev-secret',
    algorithm='HS256'
)

@app.route('/')
def home():
    # In development mode, use the mock token if no token is provided
    token = request.headers.get('Cf-Access-Jwt-Assertion')
    print(f"Received token from headers: {token}")
    
    if FLASK_ENV == 'development' and not token:
        token = DEV_MODE_TOKEN
        print(f"Using development mode token: {token}")
    
    if not token:
        return render_template('home.html')
    
    try:
        # Decode the JWT token without any verification
        decoded = jwt.decode(
            token,
            'dummy-key',
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_exp": False,
                "verify_iat": False,
                "verify_nbf": False,
                "verify_iss": False,
                "verify_sub": False,
                "verify_jti": False,
                "verify_at_hash": False,
            }
        )
        
        print(f"Decoded token contents: {decoded}")
        
        # Manual audience validation
        token_aud = decoded.get('aud')
        print(f"Token AUD: {token_aud}")
        print(f"Expected AUD: {EXPECTED_AUD}")
        
        # Handle both string and array audiences
        if isinstance(token_aud, list):
            valid_aud = EXPECTED_AUD in token_aud
        else:
            valid_aud = token_aud == EXPECTED_AUD

        if not token_aud or not valid_aud:
            return render_template('home.html', error="Invalid audience claim")
        
        # Extract email from the token and store in database
        email = decoded.get('email', 'No email found')
        get_or_create_user(email)
        
        return render_template('home.html', email=email)
    
    except Exception as e:
        print(f"Error decoding token: {str(e)}")
        return render_template('home.html', error=str(e))

@app.route('/api/profile', methods=['GET'])
def get_profile():
    token = request.headers.get('Cf-Access-Jwt-Assertion')
    if FLASK_ENV == 'development' and not token:
        token = DEV_MODE_TOKEN
    
    try:
        decoded = jwt.decode(
            token,
            'dummy-key',
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_exp": False,
                "verify_iat": False,
                "verify_nbf": False,
                "verify_iss": False,
                "verify_sub": False,
                "verify_jti": False,
                "verify_at_hash": False,
            }
        )
                
        # Validate audience
        token_aud = decoded.get('aud')
        if isinstance(token_aud, list):
            valid_aud = EXPECTED_AUD in token_aud
        else:
            valid_aud = token_aud == EXPECTED_AUD

        if not token_aud or not valid_aud:
            return jsonify({"error": "Invalid audience"}), 403
            
        email = decoded.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify(user.to_dict())
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/profile', methods=['PUT'])
def update_profile():
    token = request.headers.get('Cf-Access-Jwt-Assertion')
    if FLASK_ENV == 'development' and not token:
        token = DEV_MODE_TOKEN
    
    try:
        decoded = jwt.decode(
            token,
            'dummy-key',
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_exp": False,
                "verify_iat": False,
                "verify_nbf": False,
                "verify_iss": False,
                "verify_sub": False,
                "verify_jti": False,
                "verify_at_hash": False,
            }
        )
                
        # Validate audience
        token_aud = decoded.get('aud')
        if isinstance(token_aud, list):
            valid_aud = EXPECTED_AUD in token_aud
        else:
            valid_aud = token_aud == EXPECTED_AUD

        if not token_aud or not valid_aud:
            return jsonify({"error": "Invalid audience"}), 403
            
        email = decoded.get('email')
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        data = request.get_json()
        updateable_fields = ['full_name', 'phone', 'title', 'company', 'website', 'address', 'notes']
        
        for field in updateable_fields:
            if field in data:
                setattr(user, field, data[field])
        
        db.session.commit()
        return jsonify(user.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/edit-card')
def edit_card():
    token = request.headers.get('Cf-Access-Jwt-Assertion')
    if FLASK_ENV == 'development' and not token:
        token = DEV_MODE_TOKEN
    
    if not token:
        return render_template('edit_card.html')
    
    try:
        decoded = jwt.decode(
            token,
            'dummy-key',
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_exp": False,
                "verify_iat": False,
                "verify_nbf": False,
                "verify_iss": False,
                "verify_sub": False,
                "verify_jti": False,
                "verify_at_hash": False,
            }
        )
        
        token_aud = decoded.get('aud')
        if isinstance(token_aud, list):
            valid_aud = EXPECTED_AUD in token_aud
        else:
            valid_aud = token_aud == EXPECTED_AUD

        if not token_aud or not valid_aud:
            return render_template('edit_card.html', error="Invalid audience claim")
        
        email = decoded.get('email', 'No email found')
        get_or_create_user(email)
        
        return render_template('edit_card.html', email=email)
    
    except Exception as e:
        return render_template('edit_card.html', error=str(e))

@app.route('/api/preview-card')
def preview_card_data():
    token = request.headers.get('Cf-Access-Jwt-Assertion')
    if FLASK_ENV == 'development' and not token:
        token = DEV_MODE_TOKEN
    
    try:
        decoded = jwt.decode(
            token,
            'dummy-key',
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_exp": False,
                "verify_iat": False,
                "verify_nbf": False,
                "verify_iss": False,
                "verify_sub": False,
                "verify_jti": False,
                "verify_at_hash": False,
            }
        )
        
        token_aud = decoded.get('aud')
        if isinstance(token_aud, list):
            valid_aud = EXPECTED_AUD in token_aud
        else:
            valid_aud = token_aud == EXPECTED_AUD

        if not token_aud or not valid_aud:
            return jsonify({"error": "Invalid audience claim"}), 403

        email = decoded.get('email', 'No email found')
        user = get_or_create_user(email)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify({
            "email": email,
            "user": user.to_dict()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/preview-card')
def preview_card():
    token = request.headers.get('Cf-Access-Jwt-Assertion')
    if FLASK_ENV == 'development' and not token:
        token = DEV_MODE_TOKEN
    
    if not token:
        return render_template('preview_card.html')
    
    try:
        decoded = jwt.decode(
            token,
            'dummy-key',
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_exp": False,
                "verify_iat": False,
                "verify_nbf": False,
                "verify_iss": False,
                "verify_sub": False,
                "verify_jti": False,
                "verify_at_hash": False,
            }
        )
        
        token_aud = decoded.get('aud')
        if isinstance(token_aud, list):
            valid_aud = EXPECTED_AUD in token_aud
        else:
            valid_aud = token_aud == EXPECTED_AUD

        if not token_aud or not valid_aud:
            return render_template('preview_card.html', error="Invalid audience claim")

        email = decoded.get('email', 'No email found')
        user = get_or_create_user(email)  # Make sure we have a user record
        
        if not user:
            return render_template('preview_card.html', error="User not found")
            
        return render_template('preview_card.html', email=email, user=user)
    
    except Exception as e:
        return render_template('preview_card.html', error=str(e))

@app.route('/download-vcf')
def download_vcf():
    token = request.headers.get('Cf-Access-Jwt-Assertion')
    if FLASK_ENV == 'development' and not token:
        token = DEV_MODE_TOKEN
    
    try:
        decoded = jwt.decode(
            token,
            'dummy-key',
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_exp": False,
                "verify_iat": False,
                "verify_nbf": False,
                "verify_iss": False,
                "verify_sub": False,
                "verify_jti": False,
                "verify_at_hash": False,
            }
        )
        
        token_aud = decoded.get('aud')
        if isinstance(token_aud, list):
            valid_aud = EXPECTED_AUD in token_aud
        else:
            valid_aud = token_aud == EXPECTED_AUD

        if not token_aud or not valid_aud:
            return "Unauthorized", 403

        email = decoded.get('email', 'No email found')
        user = get_or_create_user(email)
        
        if not user:
            return "User not found", 404

        # Generate VCF content
        vcf_content = f"""BEGIN:VCARD
VERSION:3.0
FN:{user.full_name}
N:{user.full_name};;;;
TITLE:{user.title}
ORG:{user.company}
TEL;TYPE=WORK,VOICE:{user.phone}
URL:{user.website}
ADR;TYPE=WORK:;;{user.address};;;;
NOTE:{user.notes}
EMAIL:{user.email}
END:VCARD"""
        
        # Create response with VCF content
        response = make_response(vcf_content)
        response.headers['Content-Type'] = 'text/vcard'
        response.headers['Content-Disposition'] = f'attachment; filename="{user.full_name.replace(" ", "_")}.vcf"'
        return response
        
    except Exception as e:
        return str(e), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)