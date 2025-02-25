# Flask JWT Token Display App

This application displays the email address from Cloudflare Access JWT tokens.

## Build and Run

```bash
docker build -t flask-jwt-app .
docker run -p 8080:8080 flask-jwt-app
```

## Cloudflare Zero Trust Setup

1. Go to Cloudflare Zero Trust Dashboard
2. Navigate to Access -> Applications
3. Create a new application
4. Select "Self-hosted" 
5. Configure the following:
   - Application Name: Flask JWT App
   - Session Duration: Your preferred duration
   - Application Domain: Your application domain
   - Add a policy to define who can access the application

### Configure Application Settings
1. Go to the application settings
2. Under "Zero Trust" settings, make sure "Service Auth" is enabled
3. Note down the Application Audience (AUD) tag

### Set up Cloudflare Tunnel
1. Install cloudflared
2. Authenticate cloudflared:
   ```bash
   cloudflared login
   ```
3. Create a tunnel:
   ```bash
   cloudflared tunnel create flask-jwt-app
   ```
4. Configure the tunnel (create config.yml):
   ```yaml
   tunnel: <YOUR-TUNNEL-ID>
   credentials-file: /root/.cloudflared/<YOUR-TUNNEL-ID>.json
   ingress:
     - hostname: your-app-domain.com
       service: http://localhost:8080
     - service: http_status:404
   ```
5. Run the tunnel:
   ```bash
   cloudflared tunnel run flask-jwt-app
   ```

The application will now be accessible through your Cloudflare Zero Trust domain and will display the email address of authenticated users.
