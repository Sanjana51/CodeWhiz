# add_next_permutation.py

from app import app, db
from models import Problem, TestCase
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

with app.app_context():
    problem = Problem(
        title="Next Permutation",
        slug="next-permutation",
        description="""
<p>A permutation of an array of integers is an arrangement of its members into a sequence or linear order.</p>

<p>For example, for <code>arr = [1,2,3]</code>, the following are all the permutations of <code>arr</code>:<br>
<code>[1,2,3]</code>, <code>[1,3,2]</code>, <code>[2,1,3]</code>, <code>[2,3,1]</code>, <code>[3,1,2]</code>, <code>[3,2,1]</code>.</p>

<p>The <strong>next permutation</strong> of an array of integers is the next lexicographically greater permutation.<br>
If such arrangement is not possible, rearrange it as the <strong>lowest possible order</strong> (sorted in ascending order).</p>

<p><b>The replacement must be in-place and use only constant extra memory.</b></p>

<h4>Example 1:</h4>
<pre><strong>Input:</strong> nums = [1,2,3]
<strong>Output:</strong> [1,3,2]</pre>

<h4>Example 2:</h4>
<pre><strong>Input:</strong> nums = [3,2,1]
<strong>Output:</strong> [1,2,3]</pre>

<h4>Example 3:</h4>
<pre><strong>Input:</strong> nums = [1,1,5]
<strong>Output:</strong> [1,5,1]</pre>

<h4>Constraints:</h4>
<ul>
<li>1 &le; nums.length &le; 100</li>
<li>0 &le; nums[i] &le; 100</li>
</ul>
""",
        difficulty="Medium",
        topic_tags=["Array", "Two Pointers"],
        python_function_signature="",
        cpp_function_signature="",
        python_starter_code="""from typing import List

def nextPermutation(nums: List[int]) -> None:
    # Modify nums in-place to the next permutation
    pass
""",
        cpp_starter_code="""#include <vector>
using namespace std;

void nextPermutation(vector<int>& nums) {
    // Modify nums in-place to the next permutation
}
""",
        python_driver_code="""import sys
import json
from typing import List

def main():
    input_data = sys.stdin.read()
    nums = json.loads(input_data)
    nextPermutation(nums)
    print(json.dumps(nums))

if __name__ == "__main__":
    main()
""",
        cpp_driver_code="""#include <iostream>
#include <vector>
using namespace std;

// assume nextPermutation is implemented above

int main() {
    int n;
    cin >> n;
    vector<int> nums(n);
    for (int i = 0; i < n; ++i) {
        cin >> nums[i];
    }

    nextPermutation(nums);

    for (int x : nums) cout << x << " ";
    return 0;
}
"""
    )

    db.session.add(problem)
    db.session.commit()

    test_cases = [
        TestCase(input_data='[1,2,3]', expected_output='[1,3,2]', problem_id=problem.id),
        TestCase(input_data='[3,2,1]', expected_output='[1,2,3]', problem_id=problem.id),
        TestCase(input_data='[1,1,5]', expected_output='[1,5,1]', problem_id=problem.id),
    ]

    db.session.add_all(test_cases)
    db.session.commit()

    print("✅ Next Permutation problem added successfully.")

