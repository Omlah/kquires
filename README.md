# Kquires Knowledge Base

A comprehensive Django-based knowledge management system designed to organize, manage, and share information across organizations. Kquires provides a centralized platform for creating, categorizing, and accessing knowledge articles with advanced user management and departmental organization.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Features

- **Knowledge Base Management** - Create, organize, and maintain knowledge articles with rich content
- **Department Organization** - Structure content by departments for better organization  
- **Category System** - Categorize articles for easy navigation and discovery
- **Ticket System** - Integrated ticketing system for issue tracking and resolution
- **User Management** - Comprehensive user authentication and role-based access control
- **Notifications** - Real-time notification system for important updates
- **Dashboard Analytics** - Administrative dashboard with statistics and insights
- **Multi-language Support** - Internationalization support (English, French, Portuguese, Arabic)
- **Activity Logging** - Comprehensive logging system for audit trails
- **Message Alerts** - Automated alert system for important events
- **Responsive Design** - Mobile-friendly interface with Bootstrap 5
- **Real-time Features** - WebSocket support for live updates

## Tech Stack

- **Backend**: Django 4.x with Python 3.12
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Database**: PostgreSQL (production), SQLite (development)
- **Task Queue**: Celery with Redis
- **Web Server**: Nginx (production)
- **Containerization**: Docker & Docker Compose
- **Asset Management**: Webpack
- **Testing**: pytest, coverage
- **Code Quality**: Ruff, mypy
- **Documentation**: Sphinx

## Prerequisites

- Python 3.12+
- Docker and Docker Compose
- Node.js and npm (for frontend assets)
- PostgreSQL (for production)

## Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/Omlah/kquires.git
   cd kquires
   ```

2. **Build and run with Docker Compose**
   ```bash
   # For local development
   docker-compose -f docker-compose.local.yml up --build
   
   # For production
   docker-compose -f docker-compose.production.yml up --build
   ```

3. **Create a superuser**
   ```bash
   docker-compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser
   ```

4. **Access the application**
   - Main application: http://localhost:8000
   - Admin panel: http://localhost:8000/admin
   - Mailpit (email testing): http://localhost:8025

### Manual Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements/local.txt
   npm install
   ```

2. **Set environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

## Configuration

Detailed configuration settings can be found in the [Cookiecutter Django settings documentation](https://cookiecutter-django.readthedocs.io/en/latest/1-getting-started/settings.html).

## User Management

### Creating User Accounts

- **Normal User Account**: 
  1. Navigate to the Sign Up page
  2. Fill out the registration form
  3. Check your console for the email verification message (in development)
  4. Click the verification link to activate your account

- **Superuser Account**: Create administrative users with full system access:
  ```bash
  python manage.py createsuperuser
  ```

**Pro Tip**: For testing, keep your normal user logged in on Chrome and your superuser logged in on Firefox to easily switch between user perspectives.

## Testing & Quality Assurance

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage report
coverage run -m pytest
coverage html
open htmlcov/index.html
```

### Code Quality Checks

```bash
# Type checking with mypy
mypy kquires

# Code formatting and linting with ruff
ruff check .
ruff format .
```

## Background Tasks with Celery

Kquires uses Celery for handling asynchronous tasks and scheduled jobs.

### Starting Celery Worker

```bash
cd kquires
celery -A config.celery_app worker -l info
```

### Running Periodic Tasks

Start the Celery beat scheduler for [periodic tasks](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html):

```bash
# Standalone beat process (recommended for production)
celery -A config.celery_app beat

# Combined worker and beat (development only)
celery -A config.celery_app worker -B -l info
```

**Important**: Ensure you run Celery commands from the same directory as `manage.py` for proper import resolution.

## Email Testing in Development

Kquires includes [Mailpit](https://github.com/axllent/mailpit) for local email testing with a web interface.

### Accessing Mailpit

1. Start the Docker containers:
   ```bash
   docker-compose -f docker-compose.local.yml up
   ```

2. View sent emails at: `http://127.0.0.1:8025`

For more details, see the [cookiecutter-django Docker documentation](https://cookiecutter-django.readthedocs.io/en/latest/2-local-development/developing-locally-docker.html).

## Error Monitoring with Sentry

Kquires integrates with [Sentry](https://sentry.io/signup/?code=cookiecutter) for comprehensive error tracking and performance monitoring.

### Features
- 404 error logging
- WSGI application integration
- Real-time error notifications
- Performance monitoring

**Production Setup**: Configure the Sentry DSN in your production environment variables.

## Deployment

### Docker Deployment (Recommended)

For detailed Docker deployment instructions, see the [cookiecutter-django Docker documentation](https://cookiecutter-django.readthedocs.io/en/latest/3-deployment/deployment-with-docker.html).

#### Production Deployment Steps

1. **Configure environment variables**
   ```bash
   cp .env.production.example .env.production
   # Edit .env.production with your production settings
   ```

2. **Deploy with Docker Compose**
   ```bash
   docker-compose -f docker-compose.production.yml up -d --build
   ```

3. **Run production setup**
   ```bash
   # Apply database migrations
   docker-compose -f docker-compose.production.yml run --rm django python manage.py migrate
   
   # Collect static files
   docker-compose -f docker-compose.production.yml run --rm django python manage.py collectstatic --noinput
   
   # Create superuser
   docker-compose -f docker-compose.production.yml run --rm django python manage.py createsuperuser
   ```

### Manual Deployment

For traditional server deployment, refer to the [Django deployment documentation](https://docs.djangoproject.com/en/stable/howto/deployment/).

## Frontend Development & Theming

### Custom Bootstrap Compilation

Kquires uses a customized Bootstrap 5 setup with automatic recompilation:

- **Custom Variables**: Modify `static/sass/custom_bootstrap_vars` to customize Bootstrap variables
- **Available Variables**: Check the [Bootstrap source](https://github.com/twbs/bootstrap/blob/v5.1.3/scss/_variables.scss) or [Bootstrap docs](https://getbootstrap.com/docs/5.1/customize/sass/)
- **JavaScript Bundle**: Bootstrap JS and dependencies are bundled into `static/js/vendors.js`

### Asset Management

```bash
# Install frontend dependencies
npm install

# Development build with watch
npm run dev

# Production build
npm run build
```

For live reloading and SASS compilation, see [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/2-local-development/developing-locally.html#using-webpack-or-gulp).

## Core Applications

- **Articles**: Knowledge base content management
- **Categories**: Article categorization system
- **Departments**: Organizational structure management
- **Users**: User authentication and profile management
- **Tickets**: Issue tracking and resolution
- **Notifications**: Real-time notification system
- **Logs**: Activity and audit logging
- **Dashboard**: Administrative overview and analytics
- **Message Alerts**: Automated alert system

## Internationalization

Supported languages:
- English (en)
- French (fr_FR)
- Portuguese (pt_BR)
- Arabic (ar)

### Adding New Translations

```bash
# Create translation files
python manage.py makemessages -l <language_code>

# Compile translations
python manage.py compilemessages
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass (`pytest`)
6. Run code quality checks (`ruff check . && mypy kquires`)
7. Commit your changes (`git commit -m 'Add some amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## Documentation

- **API Documentation**: Available at `/api/docs/` when running the server
- **Code Documentation**: Generate with Sphinx in the `docs/` directory
- **Development Guide**: See project documentation for detailed development instructions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Documentation**: Check the `/docs` directory for detailed guides
- **Community**: Join discussions in the project's GitHub Discussions

## Authors

- **Usman** - *Lead Developer* - Initial work and ongoing development

## Acknowledgments

- Built with [Cookiecutter Django](https://github.com/cookiecutter/cookiecutter-django/)
- Bootstrap team for the excellent CSS framework
- Django community for the robust web framework
- All contributors who help improve Kquires
