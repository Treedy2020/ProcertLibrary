sft-data-generator --file_path "Standard -IEC.xlsx" \
--prompt "sft-data-generator prompt\n你是一个有用的法规查询助手，你会看到一个包含S
tandard Code在内的用户填写的内容，请根据你所看到的内容推测法规的主要Standard Code\n你只需要返回犯规的主要编号即可，即 EN 10079-1 时，你只需要返回 EN 10079，而不需要返回其他的编号，你的回答应该是一个严格
的形如如下格式的json格式， 你的回答不需要包含除了它之外的其他内容：\n注意：你不需要返回的是标准的小编号，但是标准的前置编号需要完整, basic_standard_code需要完整，而 failed_reason可以是空的，也可以是简短
的为什么失败了的说明。\n            {\n                \"basic_standard_code\": \"EN 10079\",\n                \"failed_reson\": \"<reason here>\" | null\n            }\n" \
--model "gpt-4o" \
--openai_api_key "sk-8B176nuYqRVkfLQTnJoqjOKdY95IWV2lU4sXcdAONn9Arj88" \
--openai_base_url "https://api.deerapi.com/v1" \
--batch_size 50 \
--json_output

# --openai_api_key "sk-aaee86f53153483a94584b2bb095744e" \
# --openai_base_url "https://api.deepseek.com/v1" \