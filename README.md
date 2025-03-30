# VidGuard Extract API

VidGuard Extract is an API designed to block annoying and obscene ads from video content. Simply submit your embedded video URL and get a clean download link in return.

## Table of Contents
- [Repository Setup](#repository-setup)
- [Installation](#installation)
  - [Windows](#windows)
  - [macOS](#macos)
  - [Linux](#linux)
- [Configuration](#configuration)
- [Running in Development](#running-in-development)
- [Production Deployment](#production-deployment)
  - [Setting up as a System Service](#setting-up-as-a-system-service)
  - [Nginx Configuration](#nginx-configuration)
- [API Usage](#api-usage)

## Repository Setup

Clone the repository from the Git server:

```bash
git clone /CP0004/vidguard-extract.git
cd vidguard-extract
```

## Installation

### Windows

1. Install Python 3.8 or higher if not already installed
2. Set up a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### macOS

1. Install Python 3.8 or higher if not already installed
2. Set up a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Linux

1. Install Python 3.8 or higher if not already installed
2. Set up a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Create a `.env` file based on the provided example:

```bash
cp .env.example .env
```

Edit the `.env` file to configure your environment variables:
- `BASE_URL`: The base URL for your API
- `PORT`: The port number the API should run on

## Running in Development

### Windows

For local development with auto-reload:

```bash
uvicorn src.main:app --host 127.0.0.1 --port 8002 --reload
```

### macOS and Linux

For local development with auto-reload:

```bash
uvicorn src.main:app --host 127.0.0.1 --port 8002 --reload
```

For global access (on a server):

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload
```

Note: The port can be changed according to your requirements.

## Production Deployment

### Prerequisites

Install required packages on your VPS:

```bash
sudo apt update
sudo apt install git python3 python3-pip python3-venv nginx -y
```

### Setting up as a System Service

1. Clone and set up the project as described in the Installation section.

2. Create a systemd service file:

```bash
sudo nano /etc/systemd/system/vidguard.service
```

3. Add the following content (adjust paths as needed):

```ini
[Unit]
Description=VidGuard Extract API
After=network.target

[Service]
User=root
WorkingDirectory=/root/project/python/vidguard-extract
ExecStart=/root/project/python/vidguard-extract/.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8002
Restart=always
EnvironmentFile=/root/project/python/vidguard-extract/.env

[Install]
WantedBy=multi-user.target
```

4. Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable vidguard.service
sudo systemctl start vidguard.service
```

5. Check service status:

```bash
sudo systemctl status vidguard.service
```

6. View logs if needed:

```bash
journalctl -u vidguard.service -f
```

### Nginx Configuration

1. Start and enable Nginx:

```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

2. Create an Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/api-public
```

3. Add the following configuration (adjust the server_name as needed):

```nginx
server {
    listen 80;
    server_name 45.88.9.31;

    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket Support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}
```

4. Create a symbolic link to enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/api-public /etc/nginx/sites-enabled/
```

5. Test the Nginx configuration:

```bash
sudo nginx -t
```

6. Restart Nginx to apply changes:

```bash
sudo systemctl restart nginx
```

## API Usage

The API provides the following endpoints:

- `GET /`: Welcome message
- `GET /extract?url={url}`: Extract video URL from the provided embed URL
- `GET /proxy_stream?url={url}`: Stream the video content

Example usage:
```
http://your-server-ip/extract?url=https://vidguard.to/embed-xxx
```
