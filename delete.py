from app import app, db
from models import Problem, TestCase

with app.app_context():
    problem = Problem.query.filter_by(slug="next-permutation").first()
    if problem:
        TestCase.query.filter_by(problem_id=problem.id).delete()
        db.session.delete(problem)
        db.session.commit()
        print("✅ Deleted existing 'next-permutation' problem.")




