# Digital Business Card Application

A web-based digital business card solution that lets users create, edit and share their contact information securely using QR codes authenticated securely via oAuth Providers.

## Features

- Secure authentication via oAuth Authentication Providers
- Create and edit your digital business card
- Preview your card in a clean, professional format
- Generate QR codes for easy sharing
- Download contact information as VCF (vCard) file
- Protected access through Cloudflare Zero Trust

## How to Access

1. Visit https://card.runningdigitally.com/
2. Authenticate using your oAuth Provider of choice
3. Once logged in, you can:
   - Edit your business card details
   - Preview how others will see your card
   - Generate a QR code for easy sharing
   - Download your contact information as a VCF file

## Technical Details

### Built With
- Flask (Python web framework)
- SQLite database for user data storage
- QR code generation for easy sharing
- VCF (vCard) format support
- Cloudflare Zero Trust for authentication

### Local Development Setup

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Configure your Cloudflare Access settings

### Docker Deployment

```bash
docker build -t digital-business-card .
docker run -p 8080:8080 digital-business-card
```

## Cloudflare Zero Trust Configuration

1. In Cloudflare Zero Trust Dashboard:
   - Go to Access -> Applications
   - Create a new "Self-hosted" application
   - Set application domain to card.runningdigitally.com
   - Configure access policies as needed
2. Enable "Service Auth" in the application settings
3. Note your Application Audience (AUD) tag
4. Update your environment variables with the AUD tag

## Security

- All access is protected by Cloudflare Zero Trust
- User data is stored securely in SQLite database
- JWT token validation ensures secure authentication
