import ast
import unittest
from pathlib import Path
from typing import cast


class TestAgroGeeApiPortfolio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[1]
        cls.page_path = cls.repo_root / "pages" / "agro_gee_api.py"
        cls.st_pages_path = cls.repo_root / "st_pages.py"
        cls.st_pages_text = ""
        cls.st_pages_ast = None
        cls.st_pages_syntax_error = None

        if cls.st_pages_path.exists():
            cls.st_pages_text = cls.st_pages_path.read_text(encoding="utf-8")
            try:
                cls.st_pages_ast = ast.parse(cls.st_pages_text)
            except SyntaxError as exc:
                cls.st_pages_syntax_error = exc

    @staticmethod
    def _is_st_attr(node, attr_name):
        return (
            isinstance(node, ast.Attribute)
            and node.attr == attr_name
            and isinstance(node.value, ast.Name)
            and node.value.id == "st"
        )

    @staticmethod
    def _constant_str(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None

    @staticmethod
    def _extract_target_names(assign_node):
        names = []
        targets = []

        if isinstance(assign_node, ast.Assign):
            targets = assign_node.targets
        elif isinstance(assign_node, ast.AnnAssign):
            targets = [assign_node.target]

        for target in targets:
            if isinstance(target, ast.Name):
                names.append(target.id)
            elif isinstance(target, (ast.Tuple, ast.List)):
                for element in target.elts:
                    if isinstance(element, ast.Name):
                        names.append(element.id)

        return names

    def _require_st_pages_ast(self):
        self.assertTrue(self.st_pages_path.exists(), "Expected st_pages.py to exist.")

        if self.st_pages_syntax_error is not None:
            exc = self.st_pages_syntax_error
            self.fail(
                "st_pages.py has invalid Python syntax at "
                f"line {exc.lineno}, column {exc.offset}: {exc.msg}"
            )

        self.assertIsNotNone(self.st_pages_ast, "Expected st_pages.py to be parseable.")
        return cast(ast.Module, self.st_pages_ast)

    def _extract_page_registrations(self):
        module = self._require_st_pages_ast()
        registrations = {}

        for node in ast.walk(module):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue

            call = node.value
            if not isinstance(call, ast.Call) or not self._is_st_attr(
                call.func, "Page"
            ):
                continue
            if not call.args:
                continue

            page_path = self._constant_str(call.args[0])
            if page_path is None:
                continue

            target_names = self._extract_target_names(node)

            keywords = {
                kw.arg: self._constant_str(kw.value)
                for kw in call.keywords
                if kw.arg is not None
            }

            registrations[page_path] = {
                "vars": target_names,
                "title": keywords.get("title"),
                "icon": keywords.get("icon"),
            }

        return registrations

    def _extract_navigation_groups(self):
        module = self._require_st_pages_ast()
        groups = {}

        for node in ast.walk(module):
            if not isinstance(node, ast.Call) or not self._is_st_attr(
                node.func, "navigation"
            ):
                continue
            if not node.args or not isinstance(node.args[0], ast.Dict):
                continue

            nav_map = node.args[0]
            for key_node, value_node in zip(nav_map.keys, nav_map.values):
                label = self._constant_str(key_node)
                if label is None or not isinstance(value_node, ast.List):
                    continue

                entries = groups.setdefault(label, [])
                for item in value_node.elts:
                    if isinstance(item, ast.Name):
                        entries.append(("var", item.id))
                    elif (
                        isinstance(item, ast.Call)
                        and self._is_st_attr(item.func, "Page")
                        and item.args
                    ):
                        inline_path = self._constant_str(item.args[0])
                        if inline_path is not None:
                            entries.append(("path", inline_path))

        return groups

    @staticmethod
    def _extract_streamlit_markdown_strings(module):
        chunks = []

        for node in ast.walk(module):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Attribute):
                continue
            if node.func.attr not in {"markdown", "write"}:
                continue
            if not isinstance(node.func.value, ast.Name) or node.func.value.id != "st":
                continue
            if not node.args:
                continue

            text = TestAgroGeeApiPortfolio._constant_str(node.args[0])
            if text is not None:
                chunks.append(text)

        return chunks

    def test_agro_gee_api_page_exists(self):
        self.assertTrue(
            self.page_path.exists(), "Expected pages/agro_gee_api.py to exist."
        )

    def test_agro_gee_api_page_contains_required_content(self):
        if not self.page_path.exists():
            self.skipTest("Agro GEE API page is not present yet.")

        page_text = self.page_path.read_text(encoding="utf-8")
        page_ast = ast.parse(page_text)
        markdown_chunks = self._extract_streamlit_markdown_strings(page_ast)
        combined = "\n".join(markdown_chunks).lower()

        self.assertIn("agro gee api", combined)
        self.assertIn("stack", combined)
        self.assertIn("objetiv", combined)
        self.assertIn("github.com/bsensix/agro", combined)

    def test_st_pages_registers_agro_gee_api_page_with_title_and_icon(self):
        registrations = self._extract_page_registrations()
        agro = registrations.get("pages/agro_gee_api.py")

        self.assertIsNotNone(
            agro, "Expected st_pages.py to register pages/agro_gee_api.py."
        )
        if agro is None:
            return

        self.assertIsInstance(agro["title"], str)
        self.assertIn("agro gee api", agro["title"].lower())
        self.assertIsInstance(agro["icon"], str)
        self.assertTrue(
            agro["icon"].strip(), "Expected non-empty icon for Agro GEE API."
        )

    def test_engineering_group_includes_nba_and_agro_pages(self):
        registrations = self._extract_page_registrations()
        groups = self._extract_navigation_groups()

        nba = registrations.get("pages/nba_database.py")
        agro = registrations.get("pages/agro_gee_api.py")

        self.assertIsNotNone(nba, "Expected NBA page registration in st_pages.py.")
        self.assertIsNotNone(
            agro, "Expected Agro GEE API page registration in st_pages.py."
        )
        if nba is None or agro is None:
            return

        engineering_entries = []
        for label, entries in groups.items():
            if "engenharia de dados" in label.lower():
                engineering_entries.extend(entries)

        self.assertTrue(
            engineering_entries, "Expected Engenharia de Dados group in navigation."
        )

        entry_set = set(engineering_entries)
        nba_vars = nba.get("vars", [])
        agro_vars = agro.get("vars", [])

        nba_in_group = ("path", "pages/nba_database.py") in entry_set or any(
            ("var", var_name) in entry_set for var_name in nba_vars
        )
        agro_in_group = ("path", "pages/agro_gee_api.py") in entry_set or any(
            ("var", var_name) in entry_set for var_name in agro_vars
        )

        self.assertTrue(nba_in_group, "Expected NBA page in Engenharia de Dados group.")
        self.assertTrue(
            agro_in_group, "Expected Agro GEE API page in Engenharia de Dados group."
        )


if __name__ == "__main__":
    unittest.main()
