"""
LearnHub LMS - Single Run File
================================
This script handles everything needed to start the LMS:
  1. Checks Python & pip
  2. Creates virtual environment if missing
  3. Installs all dependencies
  4. Verifies MongoDB connection
  5. Creates default admin account (if not exists)
  6. Starts the Flask server

Usage:
    python run.py

Default Admin Credentials:
    Email:    admin@learnhub.com
    Password: admin123

Server runs at: http://localhost:5000
"""

import subprocess
import sys
import os

# Force unbuffered output so prints show immediately
os.environ['PYTHONUNBUFFERED'] = '1'

# ─── Paths ────────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, 'backend')
VENV_DIR = os.path.join(ROOT_DIR, 'venv')
REQ_FILE = os.path.join(ROOT_DIR, 'requirements.txt')
ENV_FILE = os.path.join(BACKEND_DIR, '.env')

# Determine venv python/pip paths
if sys.platform == 'win32':
    VENV_PYTHON = os.path.join(VENV_DIR, 'Scripts', 'python.exe')
    VENV_PIP = os.path.join(VENV_DIR, 'Scripts', 'pip.exe')
else:
    VENV_PYTHON = os.path.join(VENV_DIR, 'bin', 'python')
    VENV_PIP = os.path.join(VENV_DIR, 'bin', 'pip')


def print_banner():
    print("=" * 55)
    print("       LearnHub LMS - Learning Management System")
    print("=" * 55)
    print()


def step(msg):
    print(f"[*] {msg}")


def success(msg):
    print(f"[OK] {msg}")


def error(msg):
    print(f"[ERROR] {msg}")


def create_venv():
    """Create virtual environment if it doesn't exist or is broken."""
    if os.path.exists(VENV_PYTHON):
        # Verify the venv actually works
        result = subprocess.run(
            [VENV_PYTHON, '--version'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            success(f"Virtual environment OK ({result.stdout.strip()}).")
            return
        else:
            step("Virtual environment is broken, recreating...")
            import shutil
            shutil.rmtree(VENV_DIR, ignore_errors=True)

    step("Creating virtual environment...")
    subprocess.check_call([sys.executable, '-m', 'venv', VENV_DIR])
    success("Virtual environment created.")


def install_dependencies():
    """Install all packages from requirements.txt."""
    step("Installing dependencies (this may take a minute)...")
    result = subprocess.run(
        [VENV_PIP, 'install', '-r', REQ_FILE, '--quiet'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        error("Failed to install dependencies!")
        print(result.stderr)
        sys.exit(1)
    success("All dependencies installed.")


def check_env_file():
    """Make sure the .env file exists."""
    if os.path.exists(ENV_FILE):
        success(".env file found.")
        return

    step("Creating default .env file...")
    with open(ENV_FILE, 'w') as f:
        f.write(
            "# MongoDB Connection\n"
            "MONGODB_URI=mongodb://localhost:27017/lms_db\n"
            "\n"
            "# JWT Secret Key (change in production!)\n"
            "JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-123456789\n"
            "\n"
            "# Flask\n"
            "FLASK_ENV=development\n"
            "FLASK_APP=app.py\n"
            "FLASK_DEBUG=True\n"
            "\n"
            "# Server\n"
            "PORT=5000\n"
            "HOST=0.0.0.0\n"
        )
    success(".env file created with defaults.")


def test_mongodb():
    """Quick check that MongoDB is reachable."""
    step("Testing MongoDB connection...")
    result = subprocess.run(
        [VENV_PYTHON, '-c',
         "from dotenv import load_dotenv; import os; load_dotenv();"
         "from pymongo import MongoClient;"
         "c = MongoClient(os.getenv('MONGODB_URI','mongodb://localhost:27017/lms_db'), serverSelectionTimeoutMS=5000);"
         "c.admin.command('ping'); print('OK')"],
        capture_output=True, text=True, cwd=BACKEND_DIR
    )
    if 'OK' in result.stdout:
        success("MongoDB is running and reachable.")
    else:
        error("Cannot connect to MongoDB!")
        print("    Make sure MongoDB is running on localhost:27017")
        print("    Or update MONGODB_URI in backend/.env")
        print()
        print("    To install MongoDB locally:")
        print("      - Download: https://www.mongodb.com/try/download/community")
        print("      - Or use MongoDB Atlas (cloud): https://cloud.mongodb.com")
        print()
        ans = input("    Continue anyway? (y/n): ").strip().lower()
        if ans != 'y':
            sys.exit(1)


def create_admin():
    """Create the default admin account if it doesn't exist."""
    step("Checking admin account...")
    result = subprocess.run(
        [VENV_PYTHON, 'create_admin.py'],
        capture_output=True, text=True, cwd=BACKEND_DIR
    )
    print("   ", result.stdout.strip().replace('\n', '\n    '))
    if result.returncode != 0 and result.stderr:
        print("   ", result.stderr.strip().replace('\n', '\n    '))


def start_server():
    """Start the Flask development server."""
    print()
    print("=" * 55)
    print("  Server starting at:  http://localhost:5000")
    print("  Login page:          http://localhost:5000/pages/login.html")
    print("  Admin credentials:   admin@learnhub.com / admin123")
    print("  Press Ctrl+C to stop the server")
    print("=" * 55)
    print()

    # Run app.py from the project root to ensure proper import paths
    os.chdir(ROOT_DIR)
    subprocess.call([VENV_PYTHON, 'app.py'])


def main():
    print_banner()

    try:
        # Step 1 - Virtual environment
        create_venv()

        # Step 2 - Install packages
        install_dependencies()

        # Step 3 - .env file
        check_env_file()

        # Step 4 - MongoDB check
        test_mongodb()

        # Step 5 - Admin account
        create_admin()

        # Step 6 - Launch
        start_server()

    except KeyboardInterrupt:
        print("\nServer stopped.")
    except subprocess.CalledProcessError as e:
        error(f"Command failed: {e}")
        sys.exit(1)
    except Exception as e:
        error(str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
