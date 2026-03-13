from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

products = [
    {"id": 1, "name": "Wireless Mouse",      "price": 499,  "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook",            "price": 99,   "category": "Stationery",  "in_stock": True},
    {"id": 3, "name": "USB Hub",             "price": 799,  "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set",             "price": 49,   "category": "Stationery",  "in_stock": True},
    {"id": 5, "name": "Laptop Stand",        "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam",              "price": 1899, "category": "Electronics", "in_stock": False},
]

orders   = []
feedback = []

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PYDANTIC MODELS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CustomerFeedback(BaseModel):
    customer_name: str           = Field(..., min_length=2, max_length=100)
    product_id:    int           = Field(..., gt=0)
    rating:        int           = Field(..., ge=1, le=5)
    comment:       Optional[str] = Field(None, max_length=300)

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity:   int = Field(..., gt=0, le=50)

class BulkOrder(BaseModel):
    company_name:  str             = Field(..., min_length=2)
    contact_email: str             = Field(..., min_length=5)
    items:         List[OrderItem] = Field(..., min_length=1)

# ── Day 4 new model ──
class NewProduct(BaseModel):
    name:      str  = Field(..., min_length=1)
    price:     int  = Field(..., gt=0)
    category:  str  = Field(..., min_length=1)
    in_stock:  bool = Field(True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def find_product(product_id: int):
    return next((p for p in products if p["id"] == product_id), None)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HOME
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/")
def home():
    return {"message": "Welcome to our E-commerce API!"}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PRODUCT ENDPOINTS  (fixed routes FIRST, then /{product_id})
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/products")
def get_all_products():
    return {"products": products, "total": len(products)}


# Day 2 – Q1: filter with min_price
@app.get("/products/filter")
def filter_products(
    category:  str  = Query(None, description="Electronics or Stationery"),
    max_price: int  = Query(None, description="Maximum price"),
    min_price: int  = Query(None, description="Minimum price"),
    in_stock:  bool = Query(None, description="True = in stock only")
):
    result = products
    if category:
        result = [p for p in result if p["category"] == category]
    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]
    if min_price is not None:
        result = [p for p in result if p["price"] >= min_price]
    if in_stock is not None:
        result = [p for p in result if p["in_stock"] == in_stock]
    return {"filtered_products": result, "count": len(result)}


@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):
    result = [p for p in products if p["category"] == category_name]
    if not result:
        return {"error": "No products found in this category"}
    return {"category": category_name, "products": result, "total": len(result)}


@app.get("/products/instock")
def get_instock():
    available = [p for p in products if p["in_stock"]]
    return {"in_stock_products": available, "count": len(available)}


# Day 2 – Q4: product summary dashboard
@app.get("/products/summary")
def product_summary():
    in_stock   = [p for p in products if p["in_stock"]]
    out_stock  = [p for p in products if not p["in_stock"]]
    expensive  = max(products, key=lambda p: p["price"])
    cheapest   = min(products, key=lambda p: p["price"])
    categories = list(set(p["category"] for p in products))
    return {
        "total_products":     len(products),
        "in_stock_count":     len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive": {"name": expensive["name"], "price": expensive["price"]},
        "cheapest":       {"name": cheapest["name"],  "price": cheapest["price"]},
        "categories":     categories,
    }


@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    results = [p for p in products if keyword.lower() in p["name"].lower()]
    if not results:
        return {"message": "No products matched your search"}
    return {"keyword": keyword, "results": results, "total_matches": len(results)}


# ✅ Day 4 – Q5: Audit endpoint  ← MUST be above /{product_id}
@app.get("/products/audit")
def product_audit():
    in_stock_list  = [p for p in products if p["in_stock"]]
    out_stock_list = [p for p in products if not p["in_stock"]]
    stock_value    = sum(p["price"] * 10 for p in in_stock_list)
    priciest       = max(products, key=lambda p: p["price"])
    return {
        "total_products":    len(products),
        "in_stock_count":    len(in_stock_list),
        "out_of_stock_names": [p["name"] for p in out_stock_list],
        "total_stock_value": stock_value,
        "most_expensive":    {"name": priciest["name"], "price": priciest["price"]},
    }


# ✅ Day 4 – Bonus: bulk category discount  ← MUST be above /{product_id}
@app.put("/products/discount")
def bulk_discount(
    category:         str = Query(..., description="Category to discount"),
    discount_percent: int = Query(..., ge=1, le=99, description="% off"),
):
    updated = []
    for p in products:
        if p["category"] == category:
            p["price"] = int(p["price"] * (1 - discount_percent / 100))
            updated.append(p)
    if not updated:
        return {"message": f"No products found in category: {category}"}
    return {
        "message":          f"{discount_percent}% discount applied to {category}",
        "updated_count":    len(updated),
        "updated_products": updated,
    }


# Day 2 – Q2: price-only endpoint  ← MUST be above /{product_id}
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    product = find_product(product_id)
    if not product:
        return {"error": "Product not found"}
    return {"name": product["name"], "price": product["price"]}


# GET single product
@app.get("/products/{product_id}")
def get_product(product_id: int):
    product = find_product(product_id)
    if not product:
        return {"error": "Product not found"}
    return {"product": product}


# ✅ Day 4 – Q1: POST – add a new product
@app.post("/products", status_code=201)
def add_product(data: NewProduct, response: Response):
    # duplicate name check
    for p in products:
        if p["name"].lower() == data.name.lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": f"Product '{data.name}' already exists"}

    next_id = max(p["id"] for p in products) + 1
    new_product = {
        "id":       next_id,
        "name":     data.name,
        "price":    data.price,
        "category": data.category,
        "in_stock": data.in_stock,
    }
    products.append(new_product)
    return {"message": "Product added", "product": new_product}


# ✅ Day 4 – Q2: PUT – update price / in_stock
@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    response:   Response,
    price:      int  = Query(None, description="New price"),
    in_stock:   bool = Query(None, description="Stock status"),
):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    if price is not None:
        product["price"] = price
    if in_stock is not None:
        product["in_stock"] = in_stock

    return {"message": "Product updated", "product": product}


# ✅ Day 4 – Q3: DELETE – remove a product
@app.delete("/products/{product_id}")
def delete_product(product_id: int, response: Response):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}
    products.remove(product)
    return {"message": f"Product '{product['name']}' deleted"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STORE & DEALS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/store/summary")
def store_summary():
    in_stock_count  = len([p for p in products if p["in_stock"]])
    out_stock_count = len(products) - in_stock_count
    categories      = list(set(p["category"] for p in products))
    return {
        "store_name":     "My E-commerce Store",
        "total_products": len(products),
        "in_stock":       in_stock_count,
        "out_of_stock":   out_stock_count,
        "categories":     categories,
    }


@app.get("/products/deals")
def get_deals():
    cheapest  = min(products, key=lambda p: p["price"])
    expensive = max(products, key=lambda p: p["price"])
    return {"best_deal": cheapest, "premium_pick": expensive}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FEEDBACK & ORDERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback.append(data.dict())
    return {
        "message":        "Feedback submitted successfully",
        "feedback":       data.dict(),
        "total_feedback": len(feedback),
    }


@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed, failed, grand_total = [], [], 0
    for item in order.items:
        product = find_product(item.product_id)
        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
        elif not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
        else:
            subtotal     = product["price"] * item.quantity
            grand_total += subtotal
            confirmed.append({"product": product["name"], "qty": item.quantity, "subtotal": subtotal})
    return {"company": order.company_name, "confirmed": confirmed, "failed": failed, "grand_total": grand_total}


@app.post("/orders")
def place_order(order: BulkOrder):
    order_id  = len(orders) + 1
    new_order = {
        "order_id": order_id,
        "company":  order.company_name,
        "email":    order.contact_email,
        "items":    [item.dict() for item in order.items],
        "status":   "pending",
    }
    orders.append(new_order)
    return {"message": "Order placed", "order": new_order}


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    for order in orders:
        if order["order_id"] == order_id:
            return {"order": order}
    return {"error": "Order not found"}


@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "confirmed"
            return {"message": "Order confirmed", "order": order}
    return {"error": "Order not found"}