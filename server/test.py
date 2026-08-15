#!/usr/bin/env python3
import os
import re
import ast
from pathlib import Path

def is_snake_case(name: str) -> bool:
    """
    判断字符串是否符合 snake_case 规范：
    - 只包含小写字母、数字和下划线
    - 必须以小写字母开头
    - 不能以下划线结尾，不能有连续下划线
    """
    pattern = r'^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$'
    return bool(re.fullmatch(pattern, name))

class IdentifierCollector(ast.NodeVisitor):
    """AST 访问器，收集所有可能标识符及其行号"""

    def __init__(self):
        self.results = []  # 元素为 (行号, 名称)

    def visit_Name(self, node):
        self.results.append((node.lineno, node.id))
        self.generic_visit(node)

    def visit_Attribute(self, node):
        self.results.append((node.lineno, node.attr))
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.results.append((node.lineno, node.name))
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.results.append((node.lineno, node.name))
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.results.append((node.lineno, node.name))
        self.generic_visit(node)

    def visit_arg(self, node):
        self.results.append((node.lineno, node.arg))
        self.generic_visit(node)

    def visit_Dict(self, node):
        # 字典字面量的 key（仅字符串常量）
        for key in node.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                self.results.append((key.lineno, key.value))
        self.generic_visit(node)

    def visit_Subscript(self, node):
        # 下标访问中的字符串索引，如 d["name"] 或 s["index"]
        if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
            self.results.append((node.slice.lineno, node.slice.value))
        self.generic_visit(node)

def analyze_file(filepath: str) -> list:
    """分析单个 Python 文件，返回符合 snake_case 的标识符列表"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        tree = ast.parse(code, filename=filepath)
    except (SyntaxError, UnicodeDecodeError):
        # 忽略语法错误或编码问题
        return []

    collector = IdentifierCollector()
    collector.visit(tree)

    # 仅保留 snake_case 的名称
    return [(line, name) for line, name in collector.results if is_snake_case(name)]

ignore = ["remote_addr", "task_done", "exc_traceback", "exc_type", "exc_value", "format_exception", "current_thread", "row_factory", "current_app", "static_folder", "send_from_directory", "generate_password_hash", "check_password_hash", "register_blueprnt", "import_name",
            "status_code", "token_urlsafe", "parse_args", "ensure_ascii", "json_provider_class",
            "before_request", "after_request", "new_option", "delete_option",  "get_json",
            "new_choice", "delete_choice", "east_asian_width", "teardown_appcontext",
            "register_blueprint", "delete_choice", "flask_route", "content_length",
            "add_argument", 
          ]

def main():
    root = os.getcwd()
    for dirpath, dirnames, filenames in os.walk(root):
        # 跳过 .venv 目录（避免进入该子目录）
        if '.venv' in dirnames:
            dirnames.remove('.venv')

        for filename in filenames:
            if filename.endswith('.py') and filename != 'test.py':
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root)
                findings = analyze_file(full_path)
                for line, name in findings:
                    if '_'  in name and name not in ignore:
                        print(f"{rel_path}:{line}: {name}")

if __name__ == '__main__':
    main()