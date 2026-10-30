
# 🏙️ Local Service Finder System

<p align="center">
  <b>A Web-Based Platform for Finding and Booking Local Services</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python" />
  <img src="https://img.shields.io/badge/Django-6.0.3-green?logo=django" />
  <img src="https://img.shields.io/badge/DRF-REST%20API-red" />
  <img src="https://img.shields.io/badge/Status-Development-orange" />
</p>

---

## 📌 About The Project

**Local Service Finder System** is a Django-based web application that connects customers with local service providers. It provides a structured platform for managing services, bookings, user accounts, payments, reviews, and service locations.

The project aims to make finding and accessing local services easier, faster, and more convenient.

## ✨ Key Modules

| Module | Description |
|---|---|
| 👤 Accounts | User account and authentication management |
| 📝 Profiles | User profile management |
| 🛠️ Services | Service-related management |
| 📂 Categories | Service categorization |
| 📍 Locations | Location-based service organization |
| 📅 Booking | Service booking management |
| 💳 Payments | Payment processing integration |
| ⭐ Reviews | Customer feedback and reviews |
| 📊 Dashboard | Centralized dashboard management |

## 🛠️ Technology Stack

### Backend
- Python
- Django 6.0.3
- Django REST Framework

### Authentication & Security
- JWT Authentication
- djangorestframework-simplejwt

### API Documentation
- drf-yasg (Swagger API Documentation)

### Payment Integration
- SSLCommerz

### Other Libraries
- Pillow
- Python Decouple
- Requests

## 📂 Project Structure

```text
Local-Service-Finder-System/
│
├── accounts/
├── booking/
├── categories/
├── dashboard/
├── locations/
├── payments/
├── profiles/
├── reviews/
├── service/
├── src/
│
├── how/
├── manage.py
├── requirements.txt
└── README.md
```

## ⚙️ Installation & Setup

Follow these steps to run the project locally.

### 1. Clone the Repository

```bash
git clone https://github.com/Salim-raza/Local-Service-Finder-System.git
```

### 2. Navigate to the Project Directory

```bash
cd Local-Service-Finder-System
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Environment Variables

Configure the required environment variables and credentials according to the project's Django settings.

> ⚠️ Never commit secret keys, database passwords, or payment gateway credentials to GitHub.

### 7. Apply Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Create Superuser

```bash
python manage.py createsuperuser
```

### 9. Run Development Server

```bash
python manage.py runserver
```

Open your browser and visit:

```text
http://127.0.0.1:8000/
```

## 📖 API Documentation

The project includes `drf-yasg` for API documentation.

If Swagger is configured in the Django URL configuration, access the Swagger documentation at:

```text
http://127.0.0.1:8000/swagger/
```

## 🔐 Security

- Keep sensitive credentials in environment variables.
- Never expose secret keys or payment gateway credentials.
- Use secure authentication practices.
- Configure production security settings before deployment.

## 🚀 Future Improvements

- Enhanced service search and filtering.
- Improved location-based service discovery.
- Real-time booking notifications.
- Advanced service provider management.
- Improved analytics and reporting.

## 👨‍💻 Author

**Salim Raza**

- GitHub: [@Salim-raza](https://github.com/Salim-raza)

## 📄 License

This project is available for educational and development purposes. Add an appropriate open-source license if you intend to distribute it publicly.

---

<p align="center">
  ⭐ If you find this project useful, consider giving it a star!
</p>
