import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import csv
import os
import re

async def scrape_tcas():
    keywords = ["วิศวกรรมคอมพิวเตอร์"]
    all_results = []
    all_fields = set(["มหาวิทยาลัย"])  # เพิ่ม column มหาวิทยาลัยไว้ล่วงหน้า

    os.makedirs("debug_html", exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://mytcas.com")

        for keyword in keywords:
            await page.fill("#search", "")
            await page.fill("#search", keyword)
            await page.keyboard.press("Enter")

            await page.wait_for_timeout(3000)  # รอให้หน้าโหลดผลลัพธ์

            try:
                await page.wait_for_selector("ul.t-programs li a", timeout=10000)
            except:
                print(f"❌ ไม่พบผลลัพธ์สำหรับคำค้นหา: {keyword}")
                continue

            links = await page.eval_on_selector_all(
                "ul.t-programs li a",
                "elements => elements.map(el => el.href)"
            )

            for idx, link in enumerate(links):
                detail_page = await browser.new_page()
                try:
                    await detail_page.goto(link, wait_until="networkidle")
                    await detail_page.wait_for_timeout(1000)

                    # คลิกแท็บ Overview หากยังไม่ active
                    tab_overview = await detail_page.query_selector('a.r0[href="#overview"]')
                    if tab_overview:
                        class_attr = await tab_overview.get_attribute("class") or ""
                        if "active" not in class_attr:
                            await tab_overview.click()
                            await detail_page.wait_for_timeout(1000)

                    content = await detail_page.content()

                    # บันทึก HTML ไว้ดูภายหลัง (debug)
                    filename = f"debug_html/{keyword.replace(' ', '_')}_{idx}.html"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(content)

                    soup = BeautifulSoup(content, "html.parser")
                    result_dict = {}

                    main_site_body = soup.select_one("main.site-body")
                    if main_site_body:
                        # ✅ ดึงชื่อมหาวิทยาลัย
                        a_uni = main_site_body.select_one("span.h-brand a")
                        if a_uni:
                            result_dict["มหาวิทยาลัย"] = a_uni.get_text(strip=True)

                        # ✅ ดึงข้อมูล dt/dd
                        div_t_box = main_site_body.select_one("div.t-box")
                        if div_t_box:
                            ul_body = div_t_box.select_one("ul.body.t-program")
                            if ul_body:
                                dls = ul_body.find_all("dl")
                                for dl in dls:
                                    dts = dl.find_all("dt")
                                    dds = dl.find_all("dd")
                                    for dt, dd in zip(dts, dds):
                                        key = dt.get_text(strip=True)
                                        value = dd.get_text(strip=True)
                                        result_dict[key] = value
                                        all_fields.add(key)

                    if result_dict:
                        all_results.append(result_dict)

                except Exception as e:
                    print(f"❌ Error with link: {link} → {e}")

                await detail_page.close()

        await browser.close()

    # ✅ สร้าง CSV
    fieldnames = ["มหาวิทยาลัย"] + sorted(f for f in all_fields if f != "มหาวิทยาลัย")
    with open("tcas_programs.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_results:
            writer.writerow(row)

if __name__ == "__main__":
    asyncio.run(scrape_tcas())
