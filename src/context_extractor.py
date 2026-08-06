# import os

# class ContextExtractor:
#     """
#     This class reads Java files and extracts different
#     amounts of code (context levels L1 through L6).
#     """

#     def __init__(self, bug):
#         # bug is a dictionary with file paths
#         self.bug = bug

#     # ── LEVEL 1: Just the test, oracle removed ────────────────────────
#     def get_test_prefix(self):
#         code = self._read_file(self.bug["test_file"])
#         return self._remove_assertions(code)

#     # ── LEVEL 2: Test + the specific method being tested ─────────────
#     def get_prefix_plus_mut(self):
#         prefix = self.get_test_prefix()
#         method = self._extract_method(
#             self.bug["source_file"],
#             self.bug["method_name"]
#         )
#         return prefix, method

#     # ── LEVEL 3: Test + the full class ───────────────────────────────
#     def get_prefix_plus_cut(self):
#         prefix = self.get_test_prefix()
#         cut    = self._read_file(self.bug["source_file"])
#         return prefix, cut

#     # ── LEVEL 4 (NEW): Test + the full test file ─────────────────────
#     def get_prefix_plus_full_test_file(self):
#         prefix         = self.get_test_prefix()
#         full_test_file = self._read_file(self.bug["test_file"])
#         return prefix, full_test_file

#     # ── LEVEL 5 (NEW): Test + class + related dependencies ───────────
#     def get_prefix_plus_dependencies(self):
#         prefix = self.get_test_prefix()
#         cut    = self._read_file(self.bug["source_file"])
#         deps   = self._extract_dependencies(self.bug["source_file"])
#         return prefix, cut, deps

#     # ── LEVEL 6 (NEW): Test + class + Javadoc comments ───────────────
#     def get_prefix_plus_javadoc(self):
#         prefix  = self.get_test_prefix()
#         cut     = self._read_file(self.bug["source_file"])
#         javadoc = self._extract_javadoc(self.bug["source_file"])
#         return prefix, cut, javadoc

#     # ── Helper: read a file ───────────────────────────────────────────
#     def _read_file(self, path):
#         with open(path, "r", encoding="utf-8") as f:
#             return f.read()

#     # ── Helper: remove assert lines ───────────────────────────────────
#     def _remove_assertions(self, code):
#         lines  = code.split("\n")
#         result = []
#         for line in lines:
#             if "assert" in line.lower():
#                 # Replace the oracle with a placeholder comment
#                 result.append("        // [ORACLE REMOVED]")
#             else:
#                 result.append(line)
#         return "\n".join(result)

#     # ── Helper: extract one method from a Java file ───────────────────
#     def _extract_method(self, file_path, method_name):
#         code   = self._read_file(file_path)
#         lines  = code.split("\n")
#         result = []
#         inside = False
#         depth  = 0
#         for line in lines:
#             if method_name in line and "(" in line:
#                 inside = True
#             if inside:
#                 result.append(line)
#                 depth += line.count("{") - line.count("}")
#                 if depth <= 0 and len(result) > 1:
#                     break
#         return "\n".join(result)

#     # ── Helper: find and read imported project classes ─────────────────
#     def _extract_dependencies(self, source_file):
#         code    = self._read_file(source_file)
#         imports = [
#             line.strip()
#             for line in code.split("\n")
#             if line.strip().startswith("import")
#         ]
#         dep_code = []
#         base_dir = os.path.dirname(source_file)
#         for imp in imports:
#             class_name = imp.split(".")[-1].replace(";", "")
#             dep_path   = os.path.join(base_dir, class_name + ".java")
#             if os.path.exists(dep_path):
#                 dep_code.append(self._read_file(dep_path))
#         return "\n\n".join(dep_code) if dep_code else "No local dependencies found."

#     # ── Helper: extract Javadoc comment blocks ─────────────────────────
#     def _extract_javadoc(self, source_file):
#         code    = self._read_file(source_file)
#         lines   = code.split("\n")
#         javadoc = []
#         inside  = False
#         for line in lines:
#             if "/**" in line:
#                 inside = True
#             if inside:
#                 javadoc.append(line)
#             if "*/" in line and inside:
#                 inside = False
#         return "\n".join(javadoc) if javadoc else "No Javadoc found."


import subprocess

class ContextExtractor:
    """
    Extracts different levels of code context
    from the GHRB dataset using Docker.

    Instead of reading files directly, it runs
    Docker commands to get the code.
    """

    def __init__(self, bug):
        """
        bug: dictionary with keys:
             id, project, bug_number
        """
        self.project    = bug["project"]
        self.bug_number = bug["bug_number"]
        self.container  = "ghrb_framework"
        self.work_dir   = "/root/framework/testing"

    def _run_in_docker(self, command):
        """Send a command to Docker and get the output back"""
        result = subprocess.run(
            ["docker", "exec", self.container,
             "/bin/bash", "-c", command],
            capture_output = True,
            text           = True,
            timeout        = 120
        )
        return result.stdout + result.stderr

    def _checkout_buggy(self):
        """Checkout the buggy version to read the files"""
        version_id = f"{self.bug_number}b"
        command = (
            f"cd /root/framework && "
            f"./cli.py checkout -p {self.project} "
            f"-v {version_id} -w {self.work_dir}"
        )
        self._run_in_docker(command)

    def _read_file_from_docker(self, file_path):
        """Read a file from inside Docker"""
        command = f"cat {file_path}"
        return self._run_in_docker(command)

    def _find_test_file(self):
        """Find the test file path inside the checked out project"""
        command = (
            f"find {self.work_dir} -name '*.java' "
            f"-path '*/test/*' | head -5"
        )
        output = self._run_in_docker(command)
        files  = [
            line.strip()
            for line in output.strip().split("\n")
            if line.strip().endswith(".java")
        ]
        return files[0] if files else None

    def _find_source_file(self):
        """Find the main source file inside the checked out project"""
        command = (
            f"find {self.work_dir} -name '*.java' "
            f"-path '*/main/*' | head -5"
        )
        output = self._run_in_docker(command)
        files  = [
            line.strip()
            for line in output.strip().split("\n")
            if line.strip().endswith(".java")
        ]
        return files[0] if files else None

    def _remove_assertions(self, code):
        """Remove assert lines and replace with placeholder"""
        lines  = code.split("\n")
        result = []
        for line in lines:
            if "assert" in line.lower():
                result.append("        // [ORACLE REMOVED]")
            else:
                result.append(line)
        return "\n".join(result)

    def _extract_method(self, code, method_name):
        """Pull out a single method from a Java file"""
        lines  = code.split("\n")
        result = []
        inside = False
        depth  = 0
        for line in lines:
            if method_name in line and "(" in line:
                inside = True
            if inside:
                result.append(line)
                depth += line.count("{") - line.count("}")
                if depth <= 0 and len(result) > 1:
                    break
        return "\n".join(result) if result else code[:500]

    def _extract_javadoc(self, code):
        """Pull out all Javadoc comment blocks"""
        lines   = code.split("\n")
        javadoc = []
        inside  = False
        for line in lines:
            if "/**" in line:
                inside = True
            if inside:
                javadoc.append(line)
            if "*/" in line and inside:
                inside = False
        return (
            "\n".join(javadoc)
            if javadoc
            else "No Javadoc found."
        )

    # ── Public methods — one per context level ────────────────────────

    def get_test_prefix(self):
        """Level 1 — just the test, oracle removed"""
        self._checkout_buggy()
        test_file = self._find_test_file()
        if not test_file:
            return "// Could not find test file"
        code = self._read_file_from_docker(test_file)
        return self._remove_assertions(code)

    def get_prefix_plus_mut(self):
        """Level 2 — test prefix + the specific method"""
        self._checkout_buggy()
        test_file   = self._find_test_file()
        source_file = self._find_source_file()
        if not test_file:
            return "// No test file", "// No source file"
        test_code   = self._read_file_from_docker(test_file)
        prefix      = self._remove_assertions(test_code)
        source_code = self._read_file_from_docker(source_file) if source_file else ""
        method      = self._extract_method(source_code, "public")
        return prefix, method

    def get_prefix_plus_cut(self):
        """Level 3 — test prefix + full class"""
        self._checkout_buggy()
        test_file   = self._find_test_file()
        source_file = self._find_source_file()
        if not test_file:
            return "// No test file", "// No source file"
        test_code   = self._read_file_from_docker(test_file)
        prefix      = self._remove_assertions(test_code)
        cut         = self._read_file_from_docker(source_file) if source_file else ""
        return prefix, cut

    def get_prefix_plus_full_test_file(self):
        """Level 4 (NEW) — test prefix + all tests in the file"""
        self._checkout_buggy()
        test_file = self._find_test_file()
        if not test_file:
            return "// No test file", "// No test file"
        test_code      = self._read_file_from_docker(test_file)
        prefix         = self._remove_assertions(test_code)
        full_test_file = test_code  # full file unchanged
        return prefix, full_test_file

    def get_prefix_plus_dependencies(self):
        """Level 5 (NEW) — test prefix + class + dependencies"""
        self._checkout_buggy()
        test_file   = self._find_test_file()
        source_file = self._find_source_file()
        if not test_file:
            return "// No test file", "// No source", "// No deps"
        test_code   = self._read_file_from_docker(test_file)
        prefix      = self._remove_assertions(test_code)
        cut         = self._read_file_from_docker(source_file) if source_file else ""

        # Find other java files in same directory as dependencies
        if source_file:
            source_dir = "/".join(source_file.split("/")[:-1])
            command    = f"find {source_dir} -name '*.java' | head -3"
            dep_files  = self._run_in_docker(command).strip().split("\n")
            deps       = "\n\n".join([
                self._read_file_from_docker(f.strip())
                for f in dep_files
                if f.strip() and f.strip() != source_file
            ])
        else:
            deps = "No dependencies found."

        return prefix, cut, deps

    def get_prefix_plus_javadoc(self):
        """Level 6 (NEW) — test prefix + class + Javadoc"""
        self._checkout_buggy()
        test_file   = self._find_test_file()
        source_file = self._find_source_file()
        if not test_file:
            return "// No test file", "// No source", "// No javadoc"
        test_code   = self._read_file_from_docker(test_file)
        prefix      = self._remove_assertions(test_code)
        cut         = self._read_file_from_docker(source_file) if source_file else ""
        javadoc     = self._extract_javadoc(cut)
        return prefix, cut, javadoc