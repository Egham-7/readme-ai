from typing import List, Dict, Type
from abc import ABC, abstractmethod
import ast
import re
import json
from dataclasses import dataclass


@dataclass
class AnalysisResult:
    """Structure for storing analysis results"""

    imports: List[str]
    classes: List[str]
    functions: List[str]
    main_purpose: str
    dependencies: List[str]
    complexity_score: int
    documentation_score: int


class FileAnalyzer(ABC):
    @abstractmethod
    def analyze(self, content: str, file_path: str) -> str:
        pass

    def _calculate_complexity_score(self, content: str) -> int:
        # Basic complexity scoring based on length and structure
        lines = content.split("\n")
        score = len(lines) // 10  # Base score from length
        score += content.count("if ") + content.count("for ") + content.count("while ")
        return min(10, score)  # Cap at 10

    def _calculate_documentation_score(self, content: str) -> int:
        # Score based on comments and docstrings
        comment_lines = len(
            [line for line in content.split("\n") if line.strip().startswith("#")]
        )
        docstring_count = content.count('"""') + content.count("'''")
        return min(10, (comment_lines + docstring_count) // 2)


class PythonAnalyzer(FileAnalyzer):
    def analyze(self, content: str, file_path: str) -> str:
        """Main analysis orchestrator that combines all analysis components."""
        try:
            tree = ast.parse(content)
            analysis_data = self._collect_analysis_data(tree, content, file_path)
            return self._format_analysis_report(analysis_data)
        except SyntaxError:
            return f"Error: Invalid Python syntax in {file_path}"

    def _get_return_annotation(self, node: ast.FunctionDef) -> str:
        """Extract return type annotation from a function definition."""
        if node.returns:
            return ast.unparse(node.returns)
        return "None"

    def _get_arg_type_hints(self, node: ast.FunctionDef) -> Dict[str, str]:
        """Extract type hints from function arguments."""
        hints = {}
        for arg in node.args.args:
            if arg.annotation:
                hints[arg.arg] = ast.unparse(arg.annotation)
        return hints

    def _find_usage_count(self, tree: ast.AST, name: str) -> int:
        """Count how many times a given name is used in the AST."""
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == name:
                count += 1
        return count

    def _collect_analysis_data(
        self, tree: ast.AST, content: str, file_path: str
    ) -> Dict:
        """Collects all analysis data into a structured format."""
        return {
            "file_path": file_path,
            "imports": self._extract_imports(tree),
            "classes": self._extract_classes(tree),
            "functions": self._extract_functions(tree),
            "complexity": self._calculate_complexity_score(content),
            "doc_score": self._calculate_documentation_score(content),
            "main_purpose": self._determine_main_purpose(tree),
            "dependencies": self._analyze_dependencies(tree),
            "type_hints": self._extract_type_hints(tree),
        }

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extracts and categorizes all imports from the code."""
        imports: List[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(n.name for n in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(f"{node.module}.{node.names[0].name}")
        return sorted(imports)

    def _extract_classes(self, tree: ast.AST) -> List[Dict]:
        """Extracts classes with their methods and docstrings."""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [
                    {
                        "name": n.name,
                        "docstring": ast.get_docstring(n),
                        "args": [arg.arg for arg in n.args.args if arg.arg != "self"],
                    }
                    for n in node.body
                    if isinstance(n, ast.FunctionDef)
                ]
                classes.append(
                    {
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "methods": methods,
                    }
                )
        return classes

    def _extract_functions(self, tree: ast.AST) -> List[Dict]:
        """Extracts standalone functions with their signatures and docstrings."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(
                    {
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "args": [arg.arg for arg in node.args.args],
                        "returns": self._get_return_annotation(node),
                    }
                )
        return functions

    def _extract_type_hints(self, tree: ast.AST) -> List[Dict]:
        """Extracts type hints from functions and class methods."""
        type_hints = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                hints = {
                    "function": node.name,
                    "args": self._get_arg_type_hints(node),
                    "return": self._get_return_annotation(node),
                }
                type_hints.append(hints)
        return type_hints

    def _analyze_dependencies(self, tree: ast.AST) -> Dict:
        """Analyzes external package dependencies and their usage."""
        dependencies = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for name in node.names:
                    dependencies[name.name] = self._find_usage_count(tree, name.name)
        return dependencies

    def _determine_main_purpose(self, tree: ast.AST) -> str:
        """Determines the main purpose of the module based on its contents."""
        class_count = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
        func_count = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])

        purpose = "Module containing "
        components = []

        if class_count:
            components.append(f"{class_count} classes")
        if func_count:
            components.append(f"{func_count} functions")

        return purpose + " and ".join(components)

    def _format_analysis_report(self, data: Dict) -> str:
        """Formats the analysis data into a structured report for LLM consumption."""
        report = [
            f"Python File Analysis for {data['file_path']}:",
            "\nImports:",
            "\n".join(f"- {imp}" for imp in data["imports"]),
            "\nClasses:",
            "\n".join(
                f"- {cls['name']}: {cls['docstring'] or 'No docstring'}"
                for cls in data["classes"]
            ),
            "\nFunctions:",
            "\n".join(
                f"- {func['name']}: {func['docstring'] or 'No docstring'}"
                for func in data["functions"]
            ),
            f"\nMain Purpose: {data['main_purpose']}",
            f"Complexity Score: {data['complexity']}/10",
            f"Documentation Score: {data['doc_score']}/10",
            "\nType Hints Coverage:",
            "\n".join(
                f"- {hint['function']}: {len(hint['args'])} args typed"
                for hint in data["type_hints"]
            ),
        ]
        return "\n".join(report)


class JavaScriptAnalyzer(FileAnalyzer):
    def analyze(self, content: str, file_path: str) -> str:
        analysis_data = self._collect_analysis_data(content)
        return self._format_analysis_report(analysis_data, file_path)

    def _collect_analysis_data(self, content: str) -> Dict:
        return {
            "imports": self._extract_imports(content),
            "classes": self._extract_classes(content),
            "functions": self._extract_functions(content),
            "exports": self._extract_exports(content),
            "complexity": self._calculate_complexity_score(content),
            "doc_score": self._calculate_documentation_score(content),
        }

    def _extract_imports(self, content: str) -> List[str]:
        patterns = {
            "es6_import": r'import\s+(?:{[^}]+}|\*\s+as\s+\w+|\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',
            "require": r'(?:const|let|var)\s+(?:{[^}]+}|\w+)\s*=\s*require\([\'"]([^\'"]+)[\'"]\)',
            "dynamic_import": r'import\([\'"]([^\'"]+)[\'"]\)',
        }

        imports = []
        for _, pattern in patterns.items():
            matches = re.finditer(pattern, content)
            imports.extend([match.group(1) for match in matches])
        return imports

    def _extract_classes(self, content: str) -> List[Dict]:
        class_pattern = r"class\s+(\w+)(?:\s+extends\s+(\w+))?\s*{([^}]+)}"
        classes = []

        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            parent_class = match.group(2)
            class_body = match.group(3)

            methods = self._extract_class_methods(class_body)
            classes.append(
                {"name": class_name, "extends": parent_class, "methods": methods}
            )
        return classes

    def _extract_class_methods(self, class_body: str) -> List[str]:
        method_patterns = [
            r"(\w+)\s*\([^)]*\)\s*{",  # Regular methods
            r"get\s+(\w+)\s*\(",  # Getters
            r"set\s+(\w+)\s*\(",  # Setters
            r"static\s+(\w+)\s*\(",  # Static methods
        ]

        methods = []
        for pattern in method_patterns:
            methods.extend(re.findall(pattern, class_body))
        return methods

    def _extract_functions(self, content: str) -> Dict[str, List[str]]:
        patterns = {
            "named_functions": r"function\s+(\w+)\s*\([^)]*\)",
            "arrow_functions": r"(?:const|let|var)\s+(\w+)\s*=\s*(?:\([^)]*\)|[^=]+)\s*=>\s*[{]?",
            "methods": r"(\w+)\s*:\s*function\s*\([^)]*\)",
            "async_functions": r"async\s+function\s+(\w+)\s*\([^)]*\)",
        }

        functions: Dict[str, List[str]] = {category: [] for category in patterns.keys()}
        for category, pattern in patterns.items():
            functions[category] = re.findall(pattern, content)
        return functions

    def _extract_exports(self, content: str) -> List[str]:
        patterns = [
            r"module\.exports\s*=\s*({[^}]+})",
            r"export\s+(?:default\s+)?(?:class|function|const|let|var)\s+(\w+)",
            r"export\s*{([^}]+)}",
        ]

        exports = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            exports.extend(matches)
        return exports

    def _format_analysis_report(self, data: Dict, file_path: str) -> str:
        total_functions = sum(len(funcs) for funcs in data["functions"].values())

        report = [
            f"JavaScript File Analysis for {file_path}:",
            f"\nImports ({len(data['imports'])}):",
            "- " + "\n- ".join(data["imports"]),
            f"\nClasses ({len(data['classes'])}):",
            "- "
            + "\n- ".join(
                f"{cls['name']}"
                + (
                    f" extends {cls['extends']
                                }"
                    if cls["extends"]
                    else ""
                )
                for cls in data["classes"]
            ),
            f"\nFunctions ({total_functions}):",
        ]

        for category, funcs in data["functions"].items():
            if funcs:
                report.extend(
                    [
                        f"\n{category.replace('_', ' ').title()}:",
                        "- " + "\n- ".join(funcs),
                    ]
                )

        report.extend(
            [
                f"\nExports ({len(data['exports'])}):",
                "- " + "\n- ".join(data["exports"]),
                f"\nComplexity Score: {data['complexity']}/10",
                f"Documentation Score: {data['doc_score']}/10",
            ]
        )

        return "\n".join(report)


class JupyterNotebookAnalyzer(FileAnalyzer):
    def analyze(self, content: str, file_path: str) -> str:
        try:
            notebook = json.loads(content)
            cells = notebook.get("cells", [])

            code_cells = [c for c in cells if c["cell_type"] == "code"]
            markdown_cells = [c for c in cells if c["cell_type"] == "markdown"]

            # Analyze code cells
            total_code_lines = sum(
                len(c.get("source", "").split("\n")) for c in code_cells
            )

            # Analyze imports in code cells
            imports = []
            for cell in code_cells:
                source = cell.get("source", "")
                if isinstance(source, list):
                    source = "".join(source)
                import_lines = [
                    line
                    for line in source.split("\n")
                    if "import" in line or "from" in line
                ]
                imports.extend(import_lines)

            analysis = f"Jupyter Notebook Analysis for {file_path}:\n"
            analysis += f"Total Cells: {len(cells)}\n"
            analysis += f"Code Cells: {len(code_cells)}\n"
            analysis += f"Markdown Cells: {len(markdown_cells)}\n"
            analysis += f"Total Code Lines: {total_code_lines}\n\n"
            analysis += "Imports Found:\n- " + "\n- ".join(imports) + "\n"

            return analysis

        except json.JSONDecodeError:
            return f"Error: Invalid notebook format in {file_path}"


class TextFileAnalyzer(FileAnalyzer):
    def analyze(self, content: str, file_path: str) -> str:
        lines = content.split("\n")
        words = content.split()

        # Basic text analysis
        avg_line_length = sum(len(line) for line in lines) / len(lines) if lines else 0

        # Identify potential structured content
        list_items = len(
            [line for line in lines if line.strip().startswith(("-", "*", "1.", "•"))]
        )
        code_blocks = content.count("```") // 2

        analysis = f"Text File Analysis for {file_path}:\n"
        analysis += f"Total Lines: {len(lines)}\n"
        analysis += f"Total Words: {len(words)}\n"
        analysis += f"Average Line Length: {avg_line_length:.2f} characters\n"
        analysis += f"List Items Found: {list_items}\n"
        analysis += f"Code Blocks Found: {code_blocks}\n"

        # Identify file type hints
        if file_path.endswith((".md", ".markdown")):
            analysis += "\nMarkdown Features:\n"
            analysis += f"Headers: {
                len([line for line in lines if line.strip().startswith('#')])}\n"
            analysis += f"Links: {
                len(re.findall(r'\[.*?\]\(.*?\)', content))}\n"

        return analysis


class RustAnalyzer(FileAnalyzer):
    def analyze(self, content: str, file_path: str) -> str:
        analysis_data = self._collect_analysis_data(content)
        return self._format_analysis_report(analysis_data, file_path)

    def _collect_analysis_data(self, content: str) -> Dict:
        return {
            "uses": self._extract_use_statements(content),
            "structs": self._extract_structs(content),
            "impls": self._extract_impls(content),
            "functions": self._extract_functions(content),
            "traits": self._extract_traits(content),
            "macros": self._extract_macros(content),
            "safety_analysis": self._analyze_safety(content),
            "memory_patterns": self._analyze_memory_patterns(content),
            "generics": self._extract_generics(content),
            "complexity": self._calculate_complexity_score(content),
            "doc_score": self._calculate_doc_score(content),
        }

    def _extract_use_statements(self, content: str) -> List[Dict]:
        pattern = r"use\s+([^;]+);"
        uses = []
        for match in re.finditer(pattern, content):
            path = match.group(1)
            uses.append(
                {
                    "path": path,
                    "is_external": not path.startswith("crate::"),
                    "is_prelude": path.startswith("std::prelude"),
                }
            )
        return uses

    def _extract_structs(self, content: str) -> List[Dict]:
        pattern = r"(?:#\[derive\(([^)]+)\)])?\s*struct\s+(\w+)(?:<([^>]+)>)?([^;{]+)?"
        structs = []
        for match in re.finditer(pattern, content):
            derives = match.group(1).split(",") if match.group(1) else []
            structs.append(
                {
                    "name": match.group(2),
                    "derives": [d.strip() for d in derives],
                    "generics": match.group(3),
                    "fields": (
                        self._parse_struct_fields(match.group(4))
                        if match.group(4)
                        else []
                    ),
                }
            )
        return structs

    def _extract_impls(self, content: str) -> List[Dict]:
        pattern = r"impl(?:<([^>]+)>)?\s+(?:([^{]+)\s+for\s+)?(\w+)(?:<[^>]+>)?"
        impls = []
        for match in re.finditer(pattern, content):
            impls.append(
                {
                    "generics": match.group(1),
                    "trait": match.group(2),
                    "type": match.group(3),
                }
            )
        return impls

    def _extract_functions(self, content: str) -> List[Dict]:
        pattern = (
            r"(?:pub\s+)?fn\s+(\w+)(?:<([^>]+)>)?\s*\(([^)]*)\)(?:\s*->\s*([^{]+))?"
        )
        functions = []
        for match in re.finditer(pattern, content):
            functions.append(
                {
                    "name": match.group(1),
                    "generics": match.group(2),
                    "params": self._parse_function_params(match.group(3)),
                    "return_type": match.group(4).strip() if match.group(4) else None,
                }
            )
        return functions

    def _extract_traits(self, content: str) -> List[Dict]:
        pattern = r"trait\s+(\w+)(?:<([^>]+)>)?(?:\s*:\s*([^{]+))?"
        traits = []
        for match in re.finditer(pattern, content):
            traits.append(
                {
                    "name": match.group(1),
                    "generics": match.group(2),
                    "supertraits": (
                        [t.strip() for t in match.group(3).split("+")]
                        if match.group(3)
                        else []
                    ),
                }
            )
        return traits

    def _analyze_safety(self, content: str) -> Dict:
        return {
            "unsafe_blocks": len(re.findall(r"unsafe\s*{", content)),
            "unsafe_functions": len(re.findall(r"unsafe\s+fn", content)),
            "unsafe_traits": len(re.findall(r"unsafe\s+trait", content)),
        }

    def _analyze_memory_patterns(self, content: str) -> Dict:
        return {
            "rc_usage": len(re.findall(r"Rc<", content)),
            "arc_usage": len(re.findall(r"Arc<", content)),
            "box_usage": len(re.findall(r"Box<", content)),
            "raw_pointers": len(re.findall(r"\*(?:const|mut)", content)),
        }

    def _extract_generics(self, content: str) -> List[Dict]:
        pattern = r"<([^>]+)>\s*(?:where\s+([^{]+))?"
        generics = []
        for match in re.finditer(pattern, content):
            generics.append(
                {
                    "params": match.group(1).split(","),
                    "where_clause": match.group(2) if match.group(2) else None,
                }
            )
        return generics

    def _calculate_doc_score(self, content: str) -> int:
        doc_comments = len(re.findall(r"///|//!", content))
        items_count = (
            len(self._extract_structs(content))
            + len(self._extract_functions(content))
            + len(self._extract_traits(content))
        )
        return min(10, int((doc_comments / max(1, items_count)) * 10))

    def _format_analysis_report(self, data: Dict, file_path: str) -> str:
        report_sections = [
            f"Rust File Analysis for {file_path}:",
            self._format_uses_section(data["uses"]),
            self._format_structs_section(data["structs"]),
            self._format_impls_section(data["impls"]),
            self._format_functions_section(data["functions"]),
            self._format_traits_section(data["traits"]),
            self._format_safety_section(data["safety_analysis"]),
            self._format_memory_section(data["memory_patterns"]),
            f"Complexity Score: {data['complexity']}/10",
            f"Documentation Score: {data['doc_score']}/10",
        ]
        return "\n\n".join(report_sections)

    def _extract_macros(self, content: str) -> List[Dict]:
        pattern = r"macro_rules!\s+(\w+)\s*{([^}]*)}"
        macros = []
        for match in re.finditer(pattern, content):
            macros.append({"name": match.group(1), "rules": match.group(2).strip()})
        return macros

    def _parse_struct_fields(self, fields_str: str) -> List[Dict]:
        field_pattern = r"(?:pub\s+)?(\w+):\s*([^,]+)"
        fields = []
        for match in re.finditer(field_pattern, fields_str):
            fields.append({"name": match.group(1), "type": match.group(2).strip()})
        return fields

    def _parse_function_params(self, params_str: str) -> List[Dict]:
        if not params_str.strip():
            return []
        param_pattern = r"(\w+):\s*([^,]+)"
        params = []
        for match in re.finditer(param_pattern, params_str):
            params.append({"name": match.group(1), "type": match.group(2).strip()})
        return params

    def _format_uses_section(self, uses: List[Dict]) -> str:
        lines = [f"Use Statements ({len(uses)}):"]
        for use in uses:
            prefix = "external" if use["is_external"] else "internal"
            lines.append(f"- [{prefix}] {use['path']}")
        return "\n".join(lines)

    def _format_structs_section(self, structs: List[Dict]) -> str:
        lines = [f"Structs ({len(structs)}):"]
        for struct in structs:
            derives = (
                f" #[derive({', '.join(
                    struct['derives'])})]"
                if struct["derives"]
                else ""
            )
            lines.append(f"- {struct['name']}{derives}")
        return "\n".join(lines)

    def _format_impls_section(self, impls: List[Dict]) -> str:
        lines = [f"Implementations ({len(impls)}):"]
        for impl in impls:
            trait_info = f" {impl['trait']} for" if impl["trait"] else ""
            lines.append(f"- impl{trait_info} {impl['type']}")
        return "\n".join(lines)

    def _format_functions_section(self, functions: List[Dict]) -> str:
        lines = [f"Functions ({len(functions)}):"]
        for func in functions:
            return_info = (
                f" -> {func['return_type']
                       }"
                if func["return_type"]
                else ""
            )
            lines.append(f"- {func['name']}{return_info}")
        return "\n".join(lines)

    def _format_traits_section(self, traits: List[Dict]) -> str:
        lines = [f"Traits ({len(traits)}):"]
        for trait in traits:
            supertrait_info = (
                f": {
                    ' + '.join(trait['supertraits'])}"
                if trait["supertraits"]
                else ""
            )
            lines.append(f"- {trait['name']}{supertrait_info}")
        return "\n".join(lines)

    def _format_safety_section(self, safety: Dict) -> str:
        return (
            f"Safety Analysis:\n"
            f"- Unsafe Blocks: {safety['unsafe_blocks']}\n"
            f"- Unsafe Functions: {safety['unsafe_functions']}\n"
            f"- Unsafe Traits: {safety['unsafe_traits']}"
        )

    def _format_memory_section(self, memory: Dict) -> str:
        return (
            f"Memory Management:\n"
            f"- Rc Usage: {memory['rc_usage']}\n"
            f"- Arc Usage: {memory['arc_usage']}\n"
            f"- Box Usage: {memory['box_usage']}\n"
            f"- Raw Pointers: {memory['raw_pointers']}"
        )


class GoAnalyzer(FileAnalyzer):
    def analyze(self, content: str, file_path: str) -> str:
        analysis_data = self._collect_analysis_data(content)
        return self._format_analysis_report(analysis_data, file_path)

    def _collect_analysis_data(self, content: str) -> Dict:
        return {
            "package": self._extract_package(content),
            "imports": self._extract_imports(content),
            "structs": self._extract_structs(content),
            "interfaces": self._extract_interfaces(content),
            "functions": self._extract_functions(content),
            "methods": self._extract_methods(content),
            "concurrency": self._analyze_concurrency(content),
            "error_handling": self._analyze_error_handling(content),
            "testing": self._analyze_testing(content),
            "complexity": self._calculate_complexity_score(content),
            "doc_score": self._calculate_doc_score(content),
        }

    def _extract_package(self, content: str) -> str:
        pattern = r"package\s+(\w+)"
        match = re.search(pattern, content)
        return match.group(1) if match else "unknown"

    def _extract_imports(self, content: str) -> List[Dict]:
        single_import = r'import\s+"([^"]+)"'
        multi_import = r"import\s+\((.*?)\)"

        imports = []

        # Process single imports
        for match in re.finditer(single_import, content):
            imports.append(
                {
                    "path": match.group(1),
                    "alias": None,
                    "is_stdlib": "." not in match.group(1),
                }
            )

        # Process multi-line imports
        for block in re.finditer(multi_import, content, re.DOTALL):
            for line in block.group(1).strip().split("\n"):
                if line.strip():
                    parts = line.strip().strip('"').split()
                    if len(parts) > 1:
                        imports.append(
                            {
                                "path": parts[1].strip('"'),
                                "alias": parts[0],
                                "is_stdlib": "." not in parts[1],
                            }
                        )
                    else:
                        imports.append(
                            {
                                "path": parts[0].strip('"'),
                                "alias": None,
                                "is_stdlib": "." not in parts[0],
                            }
                        )
        return imports

    def _extract_structs(self, content: str) -> List[Dict]:
        pattern = r"type\s+(\w+)\s+struct\s*{([^}]*)}"
        structs = []
        for match in re.finditer(pattern, content):
            structs.append(
                {
                    "name": match.group(1),
                    "fields": self._parse_struct_fields(match.group(2)),
                    "has_json_tags": bool(re.search(r'`json:"', match.group(2))),
                }
            )
        return structs

    def _parse_struct_fields(self, fields_str: str) -> List[Dict]:
        field_pattern = r"(\w+)\s+(\*?\w+(?:\[\])?(?:\.\w+)?)\s*(?:`[^`]*`)?"
        return [
            {
                "name": match.group(1),
                "type": match.group(2),
                "is_pointer": match.group(2).startswith("*"),
            }
            for match in re.finditer(field_pattern, fields_str)
        ]

    def _extract_interfaces(self, content: str) -> List[Dict]:
        pattern = r"type\s+(\w+)\s+interface\s*{([^}]*)}"
        interfaces = []
        for match in re.finditer(pattern, content):
            interfaces.append(
                {
                    "name": match.group(1),
                    "methods": self._parse_interface_methods(match.group(2)),
                }
            )
        return interfaces

    def _parse_interface_methods(self, methods_str: str) -> List[Dict]:
        method_pattern = r"(\w+)\([^)]*\)(?:\s*\([^)]*\))?"
        return [{"name": m.group(1)} for m in re.finditer(method_pattern, methods_str)]

    def _extract_functions(self, content: str) -> List[Dict]:
        pattern = r"func\s+(\w+)\s*\((.*?)\)(?:\s*\((.*?)\))?\s*{"
        return [
            {
                "name": match.group(1),
                "params": self._parse_function_params(match.group(2)),
                "returns": (
                    self._parse_function_returns(match.group(3))
                    if match.group(3)
                    else None
                ),
            }
            for match in re.finditer(pattern, content)
        ]

    def _analyze_concurrency(self, content: str) -> Dict:
        return {
            "goroutines": len(re.findall(r"go\s+\w+", content)),
            "channels": len(re.findall(r"(?:make\s*\(\s*)?chan\s+\w+", content)),
            "select_blocks": len(re.findall(r"\bselect\s*{", content)),
            "mutexes": len(re.findall(r"sync\.Mutex", content)),
        }

    def _analyze_error_handling(self, content: str) -> Dict:
        return {
            "error_checks": len(re.findall(r"if\s+err\s*!=\s*nil", content)),
            "error_returns": len(re.findall(r"return\s+.*?err", content)),
            "custom_errors": len(re.findall(r"errors\.New|fmt\.Errorf", content)),
        }

    def _analyze_testing(self, content: str) -> Dict:
        return {
            "test_functions": len(re.findall(r"func\s+Test\w+\s*\(", content)),
            "benchmark_functions": len(
                re.findall(r"func\s+Benchmark\w+\s*\(", content)
            ),
            "test_tables": len(re.findall(r"table\s*:=\s*\[\]struct", content)),
        }

    def _calculate_doc_score(self, content: str) -> int:
        doc_comments = len(re.findall(r"//\s*\w+|/\*\s*\w+", content))
        exported_items = len(re.findall(r"func\s+[A-Z]|\btype\s+[A-Z]", content))
        return min(10, int((doc_comments / max(1, exported_items)) * 10))

    def _format_analysis_report(self, data: Dict, file_path: str) -> str:
        sections = [
            f"Go File Analysis for {file_path}:",
            f"Package: {data['package']}",
            self._format_imports_section(data["imports"]),
            self._format_structs_section(data["structs"]),
            self._format_interfaces_section(data["interfaces"]),
            self._format_functions_section(data["functions"]),
            self._format_concurrency_section(data["concurrency"]),
            self._format_error_section(data["error_handling"]),
            self._format_testing_section(data["testing"]),
            f"Complexity Score: {data['complexity']}/10",
            f"Documentation Score: {data['doc_score']}/10",
        ]
        return "\n\n".join(sections)

    def _extract_methods(self, content: str) -> List[Dict]:
        pattern = (
            r"func\s+\((\w+)\s+\*?(\w+)\)\s+(\w+)\s*\((.*?)\)(?:\s*\((.*?)\))?\s*{"
        )
        methods = []
        for match in re.finditer(pattern, content):
            methods.append(
                {
                    "receiver_name": match.group(1),
                    "receiver_type": match.group(2),
                    "name": match.group(3),
                    "params": self._parse_function_params(match.group(4)),
                    "returns": (
                        self._parse_function_returns(match.group(5))
                        if match.group(5)
                        else None
                    ),
                }
            )
        return methods

    def _parse_function_params(self, params_str: str) -> List[Dict]:
        if not params_str.strip():
            return []
        params = []
        for param in params_str.split(","):
            param = param.strip()
            if param:
                parts = param.split()
                params.append(
                    {
                        "name": parts[0],
                        "type": parts[1] if len(parts) > 1 else parts[0],
                        "is_variadic": "..." in param,
                    }
                )
        return params

    def _parse_function_returns(self, returns_str: str) -> List[str]:
        return [r.strip() for r in returns_str.split(",") if r.strip()]

    def _format_imports_section(self, imports: List[Dict]) -> str:
        lines = [f"Imports ({len(imports)}):"]
        for imp in imports:
            alias = f" as {imp['alias']}" if imp["alias"] else ""
            stdlib = " (stdlib)" if imp["is_stdlib"] else ""
            lines.append(f"- {imp['path']}{alias}{stdlib}")
        return "\n".join(lines)

    def _format_structs_section(self, structs: List[Dict]) -> str:
        lines = [f"Structs ({len(structs)}):"]
        for struct in structs:
            json_info = " (with JSON tags)" if struct["has_json_tags"] else ""
            fields = [
                f"  - {f['name']}: {f['type']
                                    }"
                for f in struct["fields"]
            ]
            lines.append(f"- {struct['name']}{json_info}")
            lines.extend(fields)
        return "\n".join(lines)

    def _format_interfaces_section(self, interfaces: List[Dict]) -> str:
        lines = [f"Interfaces ({len(interfaces)}):"]
        for interface in interfaces:
            methods = [f"  - {m['name']}" for m in interface["methods"]]
            lines.append(f"- {interface['name']}")
            lines.extend(methods)
        return "\n".join(lines)

    def _format_functions_section(self, functions: List[Dict]) -> str:
        lines = [f"Functions ({len(functions)}):"]
        for func in functions:
            params = ", ".join(f"{p['name']}: {p['type']}" for p in func["params"])
            returns = (
                f" -> {', '.join(func['returns'])
                       }"
                if func["returns"]
                else ""
            )
            lines.append(f"- {func['name']}({params}){returns}")
        return "\n".join(lines)

    def _format_concurrency_section(self, concurrency: Dict) -> str:
        return (
            f"Concurrency Patterns:\n"
            f"- Goroutines: {concurrency['goroutines']}\n"
            f"- Channels: {concurrency['channels']}\n"
            f"- Select Blocks: {concurrency['select_blocks']}\n"
            f"- Mutex Usage: {concurrency['mutexes']}"
        )

    def _format_error_section(self, error_handling: Dict) -> str:
        return (
            f"Error Handling:\n"
            f"- Error Checks: {error_handling['error_checks']}\n"
            f"- Error Returns: {error_handling['error_returns']}\n"
            f"- Custom Errors: {error_handling['custom_errors']}"
        )

    def _format_testing_section(self, testing: Dict) -> str:
        return (
            f"Testing:\n"
            f"- Test Functions: {testing['test_functions']}\n"
            f"- Benchmark Functions: {testing['benchmark_functions']}\n"
            f"- Table-Driven Tests: {testing['test_tables']}"
        )


class CppAnalyzer(FileAnalyzer):
    def analyze(self, content: str, file_path: str) -> str:
        analysis_data = self._collect_analysis_data(content)
        return self._format_analysis_report(analysis_data, file_path)

    def _collect_analysis_data(self, content: str) -> Dict:
        return {
            "includes": self._extract_includes(content),
            "namespaces": self._extract_namespaces(content),
            "classes": self._extract_classes(content),
            "templates": self._extract_templates(content),
            "functions": self._extract_functions(content),
            "memory_management": self._analyze_memory_management(content),
            "oop_features": self._analyze_oop_features(content),
            "stl_usage": self._analyze_stl_usage(content),
            "modern_features": self._analyze_modern_features(content),
            "exception_handling": self._analyze_exception_handling(content),
            "complexity": self._calculate_complexity_score(content),
            "doc_score": self._calculate_doc_score(content),
        }

    def _extract_includes(self, content: str) -> List[Dict]:
        system_pattern = r"#include\s*<([^>]+)>"
        local_pattern = r'#include\s*"([^"]+)"'

        includes = []
        for match in re.finditer(system_pattern, content):
            includes.append(
                {
                    "path": match.group(1),
                    "type": "system",
                    "is_stl": self._is_stl_header(match.group(1)),
                }
            )
        for match in re.finditer(local_pattern, content):
            includes.append({"path": match.group(1), "type": "local", "is_stl": False})
        return includes

    def _extract_classes(self, content: str) -> List[Dict]:
        pattern = r"(?:class|struct)\s+(\w+)(?:\s*:\s*(?:public|private|protected)\s+(\w+))?(?:\s*{([^}]+)})?"
        classes = []
        for match in re.finditer(pattern, content):
            classes.append(
                {
                    "name": match.group(1),
                    "base_class": match.group(2),
                    "members": (
                        self._extract_class_members(match.group(3))
                        if match.group(3)
                        else []
                    ),
                    "is_struct": bool(re.match(r"\s*struct", match.group(0))),
                }
            )
        return classes

    def _extract_class_members(self, class_content: str) -> Dict:
        return {
            "methods": self._extract_methods(class_content),
            "fields": self._extract_fields(class_content),
            "access_specifiers": self._count_access_specifiers(class_content),
        }

    def _extract_methods(self, content: str) -> List[Dict]:
        pattern = r"(?:virtual\s+)?(?:const\s+)?(?:\w+\s+)+(\w+)\s*\([^)]*\)(?:\s*const)?(?:\s*=\s*0)?"
        methods = []
        for match in re.finditer(pattern, content):
            methods.append(
                {
                    "name": match.group(1),
                    "is_virtual": bool(re.search(r"virtual", match.group(0))),
                    "is_const": bool(re.search(r"const$", match.group(0))),
                    "is_pure_virtual": bool(re.search(r"=\s*0", match.group(0))),
                }
            )
        return methods

    def _analyze_memory_management(self, content: str) -> Dict:
        return {
            "new_ops": len(re.findall(r"\bnew\b", content)),
            "delete_ops": len(re.findall(r"\bdelete\b", content)),
            "smart_ptrs": {
                "unique_ptr": len(re.findall(r"unique_ptr", content)),
                "shared_ptr": len(re.findall(r"shared_ptr", content)),
                "weak_ptr": len(re.findall(r"weak_ptr", content)),
            },
            "raii_usage": self._analyze_raii_patterns(content),
        }

    def _analyze_modern_features(self, content: str) -> Dict:
        return {
            "auto": len(re.findall(r"\bauto\b", content)),
            "lambda": len(re.findall(r"\[\s*=?\s*\]", content)),
            "range_for": len(re.findall(r"for\s*\(\s*\w+\s*:\s*", content)),
            "nullptr": len(re.findall(r"\bnullptr\b", content)),
            "constexpr": len(re.findall(r"\bconstexpr\b", content)),
            "move_semantics": len(re.findall(r"std::move|&&", content)),
            "variadic_templates": len(
                re.findall(r"template\s*<\s*typename\s*\.\.\.\s*\w+\s*>", content)
            ),
        }

    def _analyze_stl_usage(self, content: str) -> Dict:
        containers = {
            "vector": len(re.findall(r"\bvector\s*<", content)),
            "map": len(re.findall(r"\bmap\s*<", content)),
            "set": len(re.findall(r"\bset\s*<", content)),
            "queue": len(re.findall(r"\bqueue\s*<", content)),
            "stack": len(re.findall(r"\bstack\s*<", content)),
            "list": len(re.findall(r"\blist\s*<", content)),
            "deque": len(re.findall(r"\bdeque\s*<", content)),
        }
        algorithms = len(
            re.findall(r"\b(?:find|sort|transform|copy|remove|replace)\b", content)
        )
        return {"containers": containers, "algorithms": algorithms}

    def _extract_namespaces(self, content: str) -> List[Dict]:
        pattern = r"namespace\s+(\w+)\s*{([^}]+)}"
        return [
            {"name": m.group(1), "content": m.group(2)}
            for m in re.finditer(pattern, content)
        ]

    def _extract_templates(self, content: str) -> List[Dict]:
        pattern = r"template\s*<([^>]+)>\s*(?:class|struct)\s+(\w+)"
        return [
            {"name": m.group(2), "params": m.group(1)}
            for m in re.finditer(pattern, content)
        ]

    def _extract_functions(self, content: str) -> List[Dict]:
        pattern = r"(?:\w+\s+)+(\w+)\s*\(([^)]*)\)\s*(?:const)?\s*{"
        return [
            {"name": m.group(1), "params": self._parse_params(m.group(2))}
            for m in re.finditer(pattern, content)
        ]

    def _analyze_oop_features(self, content: str) -> Dict:
        return {
            "constructors": len(re.findall(r"(\w+)\s*::\s*\1\s*\([^)]*\)", content)),
            "destructors": len(re.findall(r"~(\w+)\s*\([^)]*\)", content)),
            "virtual_methods": len(re.findall(r"virtual\s+\w+", content)),
            "abstract_methods": len(re.findall(r"=\s*0\s*;", content)),
        }

    def _analyze_exception_handling(self, content: str) -> Dict:
        return {
            "try_blocks": len(re.findall(r"\btry\b", content)),
            "catch_blocks": len(re.findall(r"\bcatch\b", content)),
            "throw_statements": len(re.findall(r"\bthrow\b", content)),
            "noexcept": len(re.findall(r"\bnoexcept\b", content)),
        }

    def _calculate_doc_score(self, content: str) -> int:
        doc_comments = len(re.findall(r"//[!/]<|/\*\*", content))
        total_items = len(re.findall(r"class|struct|function", content))
        return min(10, int((doc_comments / max(1, total_items)) * 10))

    def _is_stl_header(self, header: str) -> bool:
        stl_headers = {"vector", "map", "string", "iostream", "memory", "algorithm"}
        return header.strip("<>") in stl_headers

    def _extract_fields(self, content: str) -> List[Dict]:
        pattern = r"(?:private|protected|public)?\s*(\w+(?:<[^>]+>)?)\s+(\w+)\s*;"
        return [
            {"type": m.group(1), "name": m.group(2)}
            for m in re.finditer(pattern, content)
        ]

    def _count_access_specifiers(self, content: str) -> Dict:
        return {
            "public": len(re.findall(r"\bpublic:", content)),
            "private": len(re.findall(r"\bprivate:", content)),
            "protected": len(re.findall(r"\bprotected:", content)),
        }

    def _analyze_raii_patterns(self, content: str) -> Dict:
        return {
            "scope_guards": len(
                re.findall(r"unique_ptr|lock_guard|scoped_lock", content)
            ),
            "destructors": len(re.findall(r"~\w+\s*\(\)", content)),
        }

    def _format_includes_section(self, includes: List[Dict]) -> str:
        lines = [f"Includes ({len(includes)}):"]
        for inc in includes:
            inc_type = "STL" if inc["is_stl"] else inc["type"]
            lines.append(f"- {inc['path']} [{inc_type}]")
        return "\n".join(lines)

    def _format_classes_section(self, classes: List[Dict]) -> str:
        lines = [f"Classes/Structs ({len(classes)}):"]
        for cls in classes:
            inheritance = (
                f" : {cls['base_class']
                      }"
                if cls["base_class"]
                else ""
            )
            lines.append(f"- {cls['name']}{inheritance}")
        return "\n".join(lines)

    def _format_memory_section(self, memory: Dict) -> str:
        return (
            f"Memory Management:\n"
            f"- Raw: {memory['new_ops']
                      } new, {memory['delete_ops']} delete\n"
            f"- Smart Pointers: {sum(memory['smart_ptrs'].values())}\n"
            f"- RAII Usage: {memory['raii_usage']['scope_guards']} guards"
        )

    def _format_modern_features_section(self, features: Dict) -> str:
        lines = ["Modern C++ Features:"]
        for feature, count in features.items():
            lines.append(f"- {feature.replace('_', ' ').title()}: {count}")
        return "\n".join(lines)

    def _format_stl_section(self, stl: Dict) -> str:
        lines = ["STL Usage:"]
        for container, count in stl["containers"].items():
            lines.append(f"- {container}: {count}")
        lines.append(f"- Algorithm calls: {stl['algorithms']}")
        return "\n".join(lines)

    def _format_analysis_report(self, data: Dict, file_path: str) -> str:
        sections = [
            f"C++ File Analysis for {file_path}:",
            self._format_includes_section(data["includes"]),
            self._format_classes_section(data["classes"]),
            self._format_memory_section(data["memory_management"]),
            self._format_modern_features_section(data["modern_features"]),
            self._format_stl_section(data["stl_usage"]),
            f"Complexity Score: {data['complexity']}/10",
            f"Documentation Score: {data['doc_score']}/10",
        ]
        return "\n\n".join(sections)

    def _parse_params(self, params_str: str) -> List[Dict]:
        if not params_str.strip():
            return []

        params = []
        for param in params_str.split(","):
            param = param.strip()
            if param:
                # Handle reference and pointer parameters
                is_ref = "&" in param
                is_ptr = "*" in param
                # Split type and name, handling const and modifiers
                parts = param.replace("&", "").replace("*", "").split()
                if len(parts) >= 2:
                    params.append(
                        {
                            "type": " ".join(parts[:-1]),
                            "name": parts[-1],
                            "is_const": "const" in parts,
                            "is_reference": is_ref,
                            "is_pointer": is_ptr,
                        }
                    )
        return params


class AnalyzerFactory:
    _analyzers: Dict[str, Type[FileAnalyzer]] = {
        ".py": PythonAnalyzer,
        ".js": JavaScriptAnalyzer,
        ".ipynb": JupyterNotebookAnalyzer,
        ".rs": RustAnalyzer,
        ".go": GoAnalyzer,
        ".cpp": CppAnalyzer,
    }

    @classmethod
    def get_analyzer(cls, file_path: str) -> FileAnalyzer:
        extension = file_path.lower().split(".")[-1]
        extension = f".{extension}"
        analyzer_class = cls._analyzers.get(extension, TextFileAnalyzer)
        return analyzer_class()


def analyze_file(file_path: str, content: str) -> str:
    analyzer = AnalyzerFactory.get_analyzer(file_path)
    return analyzer.analyze(content, file_path)
