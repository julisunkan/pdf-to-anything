# PythonAnywhere Web App Configuration
# This file contains instructions for setting up PDF to Anything on PythonAnywhere

## Step-by-Step Setup Instructions

### 1. Initial Setup via Bash Console

```bash
# Copy and paste this command in PythonAnywhere bash console
cd ~
git clone https://github.com/YOUR_USERNAME/pdf-to-anything.git
cd pdf-to-anything
bash pythonanywhere_setup.sh
```

### 2. Configure Environment Variables

1. Open `.env` file:
   ```bash
   nano /home/YOUR_USERNAME/pdf-to-anything/.env
   ```

2. Update these critical settings:
   ```
   FLASK_ENV=production
   DEBUG=False
   SECRET_KEY=your-very-secret-key-change-this
   ADMIN_PASSWORD=your-secure-admin-password
   SQLALCHEMY_DATABASE_URI=sqlite:////home/YOUR_USERNAME/pdf-to-anything/pdf_to_anything.db
   ```

3. Press `Ctrl+X`, then `Y`, then `Enter` to save

### 3. Create Web App in PythonAnywhere Dashboard

1. Go to **PythonAnywhere Dashboard** → **Web apps**
2. Click **Add a new web app**
3. Choose:
   - **Manual configuration** (NOT "Flask")
   - **Python 3.10** (or latest available)

4. After creation, click on the web app to configure it

### 4. Configure WSGI File

1. In Web app settings, find **WSGI configuration file**
2. Click on the file path to edit it
3. Replace ALL content with:

```python
# PythonAnywhere WSGI configuration for PDF to Anything
import sys
import os
from pathlib import Path

# Add project to path
project_home = '/home/YOUR_USERNAME/pdf-to-anything'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Change to project directory
os.chdir(project_home)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

# Create Flask app
from app import create_app
app = create_app()
```

4. Save (Ctrl+X → Y → Enter)

### 5. Configure Virtualenv

1. In Web app settings, find **Virtualenv**
2. Click to set virtualenv path
3. Enter: `/home/YOUR_USERNAME/.virtualenvs/pdf-to-anything`
4. Click **Configure** if prompted

### 6. Configure Static Files

1. In Web app settings, add URL/directory mapping:
   - **URL:** `/static/`
   - **Directory:** `/home/YOUR_USERNAME/pdf-to-anything/static`
   - Click **Add**

2. (Optional) Configure media files:
   - **URL:** `/uploads/`
   - **Directory:** `/home/YOUR_USERNAME/pdf-to-anything/uploads`
   - Click **Add**

### 7. Reload Web App

1. Click the green **Reload** button at the top
2. Wait for the server to restart (usually 5-10 seconds)
3. Visit your web app at: `https://YOUR_USERNAME.pythonanywhere.com`

### 8. Verify Installation

- Visit homepage: `https://YOUR_USERNAME.pythonanywhere.com`
- Check admin: `https://YOUR_USERNAME.pythonanywhere.com/admin`
- View logs: Click **Logs** in Web app settings

---

## Configuration & Management

### Update Environment Variables

Edit via bash console:
```bash
cd /home/YOUR_USERNAME/pdf-to-anything
nano .env
```

Then reload web app in dashboard.

### View Logs

1. **Web app logs:** Web app settings → Logs → View
2. **Error logs:** Most recent errors displayed
3. **Access logs:** Request history

### Manual Database Reset

```bash
cd /home/YOUR_USERNAME/pdf-to-anything
source /home/YOUR_USERNAME/.virtualenvs/pdf-to-anything/bin/activate
rm pdf_to_anything.db  # Warning: Deletes all data
python initialize.py
```

### Manual Cleanup

```bash
cd /home/YOUR_USERNAME/pdf-to-anything
source /home/YOUR_USERNAME/.virtualenvs/pdf-to-anything/bin/activate
python cleanup.py
```

### Check System Requirements

```bash
cd /home/YOUR_USERNAME/pdf-to-anything
source /home/YOUR_USERNAME/.virtualenvs/pdf-to-anything/bin/activate
python diagnose.py
```

---

## Troubleshooting

### 502 Bad Gateway Error

1. Check Web app logs for errors
2. Verify WSGI file path is correct
3. Verify virtualenv path is correct
4. Check .env file exists and is readable
5. Try reloading the web app

### Import Errors

Re-install dependencies:
```bash
cd /home/YOUR_USERNAME/pdf-to-anything
source /home/YOUR_USERNAME/.virtualenvs/pdf-to-anything/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Database Locked

SQLite file is locked by another process. Try:
```bash
cd /home/YOUR_USERNAME/pdf-to-anything
rm pdf_to_anything.db-wal pdf_to_anything.db-shm 2>/dev/null
```

Then reload web app.

### File Upload Issues

Check directory permissions:
```bash
ls -la /home/YOUR_USERNAME/pdf-to-anything/uploads
chmod 755 /home/YOUR_USERNAME/pdf-to-anything/uploads
chmod 755 /home/YOUR_USERNAME/pdf-to-anything/outputs
```

### Storage Issues

Check PythonAnywhere disk usage:
```bash
quota
```

To see what's using space:
```bash
cd /home/YOUR_USERNAME/pdf-to-anything
du -sh *
```

Clean up old files:
```bash
rm -rf uploads/* outputs/* temp/*
python cleanup.py
```

---

## Performance Optimization

### For Free PythonAnywhere Account

1. **Reduce worker threads:**
   ```
   WORKER_THREADS=2
   ```

2. **Reduce file retention:**
   ```
   FILE_RETENTION_HOURS=1
   ```

3. **Set smaller limits:**
   ```
   MAX_UPLOAD_SIZE_MB=100
   MAX_FILES_PER_UPLOAD=10
   ```

### For Paid Accounts

1. Enable scheduled task for cleanup (under "Tasks")
2. Increase upload limits if needed
3. Consider using PostgreSQL instead of SQLite
4. Enable caching headers in WSGI file

---

## Database Backup

### Manual Backup

```bash
cd /home/YOUR_USERNAME/pdf-to-anything
cp pdf_to_anything.db pdf_to_anything.db.backup.$(date +%Y%m%d_%H%M%S)
```

### Automatic Backup

Create scheduled task in PythonAnywhere "Tasks":
```bash
cd /home/YOUR_USERNAME/pdf-to-anything && cp pdf_to_anything.db pdf_to_anything.db.backup.$(date +\%Y\%m\%d_\%H\%M\%S)
```

---

## Security Checklist

- [ ] Change `SECRET_KEY` in .env
- [ ] Change `ADMIN_PASSWORD` in .env
- [ ] Set `DEBUG=False`
- [ ] Use HTTPS (enabled by default on PythonAnywhere)
- [ ] Configure file retention limits
- [ ] Enable automatic cleanup
- [ ] Regularly backup database
- [ ] Monitor disk usage

---

## Support

- **PythonAnywhere Help:** https://help.pythonanywhere.com/
- **Project Repository:** https://github.com/YOUR_USERNAME/pdf-to-anything
- **Issues:** GitHub Issues tab

---

## Production Considerations

### Database

SQLite works fine for small deployments, but for production consider:
- PostgreSQL (via PythonAnywhere PostgreSQL add-on)
- MySQL (via PythonAnywhere MySQL add-on)

### Scaling

PythonAnywhere free accounts have limitations. For high traffic:
- Upgrade to paid account
- Increase number of worker processes
- Consider external storage
- Implement job queue (Celery + Redis)

### Email Notifications

Add to .env if implementing email:
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

---

**Last Updated:** 2024-08-19
**Version:** 1.0.0
