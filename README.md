# PRODIGY_FS_03 — Django E-Commerce Store

A full-featured e-commerce web application built with **Django**, featuring product browsing, shopping cart, order management, user authentication, product reviews, and a staff admin dashboard.

---

## Features

### 🛍️ Product Catalog
- Browse products with category filtering, keyword search, and price range filtering
- Sort by name, price (low → high / high → low), or newest
- Paginated product listing (12 per page)
- Detailed product pages with stock availability

### 🛒 Shopping Cart
- Add, update, and remove items
- Real-time stock validation (cannot add more than available stock)
- Cart persists per user session

### 📦 Orders
- Checkout with shipping details (name, email, address, city, postal code)
- Stock is automatically reduced on order placement
- Order confirmation page after successful purchase
- View personal order history (`My Orders`)
- Order statuses: **Pending → Processing → Shipped → Delivered → Cancelled**

### ⭐ Product Reviews
- Authenticated users can leave a star rating (1–5) and a comment
- One review per user per product (enforced at the database level)

### 🔐 Authentication
- User registration and login/logout
- Login required for cart, checkout, and reviews
- Staff-only admin panel

### 🖥️ Staff Admin Dashboard
- Overview: total orders, pending orders, total products
- Low-stock product alerts (stock < 10)
- Recent orders list
- Update order status
- Add products and update stock levels

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.2+ |
| Database | SQLite (default) |
| Image Handling | Pillow |
| Forms | django-crispy-forms + crispy-bootstrap5 |
| Frontend | Bootstrap 5 (via crispy forms) |

---

## Project Structure

```
ecommerce/
├── ecommerce/          # Django project config (settings, root URLs)
├── store/              # Main application
│   ├── models.py       # Category, Product, Cart, Order, Review
│   ├── views.py        # All view logic
│   ├── urls.py         # URL routing (app_name = 'store')
│   ├── forms.py        # Registration, Login, Review, Order, Product forms
│   ├── admin.py        # Django admin registration
│   ├── context_processors.py
│   └── templates/store/
├── static/             # Static assets (CSS, JS, images)
├── media/              # Uploaded product & category images
├── manage.py
└── requirements.txt
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone <repo-url>
cd ecommerce

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. Create a superuser (for the admin dashboard)
python manage.py createsuperuser

# 6. Run the development server
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## URL Reference

| URL | View | Access |
|---|---|---|
| `/` | Home / featured products | Public |
| `/products/` | Product listing with filters | Public |
| `/product/<slug>/` | Product detail + reviews | Public |
| `/register/` | User registration | Public |
| `/login/` | User login | Public |
| `/logout/` | Logout | Authenticated |
| `/cart/` | Shopping cart | Authenticated |
| `/checkout/` | Checkout form | Authenticated |
| `/my-orders/` | Order history | Authenticated |
| `/admin-dashboard/` | Staff dashboard | Staff only |
| `/admin-products/` | Manage products & stock | Staff only |
| `/admin-orders/` | Manage order statuses | Staff only |

---

## Data Models

```
Category  ──< Product ──< CartItem >── Cart ──< User
                  │
                  └──< OrderItem >── Order ──< User
                  │
                  └──< Review ──< User
```

---

## Environment & Configuration

Copy any environment-specific settings to `local_settings.py` (excluded from git). For production, set:

```python
DEBUG = False
SECRET_KEY = '<strong-random-key>'
ALLOWED_HOSTS = ['yourdomain.com']
```

---

## License

This project was built as part of the pre internship project at Tila health and Insurance 
