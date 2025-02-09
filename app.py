from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "ecommerce"

app = FastAPI()

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

class Product(BaseModel):
    name: str
    price: float
    description: str
    category: str
    stock: int

@app.post("/products/")
async def create_product(product: Product):
    product_dict = product.dict()
    result = await db.products.insert_one(product_dict)
    if result.inserted_id:
        return {"message": "Product added successfully", "id": str(result.inserted_id)}
    raise HTTPException(status_code=500, detail="Failed to add product")

@app.get("/products/")
async def get_products():
    products = await db.products.find().to_list(100)
    return [{"id": str(p["_id"]), "name": p["name"], "price": p["price"]} for p in products]

@app.put("/products/{product_id}")
async def update_product(product_id: str, product: Product):
    try:
        obj_id = ObjectId(product_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid product ID")

    result = await db.products.update_one({"_id": obj_id}, {"$set": product.dict()})
    if result.modified_count:
        return {"message": "Product updated successfully"}
    raise HTTPException(status_code=404, detail="Product not found")

@app.delete("/products/{product_id}")
async def delete_product(product_id: str):
    try:
        obj_id = ObjectId(product_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid product ID")

    result = await db.products.delete_one({"_id": obj_id})
    if result.deleted_count:
        return {"message": "Product deleted successfully"}
    raise HTTPException(status_code=404, detail="Product not found")

@app.get("/")
async def root():
    return {"message": "E-commerce API running"}
