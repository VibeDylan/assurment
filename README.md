# Assur'aimant - Insurance Premium Prediction Platform

A Django-based web application for predicting insurance premiums using machine learning. The platform allows users to get insurance premium estimates and enables advisors to manage client predictions and appointments.

## 🚀 Features

### For Users
- **User Authentication**: Sign up, login, and profile management
- **Premium Prediction**: Get AI-powered insurance premium estimates based on personal information (age, BMI, smoking status, region, etc.)
- **Prediction History**: View all your past predictions with pagination support
- **Appointment Booking**: Book appointments with insurance advisors
- **Appointment Management**: View upcoming and past appointments

### For Advisors (Conseillers)
- **Dashboard**: Overview of appointments and statistics
- **Client Management**: View and manage client list
- **Predictions for Clients**: Make predictions on behalf of clients
- **Calendar View**: Visual calendar to manage appointments
- **Availability Management**: Set and manage available time slots

### For Administrators
- Full access to all features and user management

## 🛠️ Technologies Used

- **Backend**: Django 6.0.1
- **Database**: PostgreSQL 15
- **Machine Learning**: scikit-learn, pandas, numpy, joblib
- **Containerization**: Docker & Docker Compose
- **Frontend**: HTML, CSS (Tailwind CSS), JavaScript
- **Testing**: pytest, pytest-django, factory-boy, coverage, model-bakery

## 📋 Prerequisites

- Python 3.12+
- Docker and Docker Compose (recommended)
- PostgreSQL 15 (if not using Docker)

## 🔧 Installation

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd assurment
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and configure:
   - `SECRET_KEY`: Django secret key
   - `DEBUG`: Set to `True` for development
   - Database credentials (if not using Docker defaults)

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

The application will be available at `http://localhost:8000`

### Manual Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd assurment
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**
   - Create a PostgreSQL database named `assurment`
   - Update database credentials in `.env` file

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Update `.env` with your database credentials:
   ```
   DB_NAME=assurment
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

The application will be available at `http://localhost:8000`

## 📁 Project Structure

```
assurement/
├── assurment/              # Django project settings
│   ├── settings.py        # Main settings file
│   ├── urls.py            # Root URL configuration
│   └── wsgi.py            # WSGI configuration
├── insurance_web/          # Main application
│   ├── models.py          # Database models (Profile, Appointment, Prediction)
│   ├── views/             # View functions
│   │   ├── user_views.py  # User-facing views
│   │   └── conseiller_views.py  # Advisor views
│   ├── forms.py           # Django forms
│   ├── urls.py            # Application URLs
│   ├── prediction_service.py  # ML prediction service
│   └── utils/              # Utility functions
│       ├── decorators.py  # Custom decorators
│       └── mixins.py      # Mixins
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   ├── authentification/  # Auth templates
│   ├── conseiller/        # Advisor templates
│   └── ...
├── model/                 # ML model files
│   └── gb_pipeline.joblib # Trained model
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile             # Docker image definition
├── requirements.txt       # Python dependencies
└── manage.py             # Django management script
```

## 🎯 Usage

### Creating User Accounts

1. Navigate to the signup page: `/signup/`
2. Fill in the registration form
3. You'll be automatically logged in after registration

### Making Predictions

1. **As a regular user:**
   - Login and navigate to `/predict/`
   - Fill in your information (age, BMI, smoking status, etc.)
   - Get your premium estimate
   - View prediction history on your profile page

2. **As an advisor:**
   - Login with an advisor account
   - Navigate to `/conseiller/predict/`
   - Select a client or enter client information
   - Make predictions on behalf of clients

### Booking Appointments

1. Navigate to `/conseillers/` to see available advisors
2. Click on an advisor to view their availability
3. Select a date and available time slot
4. Confirm the appointment
5. View your appointments at `/appointments/`

### Managing Appointments (Advisors)

1. Login as an advisor
2. Navigate to `/conseiller/calendar/` for calendar view
3. Navigate to `/conseiller/clients/` to manage clients
4. Use the dashboard at `/conseiller/` for an overview

## 🔐 User Roles

- **User**: Default role for regular users
- **Conseiller (Advisor)**: Can make predictions for clients and manage appointments
- **Admin**: Full administrative access

To change a user's role, use the Django admin panel or update the `Profile` model directly.

## 🤖 Machine Learning Model

The application uses a Gradient Boosting model (`gb_pipeline.joblib`) trained on insurance data. The model predicts insurance premiums based on:
- Age
- Gender (Sex)
- BMI (Body Mass Index)
- Number of children
- Smoking status
- Region

The model is loaded once at startup and reused for all predictions to ensure optimal performance.

## 📊 Database Models

### Profile
- Extends Django's User model
- Stores user demographic information
- Manages user roles (user, conseiller, admin)

### Prediction
- Stores all predictions made by users or advisors
- Tracks who created the prediction (`created_by`)
- Stores all input parameters and predicted amount
- Includes timestamp for history tracking

### Appointment
- Links advisors (conseillers) with clients
- Stores appointment date, time, and duration
- Includes optional notes

## 🧪 Development

### Running Tests

The project uses `pytest` for testing. Install test dependencies:

```bash
pip install -r requirements.txt
```

#### Using pytest (Recommended)
```bash
# Run all tests
pytest

# Run specific test file
pytest insurance_web/tests/test_models.py

# Run with coverage report
coverage run -m pytest
coverage report
coverage html  # Generate HTML report

# Run with verbosity
pytest -v

# Run specific test
pytest insurance_web/tests/test_models.py::test_profile_creation
```

#### Using Django test runner
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test insurance_web

# Run with verbosity
python manage.py test --verbosity=2
```

#### Test Coverage
```bash
# Generate coverage report
coverage run --source='.' manage.py test
coverage report
coverage html  # Open htmlcov/index.html in browser
```

### Testing Tools

The project includes the following testing tools:
- **pytest**: Modern testing framework
- **pytest-django**: Django integration for pytest
- **factory-boy**: Easy test data generation
- **coverage**: Code coverage measurement
- **model-bakery**: Alternative test data factory

See `TESTING_GUIDE.md` for comprehensive testing documentation.

### Creating Migrations
```bash
python manage.py makemigrations
```

### Applying Migrations
```bash
python manage.py migrate
```

### Accessing Django Admin
1. Create a superuser: `python manage.py createsuperuser`
2. Navigate to `/admin/`
3. Login with superuser credentials

## 🐳 Docker Commands

```bash
# Build and start containers
docker-compose up --build

# Start in background
docker-compose up -d

# Stop containers
docker-compose down

# View logs
docker-compose logs -f web

# Run commands in container
docker-compose exec web python manage.py <command>

# Access database
docker-compose exec db psql -U postgres -d assurment
```

## 🔒 Security Notes

- **Never commit `.env` file** - It contains sensitive information
- Change `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Use strong database passwords
- Configure `ALLOWED_HOSTS` in production settings

## 📝 Environment Variables

Create a `.env` file with the following variables:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=assurment
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## 🐛 Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check database credentials in `.env`
- Verify database exists: `docker-compose exec db psql -U postgres -l`

### Migration Issues
- Reset migrations: `python manage.py migrate --run-syncdb`
- Check for migration conflicts

### Model Loading Issues
- Ensure `model/gb_pipeline.joblib` exists
- Check file permissions


**Note**: This is a study project. For study case only.
