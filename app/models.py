from datetime import datetime, date
from typing import Optional
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager


class Department(db.Model):
	__tablename__ = "departments"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), unique=True, nullable=False)

	users = db.relationship("User", back_populates="department", cascade="all,delete", lazy="dynamic")

	def __repr__(self) -> str:
		return f"<Department {self.name}>"


class User(db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(200), nullable=False, index=True)
	department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True, index=True)
	join_date = db.Column(db.Date, nullable=False, default=date.today)
	is_newbie = db.Column(db.Boolean, nullable=False, default=True)

	department = db.relationship("Department", back_populates="users")
	scores = db.relationship("Score", back_populates="user", cascade="all,delete", lazy="dynamic")

	def total_points(self) -> int:
		total = 0
		for s in self.scores:
			total += s.points
		return total

	def __repr__(self) -> str:
		return f"<User {self.name}>"


class Activity(db.Model):
	__tablename__ = "activities"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), unique=True, nullable=False)
	description = db.Column(db.Text, nullable=True)

	scores = db.relationship("Score", back_populates="activity", cascade="all,delete", lazy="dynamic")

	def __repr__(self) -> str:
		return f"<Activity {self.name}>"


class Admin(UserMixin, db.Model):
	__tablename__ = "admins"
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	password_hash = db.Column(db.String(256), nullable=False)

	def set_password(self, password: str) -> None:
		self.password_hash = generate_password_hash(password)

	def check_password(self, password: str) -> bool:
		return check_password_hash(self.password_hash, password)

	def __repr__(self) -> str:
		return f"<Admin {self.username}>"


class Score(db.Model):
	__tablename__ = "scores"
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
	activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"), nullable=False, index=True)
	points = db.Column(db.Integer, nullable=False)
	date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=True, index=True)

	user = db.relationship("User", back_populates="scores")
	activity = db.relationship("Activity", back_populates="scores")
	admin = db.relationship("Admin", lazy="joined")

	def __repr__(self) -> str:
		return f"<Score user={self.user_id} points={self.points}>"


@login_manager.user_loader
def load_admin(admin_id: str) -> Optional[Admin]:
	if not admin_id:
		return None
	return db.session.get(Admin, int(admin_id))


