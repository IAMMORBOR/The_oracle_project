class Evaluator:
    """
    Measures the quality of a generated oracle.

    A GOOD oracle should:
    ✅ Compile successfully
    ✅ FAIL on the buggy version  (it catches the bug)
    ✅ PASS on the fixed version  (it does not raise false alarms)

    A BAD oracle either:
    ❌ Does not compile at all
    ❌ Misses the bug (false positive — passes on buggy code)
    ❌ Breaks on correct code (false negative — fails on fixed code)
    """

    def evaluate(self, buggy_result, fixed_result):

        compiled     = (buggy_result["compiled"] and
                        fixed_result["compiled"])

        # Did it catch the bug? (Should FAIL on buggy)
        catches_bug  = (buggy_result["compiled"] and
                        not buggy_result["passed"])

        # Does it pass on correct code? (Should PASS on fixed)
        passes_fixed = (fixed_result["compiled"] and
                        fixed_result["passed"])

        # ACCURATE = catches bug AND passes on correct code
        accurate     = catches_bug and passes_fixed

        # FALSE POSITIVE = passes on buggy (missed the bug)
        false_positive = (buggy_result["compiled"] and
                          buggy_result["passed"])

        # FALSE NEGATIVE = fails on correct code
        false_negative = (fixed_result["compiled"] and
                          not fixed_result["passed"])

        return {
            "compiled":       compiled,
            "catches_bug":    catches_bug,
            "passes_fixed":   passes_fixed,
            "accurate":       accurate,
            "false_positive": false_positive,
            "false_negative": false_negative,
        }