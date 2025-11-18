"""
Скрипт для создания администратора с безопасным паролем.
Использование: 
    python create_admin.py              # Автоматическое создание
    python create_admin.py --auto       # То же самое
    python create_admin.py --username myadmin --password mypass  # С указанными данными
"""
import secrets
import string
import sys
import os
from app import create_app, db
from app.models import Admin

def generate_secure_password(length=20):
    """Генерирует безопасный пароль"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def safe_input(prompt):
    """Безопасный ввод с обработкой ошибок кодировки"""
    try:
        return input(prompt).strip().lower()
    except (UnicodeDecodeError, EOFError, KeyboardInterrupt):
        # Если проблема с кодировкой или нет интерактивного ввода
        return 'y'  # По умолчанию соглашаемся

def main():
    # Парсим аргументы командной строки
    auto_mode = '--auto' in sys.argv or len(sys.argv) == 1
    username_arg = None
    password_arg = None
    
    if '--username' in sys.argv:
        idx = sys.argv.index('--username')
        if idx + 1 < len(sys.argv):
            username_arg = sys.argv[idx + 1]
    
    if '--password' in sys.argv:
        idx = sys.argv.index('--password')
        if idx + 1 < len(sys.argv):
            password_arg = sys.argv[idx + 1]
    
    app = create_app()
    with app.app_context():
        # Устанавливаем кодировку для вывода
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except:
                pass
        
        print("=" * 60)
        print("Creating administrator")
        print("=" * 60)
        
        # Проверяем, есть ли уже админы
        existing = Admin.query.first()
        if existing and not auto_mode:
            print(f"\nWarning: Administrator(s) already exist.")
            if not auto_mode:
                response = safe_input("Create another one? (y/n): ")
                if response != 'y':
                    print("Cancelled.")
                    return
        
        # Генерируем или используем указанные учетные данные
        if username_arg:
            username = username_arg
        else:
            username = "admin_" + ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6))
        
        if password_arg:
            password = password_arg
        else:
            password = generate_secure_password(20)
        
        print(f"\nGenerated credentials:")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print("\n" + "=" * 60)
        print("IMPORTANT: Save these credentials in a safe place!")
        print("=" * 60)
        
        # Подтверждение (только если не автоматический режим)
        if not auto_mode:
            confirm = safe_input("\nCreate administrator with these credentials? (y/n): ")
            if confirm != 'y':
                print("Cancelled.")
                return
        
        # Создаем админа
        admin = Admin(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        
        print(f"\n[OK] Administrator '{username}' created successfully!")
        print("\nYou can now login at /admin/login")
        print(f"\nUsername: {username}")
        print(f"Password: {password}")

if __name__ == "__main__":
    main()

