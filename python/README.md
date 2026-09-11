# ============================================================================
# SBRCORE - Shared Core Library for SBR Empire
# ============================================================================

## Overview

SBRCORE is the foundation library for all SBR Empire products:
- **sbrbioforge.com** - Environmental intelligence and climate data
- **sbrhikmah.com** - AI-powered super app
- **sbrbeautyhub.com** - E-commerce beauty platform

## Features

### 🔐 Authentication & Security
- JWT token generation and validation
- OAuth2 support (Google, GitHub, Microsoft)
- Role-based access control (RBAC)
- Fine-grained permissions system

### 🗄️ Database
- SQLAlchemy ORM with connection pooling
- Support for PostgreSQL, MySQL, SQLite
- Automatic migrations
- Transaction management

### 🤖 AI Services
- Multi-engine LLM routing
- Groq (fastest inference)
- OpenAI (GPT-4)
- Claude (Anthropic)
- Gemini (Google, multimodal)

### 🛍️ E-Commerce
- Product management
- Order processing
- Payment gateway integration (Stripe, PayPal, Razorpay)
- Inventory management

### 📊 API Utilities
- Authentication decorators
- Rate limiting
- Request logging
- Error handling
- Pagination

## Installation

```bash
pip install sbrcore
```

## Quick Start

### Initialize Database

```python
from sbrcore.database import DatabaseConnection, run_migrations

DatabaseConnection.initialize()
run_migrations()
```

### Create a User

```python
from sbrcore.database import DatabaseConnection, User
from sbrcore.api import hash_password

with DatabaseConnection.session_scope() as session:
    user = User(
        email='user@example.com',
        username='username',
        password_hash=hash_password('password123'),
        full_name='John Doe'
    )
    session.add(user)
```

### Generate JWT Token

```python
from sbrcore.auth import JWTHandler

jwt_handler = JWTHandler()
token = jwt_handler.generate_token(
    user_id='user-123',
    email='user@example.com',
    roles=['user', 'vendor']
)
```

### Use AI Router

```python
import asyncio
from sbrcore.ai import AIRouter

async def get_ai_response():
    router = AIRouter()
    response = await router.route_request(
        prompt="Translate this to Spanish: Hello",
        use_case='translation',
        preferred_engine='groq'
    )
    return response

result = asyncio.run(get_ai_response())
```

### Create a Product

```python
from sbrcore.ecommerce import ProductService
from sbrcore.database import DatabaseConnection

with DatabaseConnection.session_scope() as session:
    product = ProductService.create_product(
        session=session,
        seller_id='seller-123',
        name='Amazing Product',
        description='Best product ever',
        sku='PROD-001',
        price=99.99,
        category='Electronics',
        quantity=100
    )
```

## Environment Variables

Create `.env` file with:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/sbrcore

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# AI Engines
GROQ_API_KEY=your-groq-key
OPENAI_API_KEY=your-openai-key
CLAUDE_API_KEY=your-claude-key
GEMINI_API_KEY=your-gemini-key

# OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret

# E-Commerce
STRIPE_API_KEY=your-stripe-key
```

## Architecture

```
sbrcore/
├── auth/              # Authentication & Authorization
├── database/          # ORM Models & Connection
├── ai/               # AI Router & LLM Engines
├── ecommerce/        # Product, Order, Payment Services
├── api/              # Decorators, Errors, Utilities
├── logging/          # Centralized Logging
├── config.py         # Configuration Manager
└── __init__.py       # Package Initialization
```

## API Error Handling

```python
from sbrcore.api.errors import ValidationError, AuthenticationError

try:
    # Your code
    pass
except ValidationError as e:
    return format_error_response(e.message, e.code, e.status_code)
except AuthenticationError as e:
    return format_error_response(e.message, e.code, e.status_code)
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

## License

MIT License - See LICENSE file

## Support

For issues and questions, visit [GitHub Issues](https://github.com/sbr-empire/sbrcore/issues)
