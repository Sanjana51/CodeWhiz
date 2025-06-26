# update_two_sum.py
from app import app, db
from models import Problem

with app.app_context():
    problem = Problem.query.filter_by(slug="two-sum").first()

    if problem:
        # === Function Signatures ===
        problem.python_function_signature = ""
        problem.cpp_function_signature = ""

        # Clear unused language fields
        problem.java_function_signature = None
        problem.javascript_function_signature = None
        problem.c_function_signature = None

        # === Starter Code ===
        problem.python_starter_code = """from typing import List

def twoSum(nums: List[int], target: int) -> List[int]:
    # Write your logic here
    pass
"""

        problem.cpp_starter_code = """#include <iostream>
#include <vector>
#include <unordered_map>
using namespace std;

vector<int> twoSum(vector<int>& nums, int target) {
    // Write your logic here
    return {};
}
"""

        # Clear unused starter code fields
        problem.java_starter_code = None
        problem.javascript_starter_code = None
        problem.c_starter_code = None

        # === Driver Code ===
        problem.python_driver_code = """import sys
import json
from typing import List

def main():
    input_data = sys.stdin.read()
    nums, target = json.loads(input_data)
    result = twoSum(nums, target)
    print(" ".join(map(str, result)))

if __name__ == "__main__":
    main()
"""

        problem.cpp_driver_code = """#include <iostream>
#include <vector>
#include <unordered_map>
using namespace std;

// assume function is implemented above

int main() {
    int n;
    cin >> n;
    vector<int> nums(n);
    for (int i = 0; i < n; ++i) cin >> nums[i];
    int target;
    cin >> target;
    vector<int> res = twoSum(nums, target);
    for (int x : res) cout << x << " ";
    return 0;
}
"""

        # Clear unused driver code fields
        problem.java_driver_code = None
        problem.javascript_driver_code = None
        problem.c_driver_code = None

        db.session.commit()
        print("✅ Two Sum problem updated successfully.")
    else:
        print("❌ Problem not found.")
