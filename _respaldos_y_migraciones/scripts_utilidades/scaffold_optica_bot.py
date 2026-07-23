import os
from pathlib import Path

base_dir = Path(r"c:\Users\Antho\Happy app\optica-bot")

structure = [
    # root files
    ".env",
    ".env.example",
    ".gitignore",
    "requirements.txt",
    "pyproject.toml",
    "alembic.ini",
    "README.md",
    "docker-compose.yml",

    # directories
    "alembic",
    "tests/test_orders.py",
    "tests/test_payments.py",
    "tests/test_laboratories.py",
    "tests/test_whatsapp_bot.py",
    "tests/__init__.py",

    # app root
    "app/__init__.py",
    "app/main.py",

    # app/core
    "app/core/__init__.py",
    "app/core/config.py",
    "app/core/security.py",
    "app/core/database.py",
    "app/core/logging.py",
    "app/core/constants.py",

    # app/models
    "app/models/__init__.py",
    "app/models/base.py",
    "app/models/patient.py",
    "app/models/product.py",
    "app/models/prescription.py",
    "app/models/order.py",
    "app/models/payment.py",
    "app/models/laboratory.py",
    "app/models/lab_order.py",

    # app/schemas
    "app/schemas/__init__.py",
    "app/schemas/patient.py",
    "app/schemas/product.py",
    "app/schemas/prescription.py",
    "app/schemas/order.py",
    "app/schemas/payment.py",
    "app/schemas/laboratory.py",
    "app/schemas/lab_order.py",

    # app/crud
    "app/crud/__init__.py",
    "app/crud/patient.py",
    "app/crud/product.py",
    "app/crud/prescription.py",
    "app/crud/order.py",
    "app/crud/payment.py",
    "app/crud/laboratory.py",
    "app/crud/lab_order.py",

    # app/services
    "app/services/__init__.py",
    "app/services/order_service.py",
    "app/services/payment_service.py",
    "app/services/whatsapp_service.py",
    "app/services/laboratory_router.py",
    "app/services/pdf_service.py",
    "app/services/pricing_service.py",

    # app/api
    "app/api/__init__.py",
    "app/api/deps.py",
    "app/api/v1/__init__.py",
    "app/api/v1/api.py",
    
    # app/api/v1/endpoints
    "app/api/v1/endpoints/__init__.py",
    "app/api/v1/endpoints/patients.py",
    "app/api/v1/endpoints/products.py",
    "app/api/v1/endpoints/orders.py",
    "app/api/v1/endpoints/payments.py",
    "app/api/v1/endpoints/laboratories.py",
    "app/api/v1/endpoints/whatsapp.py",
    "app/api/v1/endpoints/webhooks.py",

    # app/bots
    "app/bots/__init__.py",
    "app/bots/whatsapp_bot.py",
    "app/bots/conversation_flow.py",
    "app/bots/validators.py",
    "app/bots/responses.py",

    # templates & static
    "app/templates/order_pdf.html",
    "app/templates/lab_order_pdf.html",
    "app/static/images/.gitkeep",
    "app/static/uploads/.gitkeep",

    # utils
    "app/utils/__init__.py",
    "app/utils/helpers.py",
    "app/utils/enums.py",
    "app/utils/date_utils.py",
    "app/utils/file_utils.py",
]

for path_str in structure:
    p = base_dir / path_str
    if not p.parent.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
    if not path_str.endswith("/") and not p.exists() and "." in p.name or "gitkeep" in p.name or path_str.endswith(".py"):
        p.touch()

print("Estructura optica-bot creada.")
