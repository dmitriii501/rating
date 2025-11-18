"""
Быстрое создание администратора с простыми учетными данными.
Использование: python create_default_admin.py
Создает администратора с логином 'admin' и паролем 'admin123'
"""
from app import create_app, db
from app.models import Admin

def main():
    app = create_app()
    with app.app_context():
        # Проверяем, есть ли уже админы
        existing = Admin.query.first()
        if existing:
            print("Administrator already exists!")
            print("To create another admin, use: python create_admin.py --username <username> --password <password>")
            return
        
        # Создаем администратора с простыми учетными данными
        username = "admin"
        password = "admin123"
        
        admin = Admin(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        
        print("=" * 60)
        print("Administrator created successfully!")
        print("=" * 60)
        print(f"Username: {username}")
        print(f"Password: {password}")
        print("\n⚠️  IMPORTANT: Change the password after first login!")
        print("=" * 60)

if __name__ == "__main__":
    main()

