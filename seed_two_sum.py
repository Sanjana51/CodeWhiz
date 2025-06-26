from app import app, db
from models import Problem, TestCase

with app.app_context():
    problem = Problem(
        title="Two Sum",
        slug="two-sum",
        description="""
Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.

Example 1:

Input: nums = [2,7,11,15], target = 9  
Output: [0,1]

Example 2:

Input: nums = [3,2,4], target = 6  
Output: [1,2]

Example 3:

Input: nums = [3,3], target = 6  
Output: [0,1]
""",
        difficulty="Easy",
        topic_tags=["Array", "Hash Table"],
        function_signature="def two_sum(nums, target):",
        starter_code="def two_sum(nums, target):\n    # your code here\n    pass",
        driver_code="""
import sys, json
params = json.loads(sys.stdin.read())
nums, target = params
print(two_sum(nums, target))
"""
    )

    db.session.add(problem)
    db.session.commit()

    # Add test cases
    test_cases = [
        TestCase(input_data='[[2,7,11,15], 9]', expected_output='[0, 1]', problem_id=problem.id),
        TestCase(input_data='[[3,2,4], 6]', expected_output='[1, 2]', problem_id=problem.id),
        TestCase(input_data='[[3,3], 6]', expected_output='[0, 1]', problem_id=problem.id)
    ]

    db.session.add_all(test_cases)
    db.session.commit()

    print("✅ Problem and test cases added successfully.")

