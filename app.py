from flask import Flask, request, jsonify, render_template
from jose import jwt
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

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

print(f"Generated DEV_MODE_TOKEN: {DEV_MODE_TOKEN}")

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
        
        if not token_aud or token_aud != EXPECTED_AUD:
            return render_template('home.html', error="Invalid audience claim")
        
        # Extract email from the token
        email = decoded.get('email', 'No email found')
        return render_template('home.html', email=email)
    
    except Exception as e:
        print(f"Error decoding token: {str(e)}")
        return render_template('home.html', error=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)