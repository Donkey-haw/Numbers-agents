import asyncio
import os
import base64
from playwright.async_api import async_playwright

LESSONS = [
    {"id": 1, "title": "평화 통일을 위한 노력", "pages": [12, 13, 14, 15]},
    {"id": 2, "title": "분단의 흔적, 평화의 장소", "pages": [16, 17, 18, 19]},
    {"id": 3, "title": "평화 통일을 위한 발걸음", "pages": [20, 21, 22, 23]},
    {"id": 4, "title": "함께 그리는 평화로운 미래", "pages": [24, 25, 26, 27]},
]

def get_image_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

async def generate_cards():
    template_path = os.path.abspath("html/modular_layout.html")
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for lesson in LESSONS:
            print(f"Generating card for Lesson {lesson['id']}...")
            
            images_html = ""
            for page_num in lesson['pages']:
                img_path = f"assets/pages/교과서_p{page_num}.png"
                if os.path.exists(img_path):
                    b64_data = get_image_base64(img_path)
                    images_html += f'<img src="data:image/png;base64,{b64_data}" />'
            
            html_content = template_content.replace("{{ LESSON_TITLE }}", lesson['title'])
            html_content = html_content.replace("{{ IMAGES_HTML }}", images_html)
            
            # Temporary HTML file for playwright to load
            temp_html = f"assets/cards/temp_lesson_{lesson['id']}.html"
            with open(temp_html, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            page = await browser.new_page(viewport={'width': 1920, 'height': 1080}, device_scale_factor=2)
            await page.goto(f"file://{os.path.abspath(temp_html)}")
            await page.wait_for_timeout(1000)
            
            output_path = os.path.abspath(f"assets/cards/lesson_{lesson['id']}.png")
            await page.screenshot(path=output_path, full_page=True)
            print(f"Saved: {output_path}")
            await page.close()
            os.remove(temp_html)
            
        await browser.close()

if __name__ == '__main__':
    asyncio.run(generate_cards())
