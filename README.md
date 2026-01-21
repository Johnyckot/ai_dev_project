# Quiz App

A real-time, multi-user quiz application built with Django, Django REST Framework, and Channels for WebSocket support.

## Features

- Create and manage quizzes with multiple questions
- Real-time quiz sessions with WebSocket updates
- User registration and authentication
- Leaderboards and scoring
- Responsive frontend with Bootstrap

## Technologies Used

- **Backend**: Django, Django REST Framework
- **Real-time**: Django Channels, Daphne
- **Database**: SQLite (configurable to PostgreSQL)
- **Frontend**: Django Templates, JavaScript, Bootstrap

## Installation

### Prerequisites

- Python 3.10+
- Virtual environment (recommended)

### Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd ai_dev_project
   ```

2. Create and activate virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create superuser (optional):
   ```
   python manage.py createsuperuser
   ```

## Usage

### Development Server

Run the development server:
```
python manage.py runserver
```

For WebSocket support, use Daphne:
```
daphne quiz_app.asgi:application
```

Access the app at http://127.0.0.1:8000/

### Docker

Build and run with Docker Compose:
```
docker-compose up --build
```

## Testing

Run unit and integration tests:
```
python manage.py test
```

Tests cover models, views, and API endpoints.

## API Endpoints

- `/api/quizzes/` - List/create quizzes
- `/api/questions/` - Manage questions
- `/api/quiz-sessions/` - Quiz sessions
- `/api/users/` - User management

## Deployment

### Docker

Use the provided Dockerfile and docker-compose.yml for containerized deployment.

### GitHub Actions

CI/CD pipeline is configured in `.github/workflows/django.yml`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Submit a pull request

## License

This project is licensed under the MIT License.