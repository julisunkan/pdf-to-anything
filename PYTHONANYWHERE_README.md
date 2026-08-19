# PythonAnywhere README

This directory contains everything needed to deploy PDF to Anything on PythonAnywhere.

## Quick Start

### Option 1: Automated Setup (Recommended)

1. Log into **PythonAnywhere bash console**
2. Run:
   ```bash
   cd ~
   git clone https://github.com/YOUR_USERNAME/pdf-to-anything.git
   cd pdf-to-anything
   bash pythonanywhere_quick_setup.sh YOUR_USERNAME
   ```
3. Edit `.env` with your settings:
   ```bash
   nano .env
   ```
4. Go to **Web apps** in dashboard
5. Add new web app: **Manual configuration** → **Python 3.10**
6. Set WSGI file to: `/home/YOUR_USERNAME/pdf-to-anything/pythonanywhere_wsgi.py`
7. Set virtualenv to: `/home/YOUR_USERNAME/.virtualenvs/pdf-to-anything`
8. Add static mapping: `/static/` → `/home/YOUR_USERNAME/pdf-to-anything/static`
9. Click **Reload**

### Option 2: Manual Setup

See `PYTHONANYWHERE_DEPLOYMENT.md` for detailed instructions.

## Files Included

- **pythonanywhere_wsgi.py** - WSGI entry point for web app
- **pythonanywhere_setup.sh** - Full setup script
- **pythonanywhere_quick_setup.sh** - Quick setup script
- **scheduled_cleanup.sh** - Cleanup task script
- **production_check.py** - Pre-deployment verification
- **PYTHONANYWHERE_DEPLOYMENT.md** - Complete documentation

## Configuration

### Critical .env Settings for PythonAnywhere

```bash
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-very-secret-key
ADMIN_PASSWORD=your-admin-password
SQLALCHEMY_DATABASE_URI=sqlite:////home/YOUR_USERNAME/pdf-to-anything/pdf_to_anything.db
MAX_UPLOAD_SIZE_MB=100  # Adjust for free account
FILE_RETENTION_HOURS=2
```

## Common Tasks

### View Logs
```bash
cd /home/YOUR_USERNAME/pdf-to-anything
tail -f /var/log/YOUR_USERNAME.pythonanywhere.com.error.log
```

### Run Cleanup Manually
```bash
cd /home/YOUR_USERNAME/pdf-to-anything
source /home/YOUR_USERNAME/.virtualenvs/pdf-to-anything/bin/activate
python cleanup.py
```

### Update Code
```bash
cd /home/YOUR_USERNAME/pdf-to-anything
git pull origin main
# Then reload in dashboard
```

### Check Configuration
```bash
cd /home/YOUR_USERNAME/pdf-to-anything
source /home/YOUR_USERNAME/.virtualenvs/pdf-to-anything/bin/activate
python production_check.py
```

## Troubleshooting

### 502 Bad Gateway
1. Check error logs in dashboard
2. Verify WSGI file path
3. Verify virtualenv path
4. Check .env file exists
5. Reload web app

### Import Errors
```bash
cd /home/YOUR_USERNAME/pdf-to-anything
source /home/YOUR_USERNAME/.virtualenvs/pdf-to-anything/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Storage Issues
```bash
quota  # Check disk usage
cd /home/YOUR_USERNAME/pdf-to-anything
du -sh uploads/ outputs/ temp/
```

## Performance Tips

### For Free Account
- Keep `MAX_UPLOAD_SIZE_MB` low (50-100)
- Set `WORKER_THREADS=2`
- Set `FILE_RETENTION_HOURS=1`
- Regularly run cleanup

### For Paid Account
- Can increase limits
- Add scheduled cleanup task
- Consider PostgreSQL addon

## Support

- **PythonAnywhere Help:** https://help.pythonanywhere.com/
- **Full Documentation:** See `PYTHONANYWHERE_DEPLOYMENT.md`
- **Project Issues:** https://github.com/YOUR_USERNAME/pdf-to-anything/issues

## Next Steps

1. ✅ Run setup script
2. ✅ Configure .env
3. ✅ Create web app in dashboard
4. ✅ Set WSGI and virtualenv paths
5. ✅ Add static files mapping
6. ✅ Reload web app
7. ✅ Verify app works
8. ✅ Access admin panel
9. ✅ Set up scheduled cleanup (optional)
10. ✅ Configure backup (optional)

---

**Version:** 1.0.0
**Updated:** 2024-08-19
