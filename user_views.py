import os
import time
import json
import re
import requests
from flask import Blueprint, request, jsonify, render_template
from models import db, Problem, TestCase
from utils.auth import login_required


# 🧠 Gemini AI setup
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use the correct model name
gemini_model= genai.GenerativeModel(model_name="models/gemini-1.5-flash")

user_bp = Blueprint("user_views", __name__)

# 🌐 Judge0 + RapidAPI
JUDGE0_URL = "https://judge0-ce.p.rapidapi.com"
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
HEADERS = {
    "x-rapidapi-host": "judge0-ce.p.rapidapi.com",
    "x-rapidapi-key": RAPIDAPI_KEY,
    "content-type": "application/json"
}

# 🔢 Language ID map
LANGUAGE_MAP = {
    "python": 71,
    "cpp": 54
}

# === Utility Functions ===

def normalize_output(s):
    return re.sub(r"[^\d\s\-]", "", s).strip()

def convert_input_for_cpp(input_str):
    try:
        data = json.loads(input_str)
        if isinstance(data, list) and len(data) == 2 and isinstance(data[0], list) and isinstance(data[1], int):
            arr, target = data
            return f"{len(arr)}\n{' '.join(map(str, arr))}\n{target}"
        if isinstance(data, list) and all(isinstance(x, int) for x in data):
            return f"{len(data)}\n{' '.join(map(str, data))}"
        return input_str
    except Exception:
        return input_str

def submit_code(code, language_id, stdin=""):
    res = requests.post(
        f"{JUDGE0_URL}/submissions?base64_encoded=false&wait=false",
        headers=HEADERS,
        json={"source_code": code, "language_id": language_id, "stdin": stdin}
    )
    res.raise_for_status()
    return res.json()["token"]

def get_submission_result(token):
    while True:
        res = requests.get(f"{JUDGE0_URL}/submissions/{token}?base64_encoded=false", headers=HEADERS)
        res.raise_for_status()
        data = res.json()
        if data["status"]["id"] in [1, 2]:
            time.sleep(1)
            continue
        return data

def get_llm_response(prompt):
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Gemini Error] {str(e)}"

# === Routes ===
@user_bp.route("/problems")
@login_required
def all_problems():
    problems = Problem.query.all()
    return render_template("problems.html", problems=problems)


@user_bp.route("/problem/<slug>")
@login_required
def view_problem(slug):
    problem = Problem.query.filter_by(slug=slug).first_or_404()
    language_data = {
        lang: {
            "starter_code": getattr(problem, f"{lang}_starter_code"),
            "function_signature": getattr(problem, f"{lang}_function_signature")
        } for lang in LANGUAGE_MAP
    }
    return render_template("problem_detail.html", problem=problem, language_data=language_data)

@user_bp.route("/run", methods=["POST"])
@login_required
def run_code():
    data = request.get_json()
    user_code = data.get("code", "")
    language = data.get("language", "").lower()
    input_data = data.get("input", "")
    slug = data.get("slug")

    language_id = LANGUAGE_MAP.get(language)
    if not user_code or not language_id:
        return jsonify({"message": "Code and supported language are required"}), 400

    problem = Problem.query.filter_by(slug=slug).first_or_404()
    driver_code = getattr(problem, f"{language}_driver_code", "")
    full_code = f"{user_code.strip()}\n\n{driver_code}"

    try:
        stdin = convert_input_for_cpp(input_data) if language == "cpp" else input_data
        token = submit_code(full_code, language_id, stdin)
        result = get_submission_result(token)

        output = result.get("stdout") or ""
        error = result.get("stderr") or result.get("compile_output") or ""
        return jsonify({
            "status": result["status"]["description"],
            "output": (output + error).strip() or "[No output]"
        }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@user_bp.route("/submit", methods=["POST"])
@login_required
def submit_code_all_tests():
    data = request.get_json()
    user_code = data.get("code", "")
    language = data.get("language", "").lower()
    slug = data.get("slug")

    language_id = LANGUAGE_MAP.get(language)
    if not user_code or not language_id or not slug:
        return jsonify({"message": "All fields are required"}), 400

    problem = Problem.query.filter_by(slug=slug).first_or_404()
    driver_code = getattr(problem, f"{language}_driver_code", "")
    full_code = f"{user_code.strip()}\n\n{driver_code}"
    test_cases = TestCase.query.filter_by(problem_id=problem.id).all()

    results, passed_count = [], 0

    for tc in test_cases:
        try:
            stdin = convert_input_for_cpp(tc.input_data) if language == "cpp" else tc.input_data
            token = submit_code(full_code, language_id, stdin)
            result = get_submission_result(token)

            output = result.get("stdout") or ""
            error = result.get("stderr") or result.get("compile_output") or ""
            actual = (output + error).strip() or "[No output]"
            expected = (tc.expected_output or "").strip()
            passed = normalize_output(actual) == normalize_output(expected)

            if passed:
                passed_count += 1

            results.append({
                "input": tc.input_data,
                "expected": expected,
                "actual": actual,
                "passed": passed,
                "status": result["status"]["description"]
            })
        except Exception as e:
            results.append({
                "input": tc.input_data,
                "expected": tc.expected_output,
                "actual": f"Error: {str(e)}",
                "passed": False,
                "status": "Judge0 Error"
            })

    return jsonify({
        "results": results,
        "total": len(results),
        "passed": passed_count
    }), 200


@user_bp.route("/debug", methods=["POST"])
def debug_code():
    data = request.get_json()
    code = data.get("code", "")
    prompt = f"""
You are a helpful debugging assistant. Analyze the following code thoroughly for logic, syntax, or runtime errors.

Respond with:
1. 🔍 Key Issues Found
2. 🛠 Suggested Fixes
3. ✅ Final Fixed Version (if applicable)

Code:
```python
{code}
```
"""
    ai_response = get_llm_response(prompt)
    return jsonify({"status": "success", "message": ai_response})

@user_bp.route("/optimize", methods=["POST"])
def optimize_code():
    data = request.get_json()
    code = data.get("code", "")
    prompt = f"Optimize the following code for performance. Suggest improvements and share final optimized code:\n\n```python\n{code}\n```"
    ai_response = get_llm_response(prompt)
    return jsonify({"status": "success", "message": ai_response})

@user_bp.route("/explain", methods=["POST"])
def explain_code():
    data = request.get_json()
    code = data.get("code", "")
    prompt = (
        f"Explain this code clearly using the structure:\n\n"
        f"1. 🔹 Topic involved\n"
        f"2. 🔍 Brute-force approach\n"
        f"3. ⚙ Optimal approach\n"
        f"4. 🧠 Dry-run on a sample input\n\n"
        f"Code:\n```python\n{code}\n```"
    )
    ai_response = get_llm_response(prompt)
    return jsonify({"status": "success", "message": ai_response})

@user_bp.route("/admin/debug_starters")
def debug_starters():
    problems = Problem.query.all()
    missing = []
    for p in problems:
        for lang in LANGUAGE_MAP:
            starter = getattr(p, f"{lang}_starter_code", None)
            driver = getattr(p, f"{lang}_driver_code", None)
            if not starter or not driver:
                missing.append({
                    "slug": p.slug,
                    "title": p.title,
                    "language": lang,
                    "starter_code": bool(starter),
                    "driver_code": bool(driver)
                })
    return jsonify(missing)




