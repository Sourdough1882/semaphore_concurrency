import asyncio
from urllib.parse import urlencode
from playwright.async_api import async_playwright


base_url = 'https://avito.ru/all/bytovaya_elektronika'
urls = [
    f"{base_url}?{urlencode({'q': 'rtx 5070', 'p': i})}" for i in range(1, 20)]


semaphore = asyncio.Semaphore(3)


async def screenshot_page(context, url: str, filepath: str):
    async with semaphore:
        page = await context.new_page()
        await page.goto(url)
        await page.wait_for_timeout(10000)
        await page.screenshot(path=filepath, full_page=True)
        await page.close()


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:139.0)"
            "Gecko/20100101 Firefox/139.0"
        )

        context.set_default_timeout(80000)

        count = 0

        tasks = []

        for url in urls:
            tasks.append(screenshot_page(
                context, url, f"screenshots/screenshot_page_{count}.jpg"))
            count += 1

        await asyncio.gather(*tasks)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
