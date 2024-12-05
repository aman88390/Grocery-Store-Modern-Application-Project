# Grocery-Store-Modern-Application-Project
# Flask E-Commerce Application

This is a Flask-based e-commerce application designed for both managers and users. It allows for managing categories, products, and user carts while maintaining a purchase history.

## Features

### Manager Features
- **Login**: Secure login for managers.
- **Category Management**: Add, edit, and delete categories.
- **Product Management**: Add, edit, and delete products, update stock and pricing.
- **Search Functionality**: Search categories and products by name or price.

### User Features
- **Registration and Login**: User account creation and secure login.
- **Dashboard**: View available categories and products.
- **Cart Management**: Add products to the cart, adjust quantities, and checkout.
- **Search Products**: Search for products by name, price, or category.

## Technologies Used
- **Backend**: Flask (Python)
- **Database**: SQLite (SQLAlchemy for ORM)
- **Frontend**: HTML, CSS (Templates using Flask's Jinja2)
- **Authentication**: Session-based authentication

## Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Grocery-Store-Modern-Application-Project.git
   cd Grocery-Store-Modern-Application-Project
2. Create and activate a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: .\env\Scripts\activate
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
5. Run application:
   ```bash
   python app.py
   

