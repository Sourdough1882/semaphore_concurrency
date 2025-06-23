import asyncio
from urllib.parse import urlencode
from playwright.async_api import async_playwright


class WebsiteScreenshotter:
    def __init__(self, context_parameters: dict, concurrency: int = 3) -> None:
        self.semaphore = asyncio.Semaphore(concurrency)
        self.context_parameters = context_parameters
        self.playwright = None
        self.browser = None
        self.context = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch()
        self.context = await self.browser.new_context(**self.context_parameters)
        return self

    async def __aexit__(self, *args):
        if self.playwright is not None:
            await self.playwright.stop()
        if self.browser is not None:
            await self.browser.close()
        if self.context is not None:
            await self.context.close()

    async def screenshot(self, url):
        async with self.semaphore:
            if self.context is not None:
                page = await self.context.new_page()
                try:
                    await page.goto(url)
                    await page.screenshot(path=f"screenshot_{url}.jpg")
                finally:
                    await page.close()


async def main():
    base_url = 'https://avito.ru/all/bytovaya_elektronika'

    page_count = 21

    url_list = []

    for count in range(1, page_count):
        query_params: dict = {
            'p': count,
            'q': 'видеокарта rtx 5070'
        }

        query_string: str = urlencode(query_params)

        url_list.append(f"{base_url}?{query_string}")

    context_parameters = {
        'user_agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    async with WebsiteScreenshotter(context_parameters=context_parameters, concurrency=3) as screenshotter:
        tasks = [screenshotter.screenshot(url) for url in url_list]

        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
