"""
Скрипт для генерации безопасного SECRET_KEY
Использование: python generate_secret_key.py
"""
import secrets

def main():
    key = secrets.token_urlsafe(32)
    print("=" * 60)
    print("Сгенерированный SECRET_KEY:")
    print("=" * 60)
    print(key)
    print("=" * 60)
    print("\nСкопируйте это значение в файл .env:")
    print(f"SECRET_KEY={key}")
    print("\nВАЖНО: Не делитесь этим ключом и не коммитьте его в Git!")

if __name__ == "__main__":
    main()

