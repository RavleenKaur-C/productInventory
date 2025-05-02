from peewee import *

#connect to the DB
db = SqliteDatabase("inventory.db")

class BaseModel(Model):
    class Meta:
        database = db

class Category(BaseModel):
    category_id = AutoField()
    name = CharField()

class Supplier(BaseModel):
    supplier_id = AutoField()
    name = CharField()
    contact_info = TextField(null=True)

class Product(BaseModel):
    product_id = AutoField()
    name = CharField()
    description = TextField(null=True)
    category = ForeignKeyField(Category, backref='products', null=True)
    supplier = ForeignKeyField(Supplier, backref='products', null=True)
    quantity = IntegerField(default=0)
    price = FloatField(null=True)

class StockLog(BaseModel):
    log_id = AutoField()
    product = ForeignKeyField(Product, backref='logs')
    change = IntegerField()
    reason = TextField()
    date = DateField(constraints=[SQL('DEFAULT CURRENT_DATE')])

#incase tables need to be created
def initialize_db():
    db.connect()
    db.create_tables([Category, Supplier, Product, StockLog], safe=True)
    db.close()


def add_product(name, description, category_id, supplier_id, quantity, price):
    db.connect()
    product = Product.create(
        name=name,
        description=description,
        category=category_id,
        supplier=supplier_id,
        quantity=quantity,
        price=price
    )
    StockLog.create(product=product, change=quantity, reason="Initial Stock")
    db.close()
    return product

def update_product(product_id, **kwargs):
    db.connect()
    product = Product.get_or_none(Product.product_id == product_id)
    if product:
        for key, value in kwargs.items():
            if hasattr(product, key):
                setattr(product, key, value)
        product.save()
    db.close()
    return product

def delete_product(product_id):
    db.connect()
    product = Product.get_or_none(Product.product_id == product_id)
    if product:
        StockLog.create(product=product, change=-product.quantity, reason="Deleted")
        product.delete_instance()
        db.close()
        return True
    db.close()
    return False

def list_products():
    db.connect()
    products = list(Product.select())
    db.close()
    return products

if __name__ == "__main__":
    initialize_db()
    all_products = list_products()
    for p in all_products:
        print(f"{p.product_id}: {p.name} (Qty: {p.quantity})")