---
name: enforce-test-immutability
description: Use when modifying test files to ensure original test files remain unchanged.
---
# Enforce Test Immutability

1. Review the test files to identify any modifications made during the task.
2. Ensure that no original test files are altered; only create new test files for changes.
3. Implement a check to compare original test files with modified versions.
4. If any original test files are found to be modified, log an error and revert changes.
5. Document the changes made in new test files for clarity.