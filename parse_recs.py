import re

def parse_recommendations(response_text):
    """
    Parse the LLM's response into structured JSON with the following schema:
    {
        "recommended_assessments": [
            {
                "url": str,
                "name": str,
                "adaptive_support": str,
                "description": str,
                "duration": int,
                "remote_support": str,
                "test_type": [str]
            }
        ]
    }
    """

    # extract the <result> section
    result_match = re.search(r'<result>([\s\S]*?)</result>', response_text)
    if not result_match:
        return {"recommended_assessments": []}

    result_content = result_match.group(1).strip()
    lines = [line.strip() for line in result_content.splitlines() if line.strip()]
    if len(lines) < 3:
        return {"recommended_assessments": []}

    header = lines[0]
    separator = lines[1]
    data_rows = lines[2:]

    recommendations = []

    test_type_mapping = {
        "A": ["Ability & Aptitude"],
        "B": ["Biodata & Situational Judgement"],
        "C": ["Competencies"],
        "D": ["Development & 360"],
        "E": ["Assessment Exercises"],
        "K": ["Knowledge & Skills"],
        "P": ["Personality & Behaviour"],
        "S": ["Simulations"]
    }

    for row in data_rows:
        parts = [col.strip() for col in row.split("|") if col.strip()]
        if len(parts) < 7:
            continue

        
        name = parts[0]

        url_match = re.search(r'\((https?://[^\)]+)\)', parts[1])
        url = url_match.group(1) if url_match else ""

        remote_support = parts[2]
        adaptive_support = parts[3]

        duration_numbers = re.findall(r'\d+', parts[4])
        duration = int(duration_numbers[0]) if duration_numbers else 0

        test_type_shorthand = parts[5]
        test_type = []
        for code in test_type_shorthand.split(","):
            code = code.strip()
            test_type.extend(test_type_mapping.get(code, [code]))

        description = parts[6]

        recommendations.append({
            "url": url,
            "name": name,
            "adaptive_support": adaptive_support,
            "description": description,
            "duration": duration,
            "remote_support": remote_support,
            "test_type": test_type
        })

    return {"recommended_assessments": recommendations}
