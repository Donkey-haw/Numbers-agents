import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080}, device_scale_factor=2)
        await page.goto('file:///Users/jonyeock/Desktop/Tool/NumbersAuto/modular_layout.html')
        await page.wait_for_timeout(2000)
        await page.screenshot(path='/Users/jonyeock/Desktop/Tool/NumbersAuto/디자인_마스터본.png', full_page=True)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
