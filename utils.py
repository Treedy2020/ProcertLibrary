import time
import asyncio
from typing import List
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Page
from playwright.async_api import async_playwright
from playwright.async_api import Page as AsyncPage
from tqdm import tqdm
from tenacity import retry, stop_after_attempt

async def page_pool_worker(
    worker_id: int,
    page_pool: asyncio.Queue[Page],
    query_queue: asyncio.Queue[str],
    results_list: List # 用于收集结果的列表 (也可以用结果队列)
):
    """
    工作者协程，不断从查询队列获取任务，从页面池获取页面，执行任务，归还页面。
    """
    print(f"[Worker {worker_id}] 启动")
    while True:
        try:
            # 1. 从查询队列获取任务，如果队列为空则等待
            query = await query_queue.get()
            print(f"[Worker {worker_id}] 获取到任务: '{query}'")

            page = None # 先置为 None
            try:
                # 2. 从页面池获取一个空闲页面，如果池为空则等待
                print(f"[Worker {worker_id}] 正在等待空闲页面...")
                page = await page_pool.get()
                print(f"[Worker {worker_id}] 获取到页面: {page.guid[-6:]}")

                # 3. 在获取到的页面上执行查询逻辑
                result = await handle_query_async(page, query)
                results_list.append(result) # 收集结果

            except Exception as e:
                # 捕获执行查询或获取页面时的意外错误
                print(f"[Worker {worker_id}] 执行任务 '{query}' 时发生严重错误: {e}")
                # 可以在这里记录错误，或者尝试重新将任务放回队列
                results_list.append({"query": query, "success": False, "error": f"Worker level error: {e}"})

            finally:
                if page:
                    # 4. 将页面归还到池中，供其他 Worker 使用
                    print(f"[Worker {worker_id}] 归还页面: {page.guid[-6:]}")
                    await page_pool.put(page)

                # 5. 标记查询队列中的这个任务已完成
                query_queue.task_done()

        except asyncio.CancelledError:
            print(f"[Worker {worker_id}] 被取消，正在退出...")
            break # 收到取消信号时退出循环
        except Exception as e:
            # 捕获获取查询任务时的错误 (例如队列关闭时)
            print(f"[Worker {worker_id}] 获取查询任务时出错: {e}")
            break # 退出循环

    print(f"[Worker {worker_id}] 退出")

async def run_with_page_pool(queries: List[str], pool_size: int, num_workers: int):
    """
    设置并运行页面池系统来处理查询。
    """
    page_pool: asyncio.Queue[Page] = asyncio.Queue(maxsize=pool_size)
    query_queue: asyncio.Queue[str] = asyncio.Queue()
    results_list = [] # 存储最终结果

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True) # 启动浏览器
        context = await browser.new_context() # 创建一个浏览器上下文

        print(f"正在初始化页面池 (大小: {pool_size})...")
        # 初始化页面池
        init_tasks = []
        for i in range(pool_size):
            async def create_and_init_page(pid):
                page = await context.new_page()
                page.goto("https://standards.cencenelec.eu/dyn/www/f?p=CEN:105::RESET::::")
                page.click("#sformsub1 > div > div:nth-child(6) > div.col-md-10.checkboxList > div:nth-child(7) > label")
                try:
                    print(f"  页面 {pid} ({page.guid[-6:]}) 初始化完成 (模拟)。")
                    await page_pool.put(page) 
                except Exception as e:
                    print(f"  页面 {pid} 初始化失败: {e}")
            init_tasks.append(create_and_init_page(i + 1))
        await asyncio.gather(*init_tasks)
        print(f"页面池初始化完成，可用页面: {page_pool.qsize()}")

        for query in queries:
            await query_queue.put(query)
        print(f"已将 {len(queries)} 个查询放入队列。")

        # 创建并启动工作者协程
        print(f"正在启动 {num_workers} 个工作者...")
        worker_tasks = []
        for i in range(num_workers):
            task = asyncio.create_task(
                page_pool_worker(i + 1, page_pool, query_queue, results_list)
            )
            worker_tasks.append(task)

        # 等待所有查询被处理完毕
        start_time = time.time()
        await query_queue.join() # 等待队列中的所有任务被 task_done() 标记
        print("所有查询处理完成。")
        end_time = time.time()

        # 所有查询完成后，取消工作者任务
        print("正在停止工作者...")
        for task in worker_tasks:
            task.cancel()
        # 等待所有工作者真正退出
        await asyncio.gather(*worker_tasks, return_exceptions=True)
        print("所有工作者已停止。")

        # 关闭池中的所有页面和浏览器
        print("正在关闭页面和浏览器...")
        while not page_pool.empty():
            page = await page_pool.get()
            await page.close()
        await context.close()
        await browser.close()
        print("浏览器已关闭。")

    print(f"\n--- 处理结果 ({len(results_list)} items) ---")
    # 可以在这里打印或处理 results_list
    # for res in results_list:
    #     print(res)
    print(f"总耗时: {end_time - start_time:.2f} 秒")
 

def query_standards_by_playwright_browser(*queries: List[str]):
    """
    Query standards using Playwright browser automation.

    This function uses Playwright to automate a web browser, navigate to the CEN-CENELEC
    standards search page, input a query, and retrieve the results table.

    Args:
        query (str): The search query for standards.

    Returns:
        None: This function prints the inner HTML of the results table.

    Note:
        This function requires the Playwright library to be installed and imported.
        It launches a Chromium browser, performs the search, and then closes the browser.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://standards.cencenelec.eu/dyn/www/f?p=CEN:105::RESET::::")
        page.click("#sformsub1 > div > div:nth-child(6) > div.col-md-10.checkboxList > div:nth-child(7) > label")
        # select_locator = page.locator("#HEAD_LIST")
        # select_locator.select_option(value="EN")
        for query in tqdm(queries, desc="Querying standards"):
            try:
                result = handle_query(page, query)
                yield result
            except Exception as e:
                result = {
                    "query": query,
                    "error": str(e),
                    "standards": []
                }
                yield result
        browser.close()

async def handle_query_async(page: AsyncPage, query: str) -> dict:
    await page.fill("#STAND_REF", query)
    await page.click("#tformsub1")
    table_selector = "#sdashsub1 > div"
    await page.wait_for_selector(table_selector)
    result = result_parser(page.content())
    result["query"] = query
    result["error"] = None
    return result

@retry(stop=stop_after_attempt(3))
def handle_query(page: Page, query: str) -> dict:
    """
    Handle a single query on the standards search page.

    This function fills in the search form, submits it, waits for the results,
    and then parses the results.

    Args:
        page (Page): The Playwright page object representing the current browser page.
        query (str): The search query for standards.

    Returns:
        dict: A dictionary containing the parsed results, including:
            - 'standards': A list of dictionaries, each representing a standard.
            - 'query': The original search query.
            - 'error': Always None in this function (errors are handled in the calling function).

    Raises:
        Exception: If there's an error during the process, it will be caught and re-raised
                   by the @retry decorator, which will attempt the operation up to 3 times.

    Note:
        This function is decorated with @retry, which will retry the operation
        up to 3 times in case of failure.
    """
    page.fill("#STAND_REF", query)
    page.click("#tformsub1")
    table_selector = "#sdashsub1 > div"
    page.wait_for_selector(table_selector)
    result = result_parser(page.content())
    result["query"] = query
    result["error"] = None
    return result

def result_parser(table_html: str):
    """
    Parse the result string to get the standard details.
    """
    soup = BeautifulSoup(table_html, "html.parser")
    table_rows = soup.find_all("tr")
    table_data = []
    for row in table_rows:
        row_data = row.find_all("td")
        if len(row_data) == 0:
            continue
        committee = row_data[0].text.strip('\n')

        code_with_url = row_data[1].find("a")
        code, url = code_with_url.text.strip('\n'), code_with_url["href"]
        full_data = row_data[1].text.strip('\n')
        status = row_data[2].text.strip('\n')

        row_map = {
            "full_data": full_data,
            "code": code,
            "url": url,
            "committee": committee,
            "status": status,
        }
        table_data.append(row_map)
    result = {
        "standards": table_data,
    }
    return result

if __name__ == "__main__":
    from pprint import pprint
    result = query_standards_by_playwright_browser("EN 60335-1")
    for r in result:
        pprint(r)
