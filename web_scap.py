import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import csv
import os
import re

async def scrape_tcas():
    keywords = ["วิศวกรรมคอมพิวเตอร์"]
    all_results = []

    os.makedirs("debug_html", exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://mytcas.com")

        for keyword in keywords:
            await page.fill("#search", "")
            await page.fill("#search", keyword)
            await page.keyboard.press("Enter")

            try:
                await page.wait_for_selector("#results.t-result.active ul.t-programs", timeout=15000)
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
                    await detail_page.wait_for_selector("main.site-body", timeout=15000)

                    # คลิกแท็บ Overview ถ้าไม่ active
                    tab_overview = await detail_page.query_selector('a.r0[href="#overview"]')
                    if tab_overview:
                        class_attr = await tab_overview.get_attribute("class") or ""
                        if "active" not in class_attr:
                            await tab_overview.click()
                            await detail_page.wait_for_timeout(1000)

                    content = await detail_page.content()
                    filename = f"debug_html/{keyword.replace(' ','_')}_{idx}.html"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(content)

                    soup = BeautifulSoup(content, "html.parser")

                    main_site_body = soup.select_one("main.site-body")
                    program_text = "ไม่พบข้อมูลหลักสูตรในแท็บ Overview"

                    if main_site_body:
                        div_t_box = main_site_body.select_one("div.t-box")
                        if div_t_box:
                            ul_body = div_t_box.select_one("ul.body.t-program")
                            if ul_body:
                                dls = ul_body.find_all("dl")
                                result_lines = []
                                for dl in dls:
                                    dts = dl.find_all("dt")
                                    dds = dl.find_all("dd")
                                    for dt, dd in zip(dts, dds):
                                        dd_text = dd.get_text(strip=True)
                                        # กรองเฉพาะ dd ที่มีตัวเลข
                                        if re.search(r"\d", dd_text):
                                            line = f"{dt.get_text(strip=True)}: {dd_text}"
                                            result_lines.append(line)
                                if result_lines:
                                    program_text = "\n".join(result_lines)
                                else:
                                    program_text = "ไม่พบ <dd> ที่มีตัวเลขในหลักสูตร"
                            else:
                                program_text = "ไม่พบ ul.body.t-program"
                        else:
                            program_text = "ไม่พบ div.t-box"
                    else:
                        program_text = "ไม่พบ main.site-body"

                    print(f"คำค้นหา: {keyword} | URL: {link}\nข้อมูลหลักสูตร:\n{program_text}\n{'-'*80}")

                    all_results.append({
                        "คำค้นหา": keyword,
                        "URL": link,
                        "ข้อมูลหลักสูตร": program_text
                    })

                except Exception as e:
                    print(f"{keyword} → {link} → ❌ Error: {e}")
                    all_results.append({
                        "คำค้นหา": keyword,
                        "URL": link,
                        "ข้อมูลหลักสูตร": "Error เก็บข้อมูลไม่ได้"
                    })

                await detail_page.close()

        await browser.close()

    with open("tcas_programs.csv", "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = ["คำค้นหา", "URL", "ข้อมูลหลักสูตร"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

if __name__ == "__main__":
    asyncio.run(scrape_tcas())
