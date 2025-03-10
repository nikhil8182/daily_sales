# Sales Tracking App

A Flask web application for tracking sales activities, including PR visits and telecaller activities.

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
5. Run the application:
   ```
   python run.py
   ```
6. Access the application at http://localhost:5001

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

# Install PostgreSQL if you want to use it instead of SQLite
sudo apt install -y postgresql postgresql-contrib
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

#### 6. Set Up Environment Variables

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
DATABASE_URL=sqlite:///sales.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://username:password@localhost/salesdb
```

#### 7. Set Up Database (PostgreSQL - Optional)

If using PostgreSQL instead of SQLite:

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE salesdb;
CREATE USER salesuser WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE salesdb TO salesuser;
\q

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://salesuser:your-password@localhost/salesdb
```

#### 8. Set Up Gunicorn Service

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

#### 9. Configure Nginx

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

#### 10. Set Up Webhook for Automatic Updates (Optional)

To enable the webhook for automatic updates:

1. Ensure the webhook endpoint is accessible from GitHub/GitLab
2. Set up a webhook in your Git repository settings pointing to:
   ```
   http://your_domain_or_ip/webhook
   ```
3. Make sure the application has permissions to execute git commands

#### 11. Set Up SSL with Let's Encrypt (Recommended)

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

The application uses SQLAlchemy with SQLite by default. The database will be created automatically when the application is first run. You can switch to other database backends by changing the `DATABASE_URL` environment variable.

### Database Backup (EC2)

To back up your SQLite database on EC2:

```bash
# Create a backup directory
mkdir -p /var/www/salesapp/backups

# Back up the database (run daily with cron)
cp /var/www/salesapp/instance/sales.db /var/www/salesapp/backups/sales_$(date +%Y-%m-%d).db
```

For PostgreSQL:

```bash
# PostgreSQL backup
pg_dump -U salesuser salesdb > /var/www/salesapp/backups/salesdb_$(date +%Y-%m-%d).sql
```

### Setting Up Automated Backups

Create a cron job for daily backups:

```bash
# Open crontab editor
crontab -e

# Add the following line for daily backups at 2 AM
0 2 * * * cp /var/www/salesapp/instance/sales.db /var/www/salesapp/backups/sales_$(date +\%Y-\%m-\%d).db

# For PostgreSQL
# 0 2 * * * pg_dump -U salesuser salesdb > /var/www/salesapp/backups/salesdb_$(date +\%Y-\%m-\%d).sql
```

### Database Migrations

If you need to make changes to the database schema after deployment, you might need to perform migrations:

1. Back up your existing database
2. Apply schema changes through your application or manually
3. Restart the application service:
   ```bash
   sudo systemctl restart salesapp
   ```

## Project Structure

```
daily_sales/
│
├── app/
│   ├── __init__.py
│   ├── models.py
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
│       └── main.py
│
├── config.py
├── run.py
├── wsgi.py
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
- Database connection: Verify database credentials

### Database Issues

If you have database problems:

```bash
# For SQLite
sqlite3 /var/www/salesapp/instance/sales.db .tables

# For PostgreSQL
sudo -u postgres psql -d salesdb -c "\dt"
```

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
- Check ports: `sudo netstat -tulpn | grep LISTEN`