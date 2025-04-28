headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://standards.cencenelec.eu",
    "Referer": "https://standards.cencenelec.eu/dyn/www/f?p=CEN:105::RESET::::",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.4 Safari/605.1.15"
}
cookies = {
    "_ga": "GA1.2.1952288258.1745311331",
    "_ga_9YZXET655N": "GS1.1.1745806387.2.0.1745806387.60.0.462430677",
    "_gid": "GA1.2.252076882.1745806388",
    "PUBLIC_WWV_CUSTOM-F_1752901311939974_205": "524024701017101",
    "PUBLIC_WWV_CUSTOM-F_1752901311939974_305": "678583894974601",
    "WWV_CUSTOM-F_1752901311939974_205": "C2121A07CAF9269845F250F4024E9919",
    "WWV_CUSTOM-F_1752901311939974_305": "E9139843F78AB5AAAAAEE07095EDA8FA"
}
 
 
if __name__ == "__main__":
    # har_cookies = [
    #     {"name": "_ga", "value": "GA1.2.1952288258.1745311331"},
    #     {"name": "_ga_9YZXET655N", "value": "GS1.1.1745806387.2.0.1745806387.60.0.462430677"},
    #     {"name": "_gid", "value": "GA1.2.252076882.1745806388"},
    #     {"name": "PUBLIC_WWV_CUSTOM-F_1752901311939974_205", "value": "524024701017101"},
    #     {"name": "PUBLIC_WWV_CUSTOM-F_1752901311939974_305", "value": "678583894974601"},
    #     {"name": "WWV_CUSTOM-F_1752901311939974_205", "value": "C2121A07CAF9269845F250F4024E9919"},
    #     {"name": "WWV_CUSTOM-F_1752901311939974_305", "value": "E9139843F78AB5AAAAAEE07095EDA8FA"}
    # ]
 
    # # 补充缺失的字段 (这些是基于通用实践的猜测，请务必核实!)
    # # expires_timestamp = int(time.time()) + 365 * 24 * 60 * 60 # 假设一年有效期
    # expires_timestamp = -1
 
    # cookies_for_state = []
    # for cookie in har_cookies:
    #     # 为不同类型的 cookie 设置不同的默认值（示例）
    #     is_ga_cookie = cookie["name"].startswith("_ga")
    #     is_session_like = "WWV_CUSTOM" in cookie["name"] # 猜测 WWV 是会话相关
 
    #     cookies_for_state.append({
    #         "name": cookie["name"],
    #         "value": cookie["value"],
    #         "domain": ".standards.cencenelec.eu",  # <--- 确认这个!
    #         "path": "/",                         # <--- 确认这个!
    #         "expires": expires_timestamp,       # <--- 对会话 cookie 可能需要设为 -1 或更精确的值
    #         "httpOnly": True if is_session_like else False, # <--- 猜测会话 cookie 是 httpOnly
    #         "secure": True,                     # <--- 网站是 https
    #         "sameSite": "Lax"                   # <--- 常见的默认值，需要确认
    #     })
 
    # with sync_playwright() as p:
    #     # cookies_for_state = [
    #     #     {"name": k, "value": v, "domain": ".standards.cencenelec.eu", "path": "/"}
    #     #     for k, v in cookies.items()
    #     # ]
    #     request_context = p.request.new_context(
    #         base_url="https://standards.cencenelec.eu",
    #         extra_http_headers=headers,
    #         storage_state={"cookies": cookies_for_state}
    #     )
    #     response = playwright_query_standards("IEC 60335", request_context)
    #     print(response.text)
 
    # request_html = query_standards_by_request_html("IEC 60335")
    # print(request_html)
 
    html = query_standards_by_playwright_browser("IEC 60335")
    print(html)