# ============================================================================
# Order Management Service
# Create, track, and manage orders
# ============================================================================

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from ..database.models import Order, OrderItem, Product, Payment
from ..logging import get_logger
from datetime import datetime
import uuid
import json

logger = get_logger(__name__)

class OrderService:
    """
    Manages order operations and tracking
    """
    
    @staticmethod
    def create_order(
        session: Session,
        user_id: str,
        items: List[Dict],  # [{product_id, quantity}, ...]
        shipping_address: Dict,
        **kwargs
    ) -> Optional[Order]:
        """
        Create new order
        
        Args:
            session: Database session
            user_id: Customer user ID
            items: List of items with product_id and quantity
            shipping_address: Shipping address details
        
        Returns:
            Created Order object
        """
        # Calculate totals
        subtotal = 0
        order_items = []
        
        for item in items:
            product = session.query(Product).filter(
                Product.id == item['product_id']
            ).first()
            
            if not product:
                logger.error(f"Product not found: {item['product_id']}")
                return None
            
            if product.quantity < item['quantity']:
                logger.error(f"Insufficient inventory for {product.name}")
                return None
            
            item_total = product.price * item['quantity']
            subtotal += item_total
            
            order_items.append(
                OrderItem(
                    product_id=product.id,
                    quantity=item['quantity'],
                    unit_price=product.price,
                    total_price=item_total
                )
            )
        
        # Create order
        order = Order(
            user_id=user_id,
            order_number=f"ORD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}",
            subtotal=subtotal,
            tax=subtotal * 0.10,  # 10% tax
            shipping_cost=kwargs.get('shipping_cost', 0),
            discount=kwargs.get('discount', 0),
            shipping_address=json.dumps(shipping_address),
            items=order_items
        )
        
        order.total = order.subtotal + order.tax + order.shipping_cost - order.discount
        
        # Reduce inventory
        for item in items:
            product = session.query(Product).filter(
                Product.id == item['product_id']
            ).first()
            product.quantity -= item['quantity']
        
        session.add(order)
        session.commit()
        session.refresh(order)
        
        logger.info(f"Order created: {order.order_number}")
        return order
    
    @staticmethod
    def get_order(session: Session, order_id: str) -> Optional[Order]:
        """
        Get order by ID
        """
        return session.query(Order).filter(Order.id == order_id).first()
    
    @staticmethod
    def get_order_by_number(session: Session, order_number: str) -> Optional[Order]:
        """
        Get order by order number
        """
        return session.query(Order).filter(Order.order_number == order_number).first()
    
    @staticmethod
    def get_user_orders(
        session: Session,
        user_id: str,
        limit: int = 50
    ) -> List[Order]:
        """
        Get all orders for a user
        """
        return session.query(Order).filter(
            Order.user_id == user_id
        ).order_by(Order.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def update_order_status(
        session: Session,
        order_id: str,
        status: str
    ) -> Optional[Order]:
        """
        Update order status
        """
        order = OrderService.get_order(session, order_id)
        if not order:
            return None
        
        order.status = status
        
        if status == 'shipped':
            order.shipped_at = datetime.utcnow()
        elif status == 'delivered':
            order.delivered_at = datetime.utcnow()
        
        session.commit()
        session.refresh(order)
        
        logger.info(f"Order {order.order_number} status updated to {status}")
        return order
    
    @staticmethod
    def cancel_order(session: Session, order_id: str) -> Optional[Order]:
        """
        Cancel order and restore inventory
        """
        order = OrderService.get_order(session, order_id)
        if not order:
            return None
        
        # Check if order can be cancelled
        if order.status in ['shipped', 'delivered']:
            logger.warning(f"Cannot cancel order {order.order_number} - already {order.status}")
            return None
        
        # Restore inventory
        for item in order.items:
            item.product.quantity += item.quantity
        
        order.status = 'cancelled'
        session.commit()
        session.refresh(order)
        
        logger.info(f"Order cancelled: {order.order_number}")
        return order
    
    @staticmethod
    def get_order_analytics(
        session: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get order analytics
        """
        query = session.query(Order)
        
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)
        
        orders = query.all()
        
        total_revenue = sum(order.total for order in orders)
        total_orders = len(orders)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        status_distribution = {}
        for order in orders:
            status = order.status.value
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        return {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'avg_order_value': avg_order_value,
            'status_distribution': status_distribution
        }
