"""Security classification for submitted Python source code."""

from __future__ import annotations

import ast


def classify_source(source: str) -> str:
    """
    Classify source code based on potentially dangerous operations.

    Returns one of:

    - safe
    - filesystem
    - network
    - process
    - environment
    - dynamic_import
    - dangerous_builtin
    - multiple
    - none
    """

    if not source or not source.strip():
        return "none"

    try:
        tree = ast.parse(source)
    except SyntaxError:
        # Syntax errors are handled separately by the compiler.
        return "none"

    categories: set[str] = set()

    for node in ast.walk(tree):
        # Filesystem access
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in {
                    "open",
                    "input",
                }:
                    categories.add("filesystem")

                if node.func.id in {
                    "exec",
                    "eval",
                    "compile",
                    "__import__",
                }:
                    categories.add("dangerous_builtin")

                if node.func.id in {
                    "breakpoint",
                }:
                    categories.add("process")

            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    module_name = node.func.value.id
                    function_name = node.func.attr

                    # Filesystem-related modules and methods
                    if module_name in {
                        "os",
                        "pathlib",
                        "shutil",
                        "tempfile",
                    }:
                        categories.add("filesystem")

                    # Network-related modules and methods
                    if module_name in {
                        "socket",
                        "requests",
                        "urllib",
                        "http",
                        "ftplib",
                        "telnetlib",
                    }:
                        categories.add("network")

                    # Process execution
                    if module_name in {
                        "subprocess",
                        "multiprocessing",
                    }:
                        categories.add("process")

                    if module_name == "os" and function_name in {
                        "system",
                        "popen",
                        "spawn",
                        "spawnl",
                        "spawnle",
                        "spawnlp",
                        "spawnlpe",
                        "spawnv",
                        "spawnve",
                        "spawnvp",
                        "spawnvpe",
                        "execv",
                        "execve",
                        "execvp",
                        "execvpe",
                    }:
                        categories.add("process")

                    if module_name == "os" and function_name in {
                        "getenv",
                        "putenv",
                        "environ",
                    }:
                        categories.add("environment")

        # Imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_module = alias.name.split(".")[0]

                if root_module in {
                    "os",
                    "pathlib",
                    "shutil",
                    "tempfile",
                }:
                    categories.add("filesystem")

                if root_module in {
                    "socket",
                    "requests",
                    "urllib",
                    "http",
                    "ftplib",
                    "telnetlib",
                }:
                    categories.add("network")

                if root_module in {
                    "subprocess",
                    "multiprocessing",
                }:
                    categories.add("process")

                if root_module in {
                    "importlib",
                }:
                    categories.add("dynamic_import")

                if root_module in {
                    "sys",
                    "platform",
                }:
                    categories.add("environment")

        if isinstance(node, ast.ImportFrom):
            module_name = node.module or ""
            root_module = module_name.split(".")[0]

            if root_module in {
                "os",
                "pathlib",
                "shutil",
                "tempfile",
            }:
                categories.add("filesystem")

            if root_module in {
                "socket",
                "requests",
                "urllib",
                "http",
                "ftplib",
                "telnetlib",
            }:
                categories.add("network")

            if root_module in {
                "subprocess",
                "multiprocessing",
            }:
                categories.add("process")

            if root_module in {
                "importlib",
            }:
                categories.add("dynamic_import")

            if root_module in {
                "sys",
                "platform",
            }:
                categories.add("environment")

        # Dynamic import calls
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id == "__import__":
                    categories.add("dynamic_import")

            if isinstance(node.func, ast.Attribute):
                if node.func.attr in {
                    "import_module",
                    "reload",
                }:
                    categories.add("dynamic_import")

    if not categories:
        return "safe"

    if len(categories) == 1:
        return next(iter(categories))

    return "multiple"