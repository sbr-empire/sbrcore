# ============================================================================
# SQLAlchemy ORM Models
# Core data models for all SBR products
# ============================================================================

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

BaseModel = declarative_base()

class User(BaseModel):
    """
    User model - Core user information
    """
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    phone = Column(String)
    
    # Profile Information
    profile_picture = Column(String)  # URL
    bio = Column(Text)
    location = Column(String)
    
    # Account Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_vendor = Column(Boolean, default=False)
    
    # Roles (comma-separated)
    roles = Column(String, default='user')
    
    # OAuth
    google_id = Column(String, unique=True, nullable=True)
    github_id = Column(String, unique=True, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    orders = relationship('Order', back_populates='user', cascade='all, delete-orphan')
    products = relationship('Product', back_populates='seller', cascade='all, delete-orphan')
    addresses = relationship('Address', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<User {self.email}>"

class Address(BaseModel):
    """
    User address information
    """
    __tablename__ = 'addresses'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    
    address_line1 = Column(String, nullable=False)
    address_line2 = Column(String)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    country = Column(String, nullable=False)
    
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship('User', back_populates='addresses')
    
    def __repr__(self):
        return f"<Address {self.city}, {self.country}>"

class Product(BaseModel):
    """
    Product model - E-commerce products
    """
    __tablename__ = 'products'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic Information
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    sku = Column(String, unique=True, nullable=False, index=True)
    
    # Seller Information
    seller_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    subcategory = Column(String)
    
    # Pricing
    price = Column(Float, nullable=False)
    cost_price = Column(Float)  # Cost to vendor
    discount_percent = Column(Float, default=0)
    
    # Inventory
    quantity = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=10)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False)
    rating = Column(Float, default=0)  # Average rating
    review_count = Column(Integer, default=0)
    
    # Images
    main_image = Column(String)  # URL
    images = Column(String)  # JSON array of URLs
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    seller = relationship('User', back_populates='products')
    order_items = relationship('OrderItem', back_populates='product')
    
    def __repr__(self):
        return f"<Product {self.name}>"

class Order(BaseModel):
    """
    Order model - E-commerce orders
    """
    __tablename__ = 'orders'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Customer Information
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    order_number = Column(String, unique=True, nullable=False, index=True)
    
    # Order Status
    class OrderStatus(str, enum.Enum):
        PENDING = 'pending'
        CONFIRMED = 'confirmed'
        SHIPPED = 'shipped'
        DELIVERED = 'delivered'
        CANCELLED = 'cancelled'
        REFUNDED = 'refunded'
    
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, index=True)
    
    # Pricing
    subtotal = Column(Float, nullable=False)
    tax = Column(Float, default=0)
    shipping_cost = Column(Float, default=0)
    discount = Column(Float, default=0)
    total = Column(Float, nullable=False)
    
    # Payment
    payment_method = Column(String)  # credit_card, paypal, etc.
    payment_id = Column(String, nullable=True, index=True)
    
    # Shipping
    shipping_address = Column(Text)  # JSON
    tracking_number = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship('User', back_populates='orders')
    items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
    payment = relationship('Payment', back_populates='order', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Order {self.order_number}>"

class OrderItem(BaseModel):
    """
    Individual items in an order
    """
    __tablename__ = 'order_items'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    order_id = Column(String, ForeignKey('orders.id'), nullable=False, index=True)
    product_id = Column(String, ForeignKey('products.id'), nullable=False, index=True)
    
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Relationships
    order = relationship('Order', back_populates='items')
    product = relationship('Product', back_populates='order_items')
    
    def __repr__(self):
        return f"<OrderItem {self.product_id}>"

class Payment(BaseModel):
    """
    Payment information
    """
    __tablename__ = 'payments'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    order_id = Column(String, ForeignKey('orders.id'), nullable=False, index=True, unique=True)
    
    class PaymentStatus(str, enum.Enum):
        PENDING = 'pending'
        PROCESSING = 'processing'
        SUCCESS = 'success'
        FAILED = 'failed'
        REFUNDED = 'refunded'
    
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, index=True)
    
    amount = Column(Float, nullable=False)
    currency = Column(String, default='USD')
    
    # Payment Gateway
    gateway = Column(String)  # stripe, paypal, razorpay, etc.
    transaction_id = Column(String, nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationship
    order = relationship('Order', back_populates='payment')
    
    def __repr__(self):
        return f"<Payment {self.transaction_id}>"
