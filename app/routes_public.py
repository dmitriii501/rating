from datetime import date
from flask import Blueprint, render_template, request, abort
from sqlalchemy import func, desc
from . import db
from .models import User, Department, Score

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
	return render_template("home.html")


@public_bp.route("/rating")
def rating():
	# Overall rating by total points
	# Efficient aggregation: SUM(points) grouped by user
	subq = db.session.query(
		Score.user_id.label("user_id"),
		func.coalesce(func.sum(Score.points), 0).label("total_points"),
	).group_by(Score.user_id).subquery()

	rows = (
		db.session.query(User, func.coalesce(subq.c.total_points, 0))
		.outerjoin(subq, User.id == subq.c.user_id)
		.order_by(desc(subq.c.total_points))
		.all()
	)
	return render_template("rating.html", rows=rows)


@public_bp.route("/departments")
def departments():
	depts = Department.query.order_by(Department.name.asc()).all()
	return render_template("departments.html", departments=depts)


@public_bp.route("/departments/<int:dept_id>")
def department_rating(dept_id: int):
	dept = Department.query.get_or_404(dept_id)
	subq = db.session.query(
		Score.user_id.label("user_id"),
		func.coalesce(func.sum(Score.points), 0).label("total_points"),
	).group_by(Score.user_id).subquery()
	rows = (
		db.session.query(User, func.coalesce(subq.c.total_points, 0))
		.filter(User.department_id == dept.id)
		.outerjoin(subq, User.id == subq.c.user_id)
		.order_by(desc(subq.c.total_points))
		.all()
	)
	return render_template("department_rating.html", department=dept, rows=rows)


@public_bp.route("/newbies")
def newbies():
	# Newbies joined this semester (simple heuristic: same year and month // 6)
	today = date.today()
	semester_key = (today.year, 1 if today.month <= 6 else 2)

	def is_same_semester(d: date) -> bool:
		return (d.year, 1 if d.month <= 6 else 2) == semester_key

	users = User.query.all()
	filtered = [u for u in users if is_same_semester(u.join_date)]

	# Compute totals
	subq = db.session.query(
		Score.user_id.label("user_id"),
		func.coalesce(func.sum(Score.points), 0).label("total_points"),
	).group_by(Score.user_id).subquery()
	rows = (
		db.session.query(User, func.coalesce(subq.c.total_points, 0))
		.filter(User.id.in_([u.id for u in filtered] or [-1]))
		.outerjoin(subq, User.id == subq.c.user_id)
		.order_by(desc(subq.c.total_points))
		.all()
	)
	return render_template("newbies.html", rows=rows)


@public_bp.route("/profile/<int:user_id>")
def profile(user_id: int):
	user = User.query.get_or_404(user_id)
	# Recent scores
	scores = (
		Score.query.filter(Score.user_id == user.id)
		.order_by(Score.date.desc())
		.limit(50)
		.all()
	)
	total = sum(s.points for s in scores)
	return render_template("profile.html", user=user, scores=scores, total=total)


