from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func, desc
from . import db
from .models import Admin, User, Department, Activity, Score

admin_bp = Blueprint("admin", __name__, template_folder="templates")


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		username = request.form.get("username", "").strip()
		password = request.form.get("password", "")
		admin = Admin.query.filter_by(username=username).first()
		if admin and admin.check_password(password):
			login_user(admin)
			flash("Добро пожаловать!", "success")
			return redirect(url_for("admin.dashboard"))
		flash("Неверные логин или пароль", "danger")
	return render_template("admin/login.html")


@admin_bp.route("/logout")
@login_required
def logout():
	logout_user()
	flash("Вы вышли из системы", "info")
	return redirect(url_for("admin.login"))


@admin_bp.route("/")
@login_required
def dashboard():
	user_count = User.query.count()
	dept_count = Department.query.count()
	activity_count = Activity.query.count()
	total_points = db.session.query(func.coalesce(func.sum(Score.points), 0)).scalar() or 0
	recent_scores = Score.query.order_by(Score.date.desc()).limit(10).all()
	return render_template(
		"admin/dashboard.html",
		user_count=user_count,
		dept_count=dept_count,
		activity_count=activity_count,
		total_points=total_points,
		recent_scores=recent_scores,
	)


# Departments CRUD
@admin_bp.route("/departments", methods=["GET", "POST"])
@login_required
def departments():
	if request.method == "POST":
		name = request.form.get("name", "").strip()
		if name:
			if Department.query.filter_by(name=name).first():
				flash("Отдел с таким названием уже существует", "warning")
			else:
				db.session.add(Department(name=name))
				db.session.commit()
				flash("Отдел добавлен", "success")
		return redirect(url_for("admin.departments"))
	depts = Department.query.order_by(Department.name.asc()).all()
	return render_template("admin/departments.html", departments=depts)


@admin_bp.route("/departments/<int:dept_id>/delete", methods=["POST"])
@login_required
def delete_department(dept_id: int):
	dept = Department.query.get_or_404(dept_id)
	db.session.delete(dept)
	db.session.commit()
	flash("Отдел удален", "info")
	return redirect(url_for("admin.departments"))


# Activities CRUD
@admin_bp.route("/activities", methods=["GET", "POST"])
@login_required
def activities():
	if request.method == "POST":
		name = request.form.get("name", "").strip()
		description = request.form.get("description", "").strip()
		if name:
			if Activity.query.filter_by(name=name).first():
				flash("Активность с таким названием уже существует", "warning")
			else:
				db.session.add(Activity(name=name, description=description or None))
				db.session.commit()
				flash("Активность добавлена", "success")
		return redirect(url_for("admin.activities"))
	acts = Activity.query.order_by(Activity.name.asc()).all()
	return render_template("admin/activities.html", activities=acts)


@admin_bp.route("/activities/<int:activity_id>/delete", methods=["POST"])
@login_required
def delete_activity(activity_id: int):
	activity = Activity.query.get_or_404(activity_id)
	db.session.delete(activity)
	db.session.commit()
	flash("Активность удалена", "info")
	return redirect(url_for("admin.activities"))


# Users CRUD
@admin_bp.route("/users", methods=["GET", "POST"])
@login_required
def users():
	if request.method == "POST":
		name = request.form.get("name", "").strip()
		department_id = request.form.get("department_id")
		join_date_str = request.form.get("join_date", "")
		is_newbie = request.form.get("is_newbie") == "on"
		if not name:
			flash("Имя обязательно", "warning")
			return redirect(url_for("admin.users"))
		join_date = None
		if join_date_str:
			try:
				join_date = datetime.strptime(join_date_str, "%Y-%m-%d").date()
			except ValueError:
				flash("Некорректная дата", "warning")
				return redirect(url_for("admin.users"))
		user = User(
			name=name,
			department_id=int(department_id) if department_id else None,
			join_date=join_date or date.today(),
			is_newbie=is_newbie,
		)
		db.session.add(user)
		db.session.commit()
		flash("Участник добавлен", "success")
		return redirect(url_for("admin.users"))
	departments = Department.query.order_by(Department.name.asc()).all()
	all_users = User.query.order_by(User.name.asc()).all()
	return render_template("admin/users.html", users=all_users, departments=departments)


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id: int):
	user = User.query.get_or_404(user_id)
	db.session.delete(user)
	db.session.commit()
	flash("Участник удален", "info")
	return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/edit", methods=["POST"])
@login_required
def edit_user(user_id: int):
	user = User.query.get_or_404(user_id)
	name = request.form.get("name", "").strip()
	department_id = request.form.get("department_id")
	is_newbie = request.form.get("is_newbie") == "on"
	if name:
		user.name = name
	user.department_id = int(department_id) if department_id else None
	user.is_newbie = is_newbie
	db.session.commit()
	flash("Участник обновлен", "success")
	return redirect(url_for("admin.users"))


# Scoring
@admin_bp.route("/scores", methods=["GET", "POST"])
@login_required
def scores():
	if request.method == "POST":
		user_id = int(request.form.get("user_id"))
		activity_id = int(request.form.get("activity_id"))
		points = int(request.form.get("points"))

		# Basic validation based on activity categories described in TЗ
		# Events: 1-10, Tasks: 1-5, Meetings: 1-3. We do not hardcode categories,
		# but we keep a safety bound check of 1..10.
		if points < 1 or points > 10:
			flash("Баллы должны быть от 1 до 10", "warning")
			return redirect(url_for("admin.scores"))

		score = Score(user_id=user_id, activity_id=activity_id, points=points, admin_id=current_user.id)
		db.session.add(score)
		db.session.commit()
		flash("Баллы начислены", "success")
		return redirect(url_for("admin.scores"))

	users = User.query.order_by(User.name.asc()).all()
	activities = Activity.query.order_by(Activity.name.asc()).all()
	recent_scores = (
		db.session.query(Score, User.name.label("user_name"), Activity.name.label("activity_name"))
		.join(User, Score.user_id == User.id)
		.join(Activity, Score.activity_id == Activity.id)
		.order_by(Score.date.desc())
		.limit(50)
		.all()
	)
	return render_template("admin/scores.html", users=users, activities=activities, recent_scores=recent_scores)


# Admin bootstrap (create first admin)
@admin_bp.route("/bootstrap_admin", methods=["POST"])
def bootstrap_admin():
	# Public endpoint only if there are no admins yet
	if Admin.query.first():
		return ("Forbidden", 403)
	username = request.form.get("username", "").strip()
	password = request.form.get("password", "")
	if not username or not password:
		return ("Username and password required", 400)
	admin = Admin(username=username)
	admin.set_password(password)
	db.session.add(admin)
	db.session.commit()
	return ("OK", 201)


