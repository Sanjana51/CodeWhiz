from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ---------- User Table ----------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200))  # Nullable for OAuth users
    name = db.Column(db.String(100))
    auth_type = db.Column(db.String(20), default="form")

# ---------- Problem Table ----------
class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    topic_tags = db.Column(db.PickleType)

    # Language-specific function signatures
    python_function_signature = db.Column(db.String(300))
    cpp_function_signature = db.Column(db.String(300))

    # Language-specific starter code
    python_starter_code = db.Column(db.Text)
    cpp_starter_code = db.Column(db.Text)

    # Language-specific driver code
    python_driver_code = db.Column(db.Text)
    cpp_driver_code = db.Column(db.Text)

    test_cases = db.relationship('TestCase', backref='problem', cascade="all, delete-orphan")


# ---------- TestCase Table ----------
class TestCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    input_data = db.Column(db.Text, nullable=False)
    expected_output = db.Column(db.Text, nullable=False)
    is_sample = db.Column(db.Boolean, default=False)
    explanation = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)

    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), nullable=False)
