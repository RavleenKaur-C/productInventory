# 🗃 Inventory Management System

A **Flask + SQLite** web application for managing products, categories, suppliers, and stock logs.  
Supports adding, editing, deleting products, and generating dynamic reports with filters.

---

## 📌 Features

- **Product Management**
  - Add, update, and delete products
  - Automatically log stock changes

- **Category & Supplier Management**
  - Dynamic dropdowns populated from the database
  - Add new categories or suppliers while adding a product

- **Reporting**
  - Filter by category, supplier, and price range
  - View summary statistics (total products, average price, total quantity)

- **Database Access Methods**
  - **80% ORM (Peewee)** for CRUD operations
  - **20% Prepared Statements** for complex reports

- **Transactions & Concurrency**
  - Uses `db.atomic()` for grouped operations
  - Supports isolation level discussion for multi-user scenarios

---

## 🛠 Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite (Peewee ORM)
- **Frontend:** HTML + CSS (Jinja2 templates)
- **Deployment:** Local

---

## 📂 Project Structure

inventory-app/
│
├── app.py               # Main Flask app and routes
├── models.py            # ORM models and DB utility functions
├── init_db.py           # Script to initialize DB with sample data
├── templates/
│   ├── layout.html       # Base HTML layout
│   ├── products.html     # Product listing page
│   ├── add_product.html  # Add product form
│   ├── edit_product.html # Edit product form
│   └── report.html       # Report generation page
└── README.md             # Project documentation

---

## 🚀 Setup & Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/inventory-app.git
cd inventory-app

python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

pip install flask peewee

python init_db.py

python app.py

http://127.0.0.1:5000
```


