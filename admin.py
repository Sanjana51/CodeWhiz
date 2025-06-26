from flask import Blueprint, request, jsonify, flash, redirect, url_for
from slugify import slugify
from models import db, Problem, TestCase
import json

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

from flask import render_template

@admin_bp.route('/dashboard')
def dashboard():
    return render_template('admin.html')



@admin_bp.route('/create-problem', methods=['POST'])
def create_problem():
    try:
        data = request.get_json()
        title = data['title']
        slug = slugify(title)
        description = data['description']
        difficulty = data['difficulty']
        topic_tags = data.get('topic_tags', [])
        time_limit = int(data.get('time_limit', 1000))
        memory_limit = int(data.get('memory_limit', 256))
        default_code_templates = data.get('default_code_templates', {})

        problem = Problem(
            title=title,
            slug=slug,
            description=description,
            difficulty=difficulty,
            topic_tags=topic_tags,
            time_limit=time_limit,
            memory_limit=memory_limit,
            default_code_templates=default_code_templates
        )
        db.session.add(problem)
        db.session.commit()

        return jsonify({"message": "Problem created", "slug": slug}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@admin_bp.route('/add-testcase/<slug>', methods=['POST'])
def add_testcase(slug):
    try:
        problem = Problem.query.filter_by(slug=slug).first()
        if not problem:
            return jsonify({"error": "Problem not found"}), 404

        data = request.get_json()
        input_data = data['input_data']
        expected_output = data['expected_output']
        is_sample = data.get('is_sample', False)
        explanation = data.get('explanation', '')

        test_case = TestCase(
            input_data=input_data,
            expected_output=expected_output,
            is_sample=is_sample,
            explanation=explanation,
            problem=problem
        )
        db.session.add(test_case)
        db.session.commit()

        return jsonify({"message": "Test case added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
