from utils import query_standards_by_playwright_browser


if __name__ == "__main__":
    import json
    import jsonlines
    with open("./data/standard_code.json", "r", encoding="utf-8") as f:
        standard_codes = json.load(f)

    with jsonlines.open("data/query_result.jsonl", mode="w") as writer:
        process = query_standards_by_playwright_browser(*standard_codes) 
        for res in process:
            writer.write(res)