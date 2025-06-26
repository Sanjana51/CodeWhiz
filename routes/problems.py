from flask import Blueprint, request, jsonify, render_template
from models import db, Problem, TestCase
from slugify import slugify

problem_bp = Blueprint("problem_bp", __name__)

# 🔹 Web Route: Render all problems (for users)
@problem_bp.route('/problems', methods=['GET'])
def problems_page():
    problems = Problem.query.all()
    return render_template("problems.html", problems=problems)

# 🔹 API: Create a new problem
@problem_bp.route('/api/problems', methods=['POST'])
def create_problem():
    data = request.get_json()
    slug = slugify(data['title'])

    new_problem = Problem(
        title=data['title'],
        slug=slug,
        description=data['description'],
        difficulty=data['difficulty'],
        time_limit=data.get('time_limit', 1000),
        memory_limit=data.get('memory_limit', 256),
        topic_tags=data.get('topic_tags', []),
        default_code_templates=data.get('default_code_templates', {}),
        function_signature=data.get('function_signature', ''),
        starter_code=data.get('starter_code', ''),
        driver_code=data.get('driver_code', '')
    )
    db.session.add(new_problem)
    db.session.commit()
    return jsonify({'message': 'Problem created', 'slug': slug}), 201

# 🔹 API: Get all problems with search, filter, sort
@problem_bp.route('/api/problems', methods=['GET'])
def get_problems():
    query = Problem.query

    # 🔍 Search
    search = request.args.get('search')
    if search:
        query = query.filter(Problem.title.ilike(f"%{search}%"))

    # 🎯 Filter
    difficulty = request.args.get('difficulty')
    if difficulty:
        query = query.filter_by(difficulty=difficulty)

    # 🔃 Sort
    sort = request.args.get('sort', 'id')  # Default to ID
    if sort == 'title':
        query = query.order_by(Problem.title)
    elif sort == 'difficulty':
        query = query.order_by(Problem.difficulty)
    else:
        query = query.order_by(Problem.id)

    problems = query.all()
    result = [{
        'id': p.id,
        'title': p.title,
        'slug': p.slug,
        'difficulty': p.difficulty,
        'tags': p.topic_tags
    } for p in problems]

    return jsonify(result)

# 🔹 API: Get a problem by slug
@problem_bp.route('/api/problems/<slug>', methods=['GET'])
def get_problem(slug):
    problem = Problem.query.filter_by(slug=slug).first()
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404

    test_cases = [{
        'id': tc.id,
        'input': tc.input_data,
        'expected': tc.expected_output,
        'is_sample': tc.is_sample,
        'explanation': tc.explanation
    } for tc in problem.test_cases]

    return jsonify({
        'title': problem.title,
        'description': problem.description,
        'difficulty': problem.difficulty,
        'tags': problem.topic_tags,
        'time_limit': problem.time_limit,
        'memory_limit': problem.memory_limit,
        'default_code_templates': problem.default_code_templates,
        'function_signature': problem.function_signature,
        'starter_code': problem.starter_code,
        'driver_code': problem.driver_code,
        'test_cases': test_cases
    })

# 🔹 API: Add a test case to a problem
@problem_bp.route('/api/problems/<slug>/testcases', methods=['POST'])
def add_test_case(slug):
    problem = Problem.query.filter_by(slug=slug).first()
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404

    data = request.get_json()
    test_case = TestCase(
        input_data=data['input_data'],
        expected_output=data['expected_output'],
        is_sample=data.get('is_sample', False),
        explanation=data.get('explanation'),
        order=data.get('order', 0),
        problem=problem
    )
    db.session.add(test_case)
    db.session.commit()
    return jsonify({'message': 'Test case added'}), 201
