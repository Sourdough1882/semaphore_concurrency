import time

import asyncio
from playwright.async_api import async_playwright

from urllib.parse import urlencode


class WebsiteScreenshotter:
    def __init__(self, context_parameters: dict, concurrency: int = 3, timeout: int = 30000) -> None:
        self.semaphore = asyncio.Semaphore(concurrency)
        self.context_parameters = context_parameters
        self.timeout = timeout
        self.playwright = None
        self.browser = None
        self.context = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context(**self.context_parameters)
        self.context.set_default_timeout(self.timeout)
        return self

    async def __aexit__(self, *args):
        if self.playwright is not None:
            await self.playwright.stop()
        if self.browser is not None:
            await self.browser.close()
        if self.context is not None:
            await self.context.close()

    async def screenshot(self, url, filename):
        async with self.semaphore:
            if self.context is not None:
                page = await self.context.new_page()
                try:
                    await page.goto(url)
                    await page.screenshot(path=f"{filename}.jpg", full_page=True)
                finally:
                    await page.close()


async def main():
    base_url = 'https://avito.ru/all/bytovaya_elektronika'

    page_count = 21

    query_string = 'видеокарта rtx 5070'

    url_list = [f"{base_url}?{urlencode({'p': count, 'q': query_string})}"
                for count in range(1, page_count)]

    context_parameters = {
        'user_agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    async with WebsiteScreenshotter(context_parameters=context_parameters, concurrency=3, timeout=100000) as screenshotter:
        tasks = [screenshotter.screenshot(
            url, f"screenshot/avito_screenshot_{url_list.index(url)}") for url in url_list]

        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
