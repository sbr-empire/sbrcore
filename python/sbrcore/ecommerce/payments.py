# ============================================================================
# Payment Processing Service
# Handle payments, refunds, and transaction management
# ============================================================================

from typing import Dict, Optional, Any
from sqlalchemy.orm import Session
from ..database.models import Payment, Order
from ..logging import get_logger
from datetime import datetime
import httpx

logger = get_logger(__name__)

class PaymentService:
    """
    Manages payment processing and transactions
    Supports: Stripe, PayPal, Razorpay
    """
    
    PAYMENT_GATEWAYS = {
        'stripe': 'https://api.stripe.com/v1',
        'paypal': 'https://api.paypal.com/v1',
        'razorpay': 'https://api.razorpay.com/v1'
    }
    
    @staticmethod
    def create_payment(
        session: Session,
        order_id: str,
        amount: float,
        currency: str = 'USD',
        **kwargs
    ) -> Optional[Payment]:
        """
        Create payment record
        """
        order = session.query(Order).filter(Order.id == order_id).first()
        if not order:
            logger.error(f"Order not found: {order_id}")
            return None
        
        payment = Payment(
            order_id=order_id,
            amount=amount,
            currency=currency,
            gateway=kwargs.get('gateway', 'stripe'),
            status='pending'
        )
        
        session.add(payment)
        session.commit()
        session.refresh(payment)
        
        logger.info(f"Payment created for order {order.order_number}")
        return payment
    
    @staticmethod
    def get_payment(session: Session, payment_id: str) -> Optional[Payment]:
        """
        Get payment by ID
        """
        return session.query(Payment).filter(Payment.id == payment_id).first()
    
    @staticmethod
    def get_payment_by_transaction(
        session: Session,
        transaction_id: str
    ) -> Optional[Payment]:
        """
        Get payment by transaction ID
        """
        return session.query(Payment).filter(
            Payment.transaction_id == transaction_id
        ).first()
    
    @staticmethod
    async def process_payment(
        session: Session,
        payment_id: str,
        payment_token: str,
        gateway: str = 'stripe'
    ) -> Dict[str, Any]:
        """
        Process payment through gateway
        
        Args:
            session: Database session
            payment_id: Payment record ID
            payment_token: Token from payment gateway
            gateway: Payment gateway name
        
        Returns:
            Payment result dictionary
        """
        payment = PaymentService.get_payment(session, payment_id)
        if not payment:
            return {'status': 'failed', 'error': 'Payment not found'}
        
        try:
            if gateway == 'stripe':
                result = await PaymentService._process_stripe(
                    payment,
                    payment_token
                )
            elif gateway == 'paypal':
                result = await PaymentService._process_paypal(
                    payment,
                    payment_token
                )
            elif gateway == 'razorpay':
                result = await PaymentService._process_razorpay(
                    payment,
                    payment_token
                )
            else:
                return {'status': 'failed', 'error': 'Unknown gateway'}
            
            # Update payment status
            if result.get('status') == 'success':
                payment.status = 'success'
                payment.transaction_id = result.get('transaction_id')
                payment.completed_at = datetime.utcnow()
                
                # Update order status
                order = payment.order
                order.status = 'confirmed'
                order.payment_id = payment.id
                
                session.commit()
                logger.info(f"Payment processed successfully: {payment.id}")
            else:
                payment.status = 'failed'
                session.commit()
                logger.warning(f"Payment failed: {result.get('error')}")
            
            return result
        
        except Exception as e:
            logger.error(f"Payment processing error: {str(e)}")
            payment.status = 'failed'
            session.commit()
            return {'status': 'failed', 'error': str(e)}
    
    @staticmethod
    async def _process_stripe(
        payment: Payment,
        payment_token: str
    ) -> Dict[str, Any]:
        """
        Process payment via Stripe
        """
        from ..config import Config
        
        payload = {
            'amount': int(payment.amount * 100),  # Stripe uses cents
            'currency': payment.currency.lower(),
            'source': payment_token,
            'description': f"Order {payment.order.order_number}"
        }
        
        headers = {
            'Authorization': f'Bearer {Config.STRIPE_API_KEY}',
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{PaymentService.PAYMENT_GATEWAYS['stripe']}/charges",
                data=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'success',
                    'transaction_id': data['id'],
                    'amount': payment.amount,
                    'currency': payment.currency
                }
            else:
                return {
                    'status': 'failed',
                    'error': response.json().get('error', {}).get('message', 'Unknown error')
                }
    
    @staticmethod
    async def _process_paypal(
        payment: Payment,
        payment_token: str
    ) -> Dict[str, Any]:
        """
        Process payment via PayPal
        """
        # PayPal implementation
        logger.info("PayPal processing not yet implemented")
        return {'status': 'pending', 'message': 'PayPal processing pending'}
    
    @staticmethod
    async def _process_razorpay(
        payment: Payment,
        payment_token: str
    ) -> Dict[str, Any]:
        """
        Process payment via Razorpay
        """
        # Razorpay implementation
        logger.info("Razorpay processing not yet implemented")
        return {'status': 'pending', 'message': 'Razorpay processing pending'}
    
    @staticmethod
    def refund_payment(
        session: Session,
        payment_id: str,
        reason: str = 'Customer request'
    ) -> Optional[Payment]:
        """
        Refund a payment
        """
        payment = PaymentService.get_payment(session, payment_id)
        if not payment:
            return None
        
        if payment.status != 'success':
            logger.warning(f"Cannot refund non-successful payment: {payment_id}")
            return None
        
        payment.status = 'refunded'
        payment.order.status = 'refunded'
        
        session.commit()
        session.refresh(payment)
        
        logger.info(f"Payment refunded: {payment_id} - {reason}")
        return payment
