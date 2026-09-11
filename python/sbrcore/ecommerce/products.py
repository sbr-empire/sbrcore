# ============================================================================
# Product Management Service
# CRUD operations for products
# ============================================================================

from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from ..database.models import Product, User
from ..logging import get_logger
from datetime import datetime

logger = get_logger(__name__)

class ProductService:
    """
    Manages product operations
    """
    
    @staticmethod
    def create_product(
        session: Session,
        seller_id: str,
        name: str,
        description: str,
        sku: str,
        price: float,
        category: str,
        quantity: int = 0,
        main_image: Optional[str] = None,
        **kwargs
    ) -> Product:
        """
        Create new product
        
        Args:
            session: Database session
            seller_id: Seller/vendor ID
            name: Product name
            description: Product description
            sku: Stock keeping unit (unique identifier)
            price: Product price
            category: Product category
            quantity: Initial stock quantity
            main_image: Main product image URL
        
        Returns:
            Created Product object
        """
        product = Product(
            seller_id=seller_id,
            name=name,
            description=description,
            sku=sku,
            price=price,
            category=category,
            quantity=quantity,
            main_image=main_image,
            **kwargs
        )
        
        session.add(product)
        session.commit()
        session.refresh(product)
        
        logger.info(f"Product created: {name} (SKU: {sku})")
        return product
    
    @staticmethod
    def get_product(session: Session, product_id: str) -> Optional[Product]:
        """
        Get product by ID
        """
        return session.query(Product).filter(Product.id == product_id).first()
    
    @staticmethod
    def get_products_by_seller(
        session: Session,
        seller_id: str,
        active_only: bool = True
    ) -> List[Product]:
        """
        Get all products for a seller
        """
        query = session.query(Product).filter(Product.seller_id == seller_id)
        if active_only:
            query = query.filter(Product.is_active == True)
        return query.all()
    
    @staticmethod
    def search_products(
        session: Session,
        keyword: str,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        active_only: bool = True
    ) -> List[Product]:
        """
        Search products by keyword and filters
        """
        query = session.query(Product)
        
        if active_only:
            query = query.filter(Product.is_active == True)
        
        if keyword:
            query = query.filter(
                (Product.name.ilike(f'%{keyword}%')) |
                (Product.description.ilike(f'%{keyword}%'))
            )
        
        if category:
            query = query.filter(Product.category == category)
        
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        
        return query.order_by(Product.created_at.desc()).all()
    
    @staticmethod
    def update_product(
        session: Session,
        product_id: str,
        **updates
    ) -> Optional[Product]:
        """
        Update product details
        """
        product = ProductService.get_product(session, product_id)
        if not product:
            return None
        
        for key, value in updates.items():
            if hasattr(product, key):
                setattr(product, key, value)
        
        product.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(product)
        
        logger.info(f"Product updated: {product.name}")
        return product
    
    @staticmethod
    def update_inventory(
        session: Session,
        product_id: str,
        quantity_change: int
    ) -> Optional[Product]:
        """
        Update product inventory
        
        Args:
            session: Database session
            product_id: Product ID
            quantity_change: Change in quantity (positive or negative)
        
        Returns:
            Updated Product
        """
        product = ProductService.get_product(session, product_id)
        if not product:
            return None
        
        new_quantity = product.quantity + quantity_change
        if new_quantity < 0:
            logger.warning(f"Inventory would be negative for {product.name}")
            return None
        
        product.quantity = new_quantity
        session.commit()
        session.refresh(product)
        
        logger.info(f"Inventory updated for {product.name}: {new_quantity}")
        return product
    
    @staticmethod
    def delete_product(session: Session, product_id: str) -> bool:
        """
        Soft delete product (mark as inactive)
        """
        product = ProductService.get_product(session, product_id)
        if not product:
            return False
        
        product.is_active = False
        session.commit()
        
        logger.info(f"Product deleted: {product.name}")
        return True
    
    @staticmethod
    def get_featured_products(
        session: Session,
        limit: int = 10
    ) -> List[Product]:
        """
        Get featured/trending products
        """
        return session.query(Product).filter(
            Product.is_active == True,
            Product.is_featured == True
        ).order_by(Product.rating.desc()).limit(limit).all()
    
    @staticmethod
    def get_trending_products(
        session: Session,
        limit: int = 10
    ) -> List[Product]:
        """
        Get trending products by review count
        """
        return session.query(Product).filter(
            Product.is_active == True
        ).order_by(Product.review_count.desc()).limit(limit).all()
