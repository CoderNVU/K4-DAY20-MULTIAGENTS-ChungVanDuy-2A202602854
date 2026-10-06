"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use when exploring the codebase or workspace, reading documentation, schemas, logs, "
                "or finding files. Do not modify any files; only inspect and report findings."
            ),
            "system_prompt": (
                "You are an exploration subagent. Inspect files, directories, docstrings, schema, and sample data. "
                "Report precise factual observations and do not edit or delete any files."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use when making code modifications, applying bug fixes, cleaning data, or writing tests. "
                "Execute necessary shell commands and report changes made."
            ),
            "system_prompt": (
                "You are an implementation subagent. Make precise code edits, generate output files, "
                "run tests to verify your implementation, and report the modified files and test results."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use when reviewing implementation results, running automated test suites, verifying output schemas, "
                "or checking edge cases. Do not edit files; report verification status."
            ),
            "system_prompt": (
                "You are a reviewer subagent. Inspect diffs, execute tests, verify outputs against specifications, "
                "and report any discrepancies, failures, or pass status without modifying workspace files."
            ),
        },
    ]
