# Sales Tracking App

A Flask web application for tracking sales activities using Firebase Firestore, including PR visits and telecaller activities.

## Features

### PR Visits Section
- Track visit start time
- Record client name and PR name
- Document manager in-charge
- Monitor visit status
- Add notes

### Telecaller (TC) Section
- Track calls made
- Record manager in charge
- Monitor visits booked and confirmed
- Track leads acquired and bucket leads

## Installation and Setup

### Prerequisites
You need a Firebase project with Firestore set up:
1. Create a Firebase project at https://console.firebase.google.com/
2. Set up a Firestore database in Native mode
3. Download the service account key file and save it as `fb_key_1.json` in the project root directory

### Local Development

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install requirements:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file based on `.env.example`
5. Add your Firebase service account key file as `fb_key_1.json` in the project root
6. Run the application:
   ```
   python run.py
   ```
7. Access the application at http://localhost:5001

### Production Deployment on AWS EC2

Here's a step-by-step guide to deploy this application on an AWS EC2 instance:

#### 1. Launch an EC2 Instance

1. Sign in to the AWS Management Console
2. Navigate to EC2 and click "Launch Instance"
3. Choose an Amazon Machine Image (AMI) - Ubuntu Server 22.04 LTS is recommended
4. Select an instance type (t2.micro is eligible for free tier)
5. Configure security groups to allow:
   - SSH (port 22) from your IP
   - HTTP (port 80) from anywhere
   - HTTPS (port 443) from anywhere
6. Create or select an existing key pair for SSH access
7. Launch the instance

#### 2. Connect to Your EC2 Instance

Using SSH:
```
ssh -i /path/to/your-key.pem ubuntu@your-ec2-public-dns
```

#### 3. Update and Install Dependencies

```bash
# Update package list and upgrade packages
sudo apt update
sudo apt upgrade -y

# Install Python, pip, git, and other dependencies
sudo apt install -y python3-pip python3-venv git nginx
```

#### 4. Clone the Repository

```bash
# Navigate to where you want to store the application
cd /var/www
sudo mkdir salesapp
sudo chown ubuntu:ubuntu salesapp
cd salesapp

# Clone the repository
git clone https://your-repository-url.git .
```

#### 5. Set Up Python Virtual Environment

```bash
# Create a virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

#### 6. Set Up Environment Variables and Firebase

```bash
# Create .env file
cp .env.example .env
nano .env
```

Edit the .env file with production settings:
```
FLASK_ENV=production
FLASK_APP=wsgi.py
SECRET_KEY=your-secure-random-string
```

Important: Add your Firebase service account key file:
```bash
# Copy your Firebase service account key to the server
scp -i /path/to/your-key.pem /path/to/your/fb_key_1.json ubuntu@your-ec2-public-dns:/var/www/salesapp/fb_key_1.json
```

#### 7. Set Up Gunicorn Service

Create a system service file:

```bash
sudo nano /etc/systemd/system/salesapp.service
```

Add the following content:

```
[Unit]
Description=Gunicorn instance to serve sales tracking app
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/salesapp
Environment="PATH=/var/www/salesapp/venv/bin"
EnvironmentFile=/var/www/salesapp/.env
ExecStart=/var/www/salesapp/venv/bin/gunicorn --workers 3 --bind unix:salesapp.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

Start and enable the service:

```bash
sudo systemctl start salesapp
sudo systemctl enable salesapp
sudo systemctl status salesapp
```

#### 8. Configure Nginx

Create an Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/salesapp
```

Add the following content:

```
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/salesapp/salesapp.sock;
    }
}
```

Enable the site and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/salesapp /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

#### 9. Set Up Webhook for Automatic Updates (Optional)

To enable the webhook for automatic updates:

1. Ensure the webhook endpoint is accessible from GitHub/GitLab
2. Set up a webhook in your Git repository settings pointing to:
   ```
   http://your_domain_or_ip/webhook
   ```
3. Make sure the application has permissions to execute git commands

#### 10. Set Up SSL with Let's Encrypt (Recommended)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain
```

Follow the prompts to set up SSL.

## Webhook

The application includes a webhook endpoint at `/webhook` that can be used to automatically pull updates from the git repository:

```
curl -X POST http://your-server-address/webhook
```

You can also use this webhook with GitHub, GitLab, or other Git providers to automatically deploy updates.

## Database Management

The application uses Firebase Firestore for its database. Data modeling is documented in `app/models.py` and all database operations are handled by `app/firebase_db.py`.

### Firebase Firestore Collections

The application uses three main collections:
- `team_members`: Stores PR, TC, and SM (Sales Manager) team member data
- `pr_visits`: Stores PR visit activity information
- `tc_activities`: Stores telecaller activity information

### Firebase Project Setup

1. Create a project in the Firebase console (https://console.firebase.google.com/)
2. Set up Firestore database in "Native" mode (not Datastore mode)
3. Create a service account and download the key file
4. Place the key file as `fb_key_1.json` in the project root directory

### Backing Up Firestore Data

You can export Firestore data using the Firebase Admin SDK or the gcloud CLI:

```bash
# Install gcloud CLI (if not already installed)
curl https://sdk.cloud.google.com | bash

# Authenticate 
gcloud auth login

# Set your project
gcloud config set project your-firebase-project-id

# Export data to Google Cloud Storage
gcloud firestore export gs://your-backup-bucket-name/backups/$(date +%Y-%m-%d)
```

## Project Structure

```
daily_sales/
│
├── app/
│   ├── __init__.py
│   ├── models.py          # Contains documentation of Firebase data models
│   ├── firebase_db.py     # Contains all Firebase database operations
│   ├── error_handlers.py
│   ├── static/
│   │   └── css/
│   │       └── main.css
│   ├── templates/
│   │   ├── layout.html
│   │   ├── index.html
│   │   ├── add_pr_visit.html
│   │   ├── add_tc_activity.html
│   │   ├── team.html
│   │   └── errors/
│   │       ├── 404.html
│   │       ├── 500.html
│   │       ├── 403.html
│   │       └── 400.html
│   └── routes/
│       ├── __init__.py
│       ├── main.py
│       ├── pr.py
│       └── tc.py
│
├── config.py
├── run.py
├── wsgi.py
├── fb_key_1.json          # Firebase service account key (not committed to git)
├── requirements.txt
├── .env.example
└── README.md
```

## Troubleshooting on EC2

### Application Won't Start

If the application won't start on EC2, check the logs:

```bash
sudo systemctl status salesapp
sudo journalctl -u salesapp
```

Common issues:
- Permission problems: Check file permissions in /var/www/salesapp
- Environment variables: Make sure .env file exists and is correctly formatted
- Firebase setup: Verify that fb_key_1.json exists and has correct permissions
- Network issues: Ensure the server can connect to Firebase

### Firebase Connection Issues

If you're having trouble connecting to Firebase:
- Check that the firebase key file exists and has the correct permissions
- Verify that your Firebase project has Firestore enabled in Native mode
- Ensure your IAM permissions are correct for the service account
- Check if there are any outbound firewall rules blocking the connection

### Nginx Problems

Check Nginx configuration:

```bash
sudo nginx -t
sudo systemctl status nginx
sudo journalctl -u nginx
```

### Other Issues

- Check file permissions: `sudo chown -R ubuntu:www-data /var/www/salesapp`
- Restart services: `sudo systemctl restart salesapp nginx`
- Check port availability: `sudo netstat -tulpn | grep LISTEN`
- View application logs: `journalctl -u salesapp -f`