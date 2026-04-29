# Hendor's Report Studio V14.2 Cloud/Web Mirror

Keeps the V14.2 look and workflow for browser/cloud use.

Local test:
1. Run START_LOCAL.bat
2. Open http://localhost:1420
3. Login admin / admin123

Cloud deployment:
- Build command: pip install -r requirements.txt
- Start command: gunicorn app:app
- Health check: /health

Browser safety limits:
- Windows Snip and Open Local Folder cannot work exactly in cloud browser mode.
- Use paste/upload/download equivalents for internet use.
