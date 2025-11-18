import os
import sys
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

activate_this = os.path.join(BASE_DIR, "venv", "bin", "activate_this.py")
if os.path.exists(activate_this):
    with open(activate_this) as f:
        exec(f.read(), {"__file__": activate_this})

log_dir = "/var/www/u3325711/data/logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "app.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logging.info("Passenger WSGI starting")

from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(BASE_DIR, ".env"))

from app import create_app  # noqa: E402

try:
    application = create_app()
    logging.info("create_app completed successfully")
except Exception:
    logging.exception("create_app failed")
    raise

