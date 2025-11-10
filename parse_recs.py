import re
import json

def parse_recommendations(response_text: str) -> str:
    """
    Extracts and returns the <result> JSON block from LLM output as a JSON string.
    If invalid or missing, returns a minimal valid JSON structure.
    """


    result_match = re.search(r"<result>([\s\S]*?)</result>", response_text, re.IGNORECASE)
    if not result_match:
        return json.dumps({"recommended_assessments": []}, indent=2)

    result_content = result_match.group(1).strip()


    result_content = re.sub(r"^```(?:json)?|```$", "", result_content.strip(), flags=re.MULTILINE).strip()


    try:
        parsed = json.loads(result_content)

        if not isinstance(parsed, dict) or "recommended_assessments" not in parsed:
            parsed = {"recommended_assessments": []}

        return json.dumps(parsed, indent=2)

    except json.JSONDecodeError:

        cleaned = re.sub(r"[\x00-\x1f]", "", result_content)
        try:
            parsed = json.loads(cleaned)
            return json.dumps(parsed, indent=2)
        except Exception:
            return json.dumps({"recommended_assessments": []}, indent=2)
