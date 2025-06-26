# test_judge0.py
from judge0_api import submit_code, get_submission_result

token = submit_code("print('Hello, world!')", language_id=71)  # Python 3
result = get_submission_result(token)

print("Output:", result["stdout"])
print("Time:", result["time"])
print("Memory:", result["memory"])
