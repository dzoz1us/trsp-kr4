# seed.py
from app.database import SessionLocal
from app.models import Product

db = SessionLocal()

product1 = Product(title="Laptop", price=1500, count=10)
product2 = Product(title="Mouse", price=50, count=100)

db.add_all([product1, product2])
db.commit()
db.close()
print("Database seeded!")