import subprocess

class TestRunner:

    def __init__(self, project, bug_number,
                 work_dir=None,
                 container="ghrb_framework"):
        self.project    = project
        self.bug_number = bug_number
        self.container  = container
        self.work_dir   = (
            work_dir or
            f"/root/framework/testing_{project}_{bug_number}"
        )

    def _run_in_docker(self, command):
        full_command = [
            "docker", "exec",
            self.container,
            "/bin/bash", "-c",
            command
        ]
        result = subprocess.run(
            full_command,
            capture_output = True,
            text           = True,
            timeout        = 120
        )
        return result

    def checkout(self, version):
        self._run_in_docker(f"mkdir -p {self.work_dir}")
        version_id = f"{self.bug_number}{version}"
        command = (
            f"cd /root/framework && "
            f"./cli.py checkout -p {self.project} "
            f"-v {version_id} -w {self.work_dir}"
        )
        result  = self._run_in_docker(command)
        success = "Check out program version" in result.stdout
        print(f"    Checkout {version_id}: "
              f"{'OK' if success else 'FAILED'}")
        return success

    def compile(self):
        command = (
            f"cd /root/framework && "
            f"./cli.py compile -w {self.work_dir}"
        )
        result  = self._run_in_docker(command)
        success = "Build Success" in result.stdout
        print(f"    Compile: {'OK' if success else 'FAILED'}")
        return success

    def run_test(self):
        command = (
            f"cd /root/framework && "
            f"./cli.py test -w {self.work_dir}"
        )
        result  = self._run_in_docker(command)
        output  = result.stdout + result.stderr
        has_failure = (
            "Failure" in output or
            "ERROR"   in output or
            "FAIL"    in output
        )
        has_success = "Test Success" in output
        passed      = has_success and not has_failure
        print(f"    Test: {'PASSED' if passed else 'FAILED'}")
        return {"passed": passed, "output": output}

    def run_full_check(self):
        print(f"\n  Checking: {self.project} bug {self.bug_number}")

        print("  [Buggy version]")
        if not self.checkout("b"):
            return self._error_result("Buggy checkout failed")
        if not self.compile():
            return self._error_result("Buggy compile failed")
        buggy_test = self.run_test()

        print("  [Fixed version]")
        if not self.checkout("f"):
            return self._error_result("Fixed checkout failed")
        if not self.compile():
            return self._error_result("Fixed compile failed")
        fixed_test = self.run_test()

        return {
            "compiled":       True,
            "catches_bug":    not buggy_test["passed"],
            "passes_fixed":   fixed_test["passed"],
            "accurate":       (not buggy_test["passed"]) and
                               fixed_test["passed"],
            "false_positive": buggy_test["passed"],
            "false_negative": not fixed_test["passed"],
            "buggy_output":   buggy_test["output"],
            "fixed_output":   fixed_test["output"],
        }

    def _error_result(self, reason):
        print(f"  ERROR: {reason}")
        return {
            "compiled":       False,
            "catches_bug":    False,
            "passes_fixed":   False,
            "accurate":       False,
            "false_positive": False,
            "false_negative": False,
            "buggy_output":   reason,
            "fixed_output":   reason,
        }
