from openai import OpenAI
from config.settings import OPENAI_API_KEY, MODEL, TEMPERATURE, MAX_TOKENS

# Connect to OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

class OracleGenerator:
    """
    Sends code context to GPT-4O and receives
    a generated test oracle (assertion) back.
    """

    def generate(self, context_level, context_data):
        """
        context_level: "L1", "L2", "L3", "L4", "L5", or "L6"
        context_data:  dictionary containing the code strings
        Returns: the LLM's response as a string
        """
        prompt   = self._build_prompt(context_level, context_data)
        response = client.chat.completions.create(
            model       = MODEL,
            temperature = TEMPERATURE,
            max_tokens  = MAX_TOKENS,
            messages    = [
                {
                    "role":    "system",
                    "content": (
                        "You are an expert Java software tester. "
                        "Generate ONLY the Java assertion lines for the test. "
                        "No explanations, no markdown, no extra code."
                    )
                },
                {
                    "role":    "user",
                    "content": prompt
                }
            ]
        )
        return response.choices[0].message.content

    def _build_prompt(self, level, data):
        """Builds the right prompt for each context level"""

        # This is the base prompt every level starts with
        base = f"""
Here is a Java test method. The oracle (assertion) has been removed.
Please generate the correct assertion to replace [ORACLE REMOVED].

TEST METHOD:
{data['test_prefix']}
"""
        # Each level adds more information on top of the base
        if level == "L1":
            return base

        elif level == "L2":
            return base + f"""
THE METHOD BEING TESTED:
{data['mut']}
"""
        elif level == "L3":
            return base + f"""
THE FULL CLASS BEING TESTED:
{data['cut']}
"""
        elif level == "L4":
            return base + f"""
THE FULL TEST FILE (all tests in the same class):
{data['full_test_file']}
"""
        elif level == "L5":
            return base + f"""
THE FULL CLASS BEING TESTED:
{data['cut']}

RELATED CLASSES THIS CODE DEPENDS ON:
{data['dependencies']}
"""
        elif level == "L6":
            return base + f"""
THE FULL CLASS BEING TESTED:
{data['cut']}

API DOCUMENTATION (Javadoc comments):
{data['javadoc']}
"""
        return base