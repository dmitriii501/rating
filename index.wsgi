import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

activate_this = os.path.join(BASE_DIR, "venv", "bin", "activate_this.py")
if os.path.exists(activate_this):
    with open(activate_this) as f:
        exec(f.read(), {"__file__": activate_this})

from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(BASE_DIR, ".env"))

from app import create_app  # noqa: E402

application = create_app()

