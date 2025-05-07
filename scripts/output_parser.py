import json
import re
import jsonlines
from tqdm import tqdm

result_files = [
    "data/Standard -EN.xlsx.output.jsonl",
    "data/Standard -IEC.xlsx.output.jsonl",
]

def process_jsonl_file(*file): 
    result = set()
    pattern = r"```json\n(.*?)\n```"
    error_count = 0

    for file in tqdm(file):
        with jsonlines.open(file) as reader:
            for obj in reader:
                try:
                    if "```json" in obj["gpt-response"]:
                        match = re.search(pattern, obj["gpt-response"], re.DOTALL)
                        if match:
                            json_str = match.group(1)
                            obj["gpt-response"] = json_str
                    res = json.loads(obj["gpt-response"])['basic_standard_code']
                    result.add(res)
                except json.JSONDecodeError as e:
                    error_count += 1
    return result
    

if __name__ == "__main__":
    import json
    with open("data/standard_code.json", "w", encoding="utf-8") as f:
        # f.write(json.dumps(list(process_jsonl_file(*result_files)), ensure_ascii=False, indent=4))
        json.dump(list(process_jsonl_file(*result_files)), f, ensure_ascii=False, indent=4)