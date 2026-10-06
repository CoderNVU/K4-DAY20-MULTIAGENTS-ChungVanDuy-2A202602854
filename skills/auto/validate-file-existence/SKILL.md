---
name: validate-file-existence
description: Use when ensuring that required files exist before executing tasks that depend on them.
---
# Validate File Existence

1. Identify all files required for the task execution.
2. Before running the task, check if each required file exists in the specified directory.
3. If any file is missing, log an error message and halt execution.
4. Provide a clear list of missing files to assist in troubleshooting.
5. Ensure that the file paths are correctly specified and accessible.