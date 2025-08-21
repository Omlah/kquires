# Environment Setup Guide

This is a quick reference for setting up your environment variables in Kquires.

## 🚀 Quick Setup

### 1. Copy Environment Templates

```bash
# For local development
cp .envs/.local/.django.example .envs/.local/.django
cp .envs/.local/.postgres.example .envs/.local/.postgres

# For production
cp .envs/.production/.django.example .envs/.production/.django
cp .envs/.production/.postgres.example .envs/.production/.postgres
```

### 2. Edit with Your Values

```bash
# Edit local environment
nano .envs/.local/.django
nano .envs/.local/.postgres

# Edit production environment
nano .envs/.production/.django
nano .envs/.production/.postgres
```

### 3. Generate Django Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 📁 File Structure

```
.envs/
├── .local/
│   ├── .django          # Local Django settings
│   ├── .django.example  # Template for Django settings
│   ├── .postgres        # Local database settings
│   └── .postgres.example # Template for database settings
└── .production/
    ├── .django          # Production Django settings
    ├── .django.example  # Template for Django settings
    ├── .postgres        # Production database settings
    └── .postgres.example # Template for database settings
```

## 🔑 Required Variables

### Django Settings
- `DJANGO_SECRET_KEY` - Your Django secret key
- `DJANGO_ADMIN_URL` - Custom admin URL
- `DJANGO_ALLOWED_HOSTS` - Comma-separated list of allowed hosts

### Database Settings
- `POSTGRES_HOST` - Database host
- `POSTGRES_PORT` - Database port
- `POSTGRES_DB` - Database name
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password

### API Keys
- `MAILGUN_API_KEY` - Mailgun API key
- `MAILGUN_DOMAIN` - Mailgun domain
- `SENTRY_DSN` - Sentry DSN for error monitoring

## ⚠️ Security Reminders

- **NEVER** commit `.env` files to Git
- **NEVER** share credentials in chat/email
- **ALWAYS** use different credentials for each environment
- **ALWAYS** use strong, unique passwords
