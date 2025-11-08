# # main.py
# from fastapi import FastAPI
# from database import SessionLocal, engine
# from database_models import ProductDB
# from models import ProductSchema
# import database

# app = FastAPI()

# database.Base.metadata.create_all(bind=engine)

# Products = [
#     ProductSchema(id=1, name='phone', description='budget phone', price=99, quantity=10),
#     ProductSchema(id=2, name='laptop', description='gaming laptop', price=999, quantity=6)
# ]

# @app.get("/")
# def greet():
#     return {"message": "hello world"}

# @app.get("/products")
# def get_all_products():
#     return Products

# @app.get("/product/{id}")
# def get_product_by_id(id: int):
#     for product in Products:
#         if product.id == id:
#             return product
#     return {"error": f"not found {id}"}

# @app.post("/product")
# def add_product(product: ProductSchema):
#     Products.append(product)
#     return product

# @app.put("/product/{id}")
# def update_product(id: int, product: ProductSchema):
#     for i in range(len(Products)):
#         if Products[i].id == id:
#             Products[i] = product
#             return {"message": "product updated successfully"}
#     return {"error": "no product found"}

# @app.delete("/product/{id}")
# def delete_product(id: int):
#     for i in range(len(Products)):
#         if Products[i].id == id:
#             del Products[i]
#             return {"message": "product deleted successfully"}
#     return {"error": "no product found"}

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import  engine,get_db
from database_models import ProductDB
from models import ProductSchema
import database

app = FastAPI()

# Create tables
database.Base.metadata.create_all(bind=engine)



@app.get("/")
def greet():
    return {"message": "hello world"}


@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):
    products = db.query(ProductDB).all()
    return products


@app.get("/product/{id}")
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(ProductDB.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {id} not found")
    return product


@app.post("/product")
def add_product(product: ProductSchema, db: Session = Depends(get_db)):
    new_product = ProductDB(
        name=product.name,
        description=product.description,
        price=product.price,
        quantity=product.quantity
    )
    db.add(new_product)
    db.commit()             # ✅ Commit changes
    db.refresh(new_product) # ✅ Refresh to get the new ID
    return new_product


@app.put("/product/{id}")
def update_product(id: int, product: ProductSchema, db: Session = Depends(get_db)):
    existing_product = db.query(ProductDB).filter(ProductDB.id == id).first()
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing_product.name = product.name
    existing_product.description = product.description
    existing_product.price = product.price
    existing_product.quantity = product.quantity

    db.commit()  # ✅ Save updates
    db.refresh(existing_product)
    return {"message": "Product updated successfully", "product": existing_product}


@app.delete("/product/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(ProductDB.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()  # ✅ Commit deletion
    return {"message": "Product deleted successfully"}

