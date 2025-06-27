# Coderr Backend API

A Django REST Framework backend for the Coderr freelance platform with comprehensive image upload functionality.

## Features

- **User Management**: Registration, authentication, and profile management
- **Offer System**: Create and manage service offerings with image uploads
- **Order Management**: Handle client orders and project workflow  
- **Review System**: Client feedback and rating system
- **Image Upload**: Profile pictures and offer images with media serving

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Create superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

4. **Run development server**:
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/api/`

## API Endpoints

### Authentication
- `POST /api/registration/` - User registration
- `POST /api/login/` - User login

### Users & Profiles
- `GET /api/profile/` - List user profiles
- `GET/PATCH /api/profile/{id}/` - Retrieve/update user profile (supports image upload)

### Offers
- `GET /api/offers/` - List offers
- `POST /api/offers/` - Create offer (supports image upload, business users only)
- `GET/PUT/DELETE /api/offers/{id}/` - Retrieve/update/delete offer

### Orders
- `GET /api/orders/` - List orders
- `POST /api/orders/` - Create order
- `GET/PUT/DELETE /api/orders/{id}/` - Retrieve/update/delete order

### Reviews
- `GET /api/reviews/` - List reviews
- `POST /api/reviews/` - Create review
- `GET/PUT/DELETE /api/reviews/{id}/` - Retrieve/update/delete review

## Image Upload Examples

### Upload Profile Picture
```bash
curl -X PATCH http://127.0.0.1:8000/api/profile/1/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "file=@profile.jpg" \
  -F "first_name=John"
```

### Create Offer with Image
```bash
curl -X POST http://127.0.0.1:8000/api/offers/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "title=Web Development" \
  -F "description=Professional web development services" \
  -F "image=@offer.jpg" \
  -F 'details=[{"title":"Basic","price":"299.00","revisions":2,"delivery_time_in_days":5,"features":["Responsive Design"],"offer_type":"basic"}]'
```

## Development

### Running Tests
Test files are available locally for development but excluded from the repository:
- `test_image_endpoints.py` - Comprehensive image upload testing
- `system_check.py` - System configuration validation
- `cleanup_test_images.py` - Test file cleanup utility

### Project Structure
```
backend/
├── coderr_backend/          # Django project settings
├── users/                   # User management app
├── offers/                  # Offer management app
├── orders/                  # Order management app
├── reviews/                 # Review system app
├── core/                    # Core functionality app
├── media/                   # User uploaded files
├── requirements.txt         # Python dependencies
└── manage.py               # Django management script
```

## Configuration

### Media Files
- **Development**: Served by Django at `/media/`
- **Production**: Configure nginx/Apache or cloud storage (AWS S3)

### Database
- **Development**: SQLite (default)
- **Production**: Configure PostgreSQL/MySQL in settings

### CORS
Configured for frontend development at `http://127.0.0.1:5500`
