from flask import Flask, render_template, request, redirect, url_for, g
from peewee import *
from datetime import date

app = Flask(__name__)
db = SqliteDatabase("/Users/ravle/productinventory/inventory.db")

#ORM: Base model
class BaseModel(Model):
    class Meta:
        database = db

#ORM: Category table definition
class Category(BaseModel):
    category_id = AutoField()
    name = CharField()
    class Meta:
        table_name = 'Categories'

#ORM: Supplier table definition
class Supplier(BaseModel):
    supplier_id = AutoField()
    name = CharField()
    contact_info = TextField(null=True)
    class Meta:
        table_name = 'Suppliers'

#ORM: Product table with foreign keys to Category and Supplier
class Product(BaseModel):
    product_id = AutoField()
    name = CharField()
    description = TextField(null=True)
    category = ForeignKeyField(Category, backref='products', null=True)  #ORM: FK relationship
    supplier = ForeignKeyField(Supplier, backref='products', null=True)  #ORM: FK relationship
    quantity = IntegerField(default=0)
    price = FloatField(null=True)
    class Meta:
        table_name = 'Products'

#ORM: Logs changes in product stock
class StockLog(BaseModel):
    log_id = AutoField()
    product = ForeignKeyField(Product, backref='logs')  #ORM: FK to Product
    change = IntegerField()
    reason = TextField()
    date = DateField(default=date.today)
    class Meta:
        table_name = 'StockLogs'

@app.route('/')
def home():
    return redirect(url_for('list_products'))

@app.route('/products')
def list_products():
    #ORM: Select products and join Category and Supplier tables for display
    products = Product.select().join(Category, JOIN.LEFT_OUTER).switch(Product).join(Supplier, JOIN.LEFT_OUTER)
    return render_template('products.html', products=products)

@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])

        new_category = request.form.get('new_category', '').strip()
        new_supplier = request.form.get('new_supplier', '').strip()
        new_supplier_contact = request.form.get('new_supplier_contact', '').strip()
        category_id = request.form.get('category')
        supplier_id = request.form.get('supplier')

        #ORM: Create new category if provided
        if new_category:
            category = Category.create(name=new_category)
            category_id = category.category_id  #ORM: get auto-generated PK
        else:
            category_id = int(category_id)

        #ORM: Create new supplier if provided
        if new_supplier:
            supplier = Supplier.create(name=new_supplier, contact_info=new_supplier_contact)
            supplier_id = supplier.supplier_id
        else:
            supplier_id = int(supplier_id)

        with db.atomic():
            #ORM: Create a new Product entry
            product = Product.create(
                name=name,
                description=description,
                category=category_id,
                supplier=supplier_id,
                quantity=quantity,
                price=price
            )

            #ORM: Insert an initial stock log
            StockLog.create(product=product, change=quantity, reason="Initial Stock")

        return redirect(url_for('list_products'))

    #ORM: Load categories and suppliers to populate dropdowns
    categories = Category.select()
    suppliers = Supplier.select()
    return render_template('add_product.html', categories=categories, suppliers=suppliers)

@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    #ORM: Retrieve the product or return 404
    product = Product.get_or_none(Product.product_id == product_id)
    if not product:
        return "Product not found", 404

    if request.method == 'POST':
        #ORM: Update product fields and save
        product.name = request.form['name']
        product.description = request.form['description']
        product.category = request.form['category']
        product.supplier = request.form['supplier']
        product.quantity = int(request.form['quantity'])
        product.price = float(request.form['price'])
        product.save()  # ORM: persist changes to DB
        return redirect(url_for('list_products'))

    #ORM: Load categories and suppliers to populate dropdowns
    categories = Category.select()
    suppliers = Supplier.select()
    return render_template('edit_product.html', product=product, categories=categories, suppliers=suppliers)

@app.route('/delete/<int:product_id>')
def delete_product(product_id):
    #ORM: Retrieve product and delete it
    product = Product.get_or_none(Product.product_id == product_id)
    if product:
        product.delete_instance(recursive=True)  #ORM: delete product and related logs
    return redirect(url_for('list_products'))


@app.route('/report', methods=['GET', 'POST'])
def report():
    categories = Category.select()
    suppliers = Supplier.select()

    selected_category = []
    selected_supplier = []
    min_price = max_price = None
    products = []
    stats = {'count': 0, 'avg_price': 0, 'total_qty': 0}

    if request.method == 'POST':
        selected_category = request.form.getlist('category')
        selected_supplier = request.form.getlist('supplier')
        min_price = request.form.get('min_price')
        max_price = request.form.get('max_price')

        #Build query
        query = """
        SELECT P.name, C.name AS category, S.name AS supplier, P.price, P.quantity
        FROM Products P
        LEFT JOIN Categories C ON P.category_id = C.category_id
        LEFT JOIN Suppliers S ON P.supplier_id = S.supplier_id
        WHERE 1=1
        """
        params = []

        if selected_category:
            placeholders = ','.join(['?'] * len(selected_category))
            query += f" AND P.category_id IN ({placeholders})"
            params.extend(selected_category)

        if selected_supplier:
            placeholders = ','.join(['?'] * len(selected_supplier))
            query += f" AND P.supplier_id IN ({placeholders})"
            params.extend(selected_supplier)

        if min_price:
            query += " AND P.price >= ?"
            params.append(min_price)

        if max_price:
            query += " AND P.price <= ?"
            params.append(max_price)

        cur = db.execute_sql(query, params)
        cols = [col[0] for col in cur.description]
        products = [dict(zip(cols, row)) for row in cur.fetchall()]

        #Stats query
        stat_query = "SELECT COUNT(*), AVG(price), SUM(quantity) FROM Products WHERE 1=1"
        stat_params = []

        if selected_category:
            placeholders = ','.join(['?'] * len(selected_category))
            stat_query += f" AND category_id IN ({placeholders})"
            stat_params.extend(selected_category)

        if selected_supplier:
            placeholders = ','.join(['?'] * len(selected_supplier))
            stat_query += f" AND supplier_id IN ({placeholders})"
            stat_params.extend(selected_supplier)

        if min_price:
            stat_query += " AND price >= ?"
            stat_params.append(min_price)
        if max_price:
            stat_query += " AND price <= ?"
            stat_params.append(max_price)

        stat_result = db.execute_sql(stat_query, stat_params).fetchone()
        stats = {
            'count': stat_result[0],
            'avg_price': stat_result[1],
            'total_qty': stat_result[2]
        }

    return render_template("report.html",
                           categories=categories,
                           suppliers=suppliers,
                           products=products,
                           stats=stats,
                           selected_category=list(map(int, selected_category)),
                           selected_supplier=list(map(int, selected_supplier)),
                           min_price=min_price,
                           max_price=max_price)



if __name__ == '__main__':
    db.connect()  #ORM: connect to SQLite database
    db.create_tables([Category, Supplier, Product, StockLog], safe=True)  #ORM: create tables if they dont exist
    app.run(debug=True)
