from app import create_app, db
from app.models import Department, Activity

DEPARTMENTS = [
	"АйТи",
	"Дмитрий Худяков",
	"Дмитрий Шнайдер",
	"Орг отдел",
	"Ольга Гурова",
	"Александр Ревин",
	"Анна Пряничникова",
	"Смм отдел",
	"Анна Мальцева",
	"Дарья Сысоева",
	"Екатерина Стрельцова",
	"Варвара Трифонова",
	"Грантовый отдел",
	"Антонида Нагорных",
	"Дизайн отдела",
	"Фандрайзинг отдел",
	"Максим Альбрант",
]

ACTIVITIES = [
	("Мероприятие", "Посещение/организация мероприятия (1–10)"),
	("Задание", "Выполнение задания (1–5)"),
	("Собрание", "Посещение собрания (1–3)"),
]


def main():
	app = create_app()
	with app.app_context():
		for name in DEPARTMENTS:
			if not Department.query.filter_by(name=name).first():
				db.session.add(Department(name=name))
		for name, desc in ACTIVITIES:
			if not Activity.query.filter_by(name=name).first():
				db.session.add(Activity(name=name, description=desc))
		db.session.commit()
		print("Seed completed.")


if __name__ == "__main__":
	main()


