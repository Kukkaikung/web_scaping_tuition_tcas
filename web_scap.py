import asyncio
from playwright.async_api import async_playwright

async def scrape_tcas():
    keywords = ["วิศวกรรมคอมพิวเตอร์", "AI", "ปัญญาประดิษฐ์"]
    all_results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # เปลี่ยนเป็น True ถ้าไม่อยากให้โชว์ browser
        page = await browser.new_page()
        await page.goto("https://mytcas.com")

        for keyword in keywords:
            # พิมพ์คำค้นหา
            await page.fill("#search", keyword)
            await page.keyboard.press("Enter")

            # รอให้ผลลัพธ์โหลดเสร็จ
            await page.wait_for_selector("#results.t-result.active", timeout=15000)

            # ดึงลิงก์หลักสูตรทั้งหมด
            links = await page.eval_on_selector_all(
                "ul.t-programs li a",
                "elements => elements.map(el => el.href)"
            )

            for link in links:
                # เปิดแท็บใหม่เข้าไปดูรายละเอียดหลักสูตร
                detail_page = await browser.new_page()
                await detail_page.goto(link)

                try:
                    await detail_page.wait_for_selector("div.tuition", timeout=10000)
                    tuition = await detail_page.inner_text("div.tuition")
                    print(f"{keyword} → {link} → ค่าเทอม: {tuition}")
                    all_results.append((keyword, link, tuition))
                except:
                    print(f"{keyword} → {link} → ❌ ไม่พบข้อมูลค่าเทอม")
                    all_results.append((keyword, link, "ไม่พบ"))

                await detail_page.close()

        await browser.close()

    # บันทึกผลลัพธ์
    import csv
    with open("tuition_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["คำค้นหา", "ลิงก์หลักสูตร", "ค่าเทอม"])
        writer.writerows(all_results)

asyncio.run(scrape_tcas())
