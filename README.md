# Browse Analyze Download (Flask + ydata-profiling)

Beginner-friendly Flask app to upload CSV/Excel datasets, preview first rows, and generate an automated EDA report using ydata-profiling (formerly pandas-profiling).

## Features
- Upload CSV or Excel files
- Preview first 5–10 rows
- Generate and view/download EDA HTML report

## Project Structure
```
Browse Analyze Download/
├─ app.py
├─ templates/
│  ├─ base.html
│  └─ index.html
├─ static/
│  └─ styles.css
├─ uploads/            # temporary uploaded files
├─ reports/            # generated HTML reports
├─ README.md
└─ pyproject.toml      # uv dependency management
```

## Prerequisites
- Python 3.10+
- uv package manager

Install uv (if needed):
```bash
pip install uv
```

## Setup
Install dependencies with uv:
```bash
uv sync
```

## Run the app
```bash
uv run flask --app app run --debug
```

Then open your browser at http://127.0.0.1:5000/

## Usage
1. Choose a CSV or Excel file and upload.
2. Preview appears (first 10 rows).
3. Click "Generate EDA" to produce the HTML report.
4. Open the report link or download it.

## Notes
- Supported Excel engine: openpyxl
- Uploaded files and reports are stored in the local `uploads/` and `reports/` folders. They are not persisted or versioned.

## Safety & Limits
- Only basic file type checks are performed. Do not upload sensitive data.
- Large files may take time to process.

## Configuration
- Environment variables (optional):
  - `FLASK_SECRET_KEY`: secret key for sessions/flashing (defaults to a development key).
- File size: The app caps uploads at 200 MB by default. Adjust in `app.py` at `MAX_CONTENT_LENGTH` if needed.

## How it works
- `POST /upload`: saves the uploaded file to `uploads/`, reads it via pandas, renders a preview table.
- `POST /generate`: builds a ydata-profiling `ProfileReport` and writes HTML to `reports/`, then shows a link and an embedded `<iframe>`.

## Troubleshooting
- If you see `ModuleNotFoundError: pkg_resources`, make sure `setuptools` is installed (already listed in `pyproject.toml`). Re-run: `uv sync`.
- For Excel files failing to load, ensure the file is `.xlsx`/`.xls` and that `openpyxl` is installed (already listed). CSV is most reliable for large files.
- If EDA generation is slow or memory-heavy, consider uploading a sampled dataset or increase the instance memory/CPU.

---

## Deploying to AWS EC2 (Ubuntu) with Gunicorn + Nginx
Below is a minimal, production-style setup. Replace `your_domain` if you have one, or use the server IP.

### 1) Create and connect to an EC2 instance
- Launch an Ubuntu 22.04 (or similar) t2.micro (or larger) instance.
- Open security group ports: 22 (SSH), 80 (HTTP). Add 443 if using TLS later.
- SSH into the instance:
```bash
ssh -i /path/to/key.pem ubuntu@EC2_PUBLIC_IP
```

### 2) Install system packages
```bash
sudo apt update -y
sudo apt install -y python3 python3-venv python3-pip nginx git
python3 -V
pip3 install --upgrade pip
pip3 install uv
```

### 3) Get your app onto the server
Option A: Git clone your repository
```bash
cd /var/www
sudo mkdir -p browse-analyze-download && sudo chown $USER:$USER browse-analyze-download
cd browse-analyze-download
git clone <your_repo_url> .
```

Option B: Upload zip or files from local
```bash
# from your local machine
scp -i /path/to/key.pem -r "Browse Analyze Download" ubuntu@EC2_PUBLIC_IP:/var/www/browse-analyze-download
```

### 4) Install Python dependencies with uv
```bash
cd /var/www/browse-analyze-download
uv sync
```

Install a production WSGI server (Gunicorn) inside the project environment:
```bash
uv add gunicorn
```

Test Gunicorn process:
```bash
uv run gunicorn -w 2 -k gthread -b 127.0.0.1:8000 app:app
```
Visit `http://SERVER_IP:8000` from the server (e.g., `curl 127.0.0.1:8000`) to confirm it serves HTML.
Press Ctrl+C to stop for now.

### 5) Create a systemd service for Gunicorn
```bash
sudo tee /etc/systemd/system/browse-analyze.service > /dev/null << 'EOF'
[Unit]
Description=Browse Analyze Download Gunicorn Service
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/browse-analyze-download
Environment=FLASK_SECRET_KEY=change-me
ExecStart=/usr/bin/bash -lc 'cd /var/www/browse-analyze-download && uv run gunicorn -w 2 -k gthread -b 127.0.0.1:8000 app:app'
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable browse-analyze
sudo systemctl start browse-analyze
sudo systemctl status browse-analyze --no-pager
```

### 6) Configure Nginx as a reverse proxy
```bash
sudo tee /etc/nginx/sites-available/browse-analyze > /dev/null << 'EOF'
server {
    listen 80;
    server_name your_domain_or_server_ip;

    client_max_body_size 200M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/browse-analyze /etc/nginx/sites-enabled/browse-analyze || true
sudo nginx -t
sudo systemctl restart nginx
```

Your app should now be available at `http://EC2_PUBLIC_IP/`.

### 7) Optional: HTTPS with Let’s Encrypt
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain
```

### 8) Logs and maintenance
- App logs: `sudo journalctl -u browse-analyze -f`
- Nginx logs: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- Clean old uploads/reports periodically if needed: `rm -f uploads/* reports/*`

### 9) Common deployment issues
- `502 Bad Gateway`: Gunicorn not running or bound to wrong address/port; check service logs.
- `413 Request Entity Too Large`: increase `client_max_body_size` in Nginx and align with Flask `MAX_CONTENT_LENGTH`.
- Permission errors in `/var/www/...`: ensure correct `User` and directory ownership.

---

## Local development tips (Windows)
- Use `uv run flask --app app run --debug` for hot reload.
- If Excel uploads fail on Windows, install Microsoft Visual C++ Build Tools if prompted, or prefer CSV.
- Long paths or spaces in directories are okay; the app uses relative paths.

