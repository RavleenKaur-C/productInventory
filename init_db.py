import sqlite3

#create or connect to db
conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()

#drop lowercase tables
cursor.execute("DROP TABLE IF EXISTS supplier")
cursor.execute("DROP TABLE IF EXISTS category")
cursor.execute("DROP TABLE IF EXISTS product")
cursor.execute("DROP TABLE IF EXISTS stocklog")

#drop tables
cursor.execute("DROP TABLE IF EXISTS StockLogs")
cursor.execute("DROP TABLE IF EXISTS Products")
cursor.execute("DROP TABLE IF EXISTS Categories")
cursor.execute("DROP TABLE IF EXISTS Suppliers")

#cased tables
cursor.execute("""
CREATE TABLE Categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);
""")

cursor.execute("""
CREATE TABLE Suppliers (
    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact_info TEXT
);
""")

cursor.execute("""
CREATE TABLE Products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    category_id INTEGER,
    supplier_id INTEGER,
    quantity INTEGER NOT NULL DEFAULT 0,
    price REAL,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id),
    FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id)
);
""")

cursor.execute("""
CREATE TABLE StockLogs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    change INTEGER,
    reason TEXT,
    date TEXT DEFAULT CURRENT_DATE,
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);
""")

#dummy data
categories = [
    ("Electronics",),
    ("Stationery",),
    ("Groceries",),
    ("Clothing",),
    ("Toys",),
    ("Books",),
    ("Furniture",),
    ("Sports",),
    ("Beauty",),
    ("Automotive",)
]
cursor.executemany("INSERT INTO Categories (name) VALUES (?)", categories)

#dummy data
suppliers = [
    ("Acme Inc.", "acme@example.com"),
    ("PaperWorld", "paper@example.com"),
    ("GroceryCo", "groceries@example.com"),
    ("FashionHub", "fashion@example.com"),
    ("ToyLand", "toys@example.com"),
    ("ReadMore", "books@example.com"),
    ("FurnishIt", "furnish@example.com"),
    ("FitLife", "sports@example.com"),
    ("GlowUp", "beauty@example.com"),
    ("AutoGear", "auto@example.com")
]
cursor.executemany("INSERT INTO Suppliers (name, contact_info) VALUES (?, ?)", suppliers)

#dummy data
products = [
    ("USB Cable", "Type-C to USB", 1, 1, 50, 9.99),
    ("Notebook", "200 pages ruled", 2, 2, 120, 3.49),
    ("Rice Bag", "5kg long grain rice", 3, 3, 25, 12.00),
    ("T-Shirt", "Cotton, Medium size", 4, 4, 40, 15.99),
    ("Teddy Bear", "Soft plush toy", 5, 5, 30, 18.50),
    ("Science Book", "High school level", 6, 6, 60, 8.75),
    ("Office Chair", "Ergonomic with wheels", 7, 7, 10, 89.99),
    ("Yoga Mat", "Non-slip surface", 8, 8, 35, 19.95),
    ("Face Cream", "Moisturizing cream", 9, 9, 80, 14.30),
    ("Car Wiper", "Universal fit", 10, 10, 20, 11.49)
]
cursor.executemany("""
INSERT INTO Products (name, description, category_id, supplier_id, quantity, price)
VALUES (?, ?, ?, ?, ?, ?)""", products)

#dummy data
stock_logs = [
    (1, 20, "Restock"),
    (2, -10, "Sold"),
    (3, -5, "Damaged"),
    (4, 15, "Restock"),
    (5, -3, "Sold"),
    (6, 25, "Initial Stock"),
    (7, -2, "Sample Unit"),
    (8, 10, "Restock"),
    (9, -5, "Returned"),
    (10, 5, "Restock")
]
cursor.executemany("""
INSERT INTO StockLogs (product_id, change, reason) VALUES (?, ?, ?)""", stock_logs)

#Adding indexes to support querying in the report function
cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_products_category_supplier
ON Products(category_id, supplier_id);
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_products_price
ON Products(price);
""")

#commit and close
conn.commit()
conn.close()

print("intialized")