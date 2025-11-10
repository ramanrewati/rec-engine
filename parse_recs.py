import re
import json

def parse_recommendations(response_text):



    result_match = re.search(r'<result>([\s\S]*?)</result>', response_text)
    if not result_match:
        return {"recommended_assessments": []}
    
    result_content = result_match.group(1).strip()

    try:
        parsed_json = json.loads(result_content)

        if "recommended_assessments" in parsed_json and isinstance(parsed_json["recommended_assessments"], list):
            return parsed_json
        else:
            return {"recommended_assessments": []}
    except json.JSONDecodeError:
        return {"recommended_assessments": []}
