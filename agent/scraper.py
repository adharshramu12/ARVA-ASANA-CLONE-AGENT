# Web scraping functionality
import asyncio
from playwright.async_api import async_playwright
import json
import os
from dotenv import load_dotenv

load_dotenv()

ASANA_EMAIL = os.getenv("ASANA_EMAIL")
ASANA_PASSWORD = os.getenv("ASANA_PASSWORD")

async def extract_page(page, name):
    """Extracts HTML and computed CSS of the current page."""
    html = await page.content()

    # Extract computed CSS for all elements
    css_data = await page.evaluate("""
    () => {
        const elements = [...document.querySelectorAll('*')];
        return elements.map(el => {
            const styles = getComputedStyle(el);
            return {
                tag: el.tagName,
                class: el.className,
                id: el.id,
                css: {
                    color: styles.color,
                    background: styles.backgroundColor,
                    fontSize: styles.fontSize,
                    padding: styles.padding,
                    margin: styles.margin,
                    width: styles.width,
                    height: styles.height,
                    display: styles.display,
                }
            };
        });
    }
    """)

    data = {"html": html, "css": css_data}

    with open(f"agent/extracted/{name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"[OK] Extracted and saved: {name}.json")


async def login_and_extract():
    async with async_playwright() as p:
        print("[INFO] Launching browser...")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # STEP 1 — LOGIN
        print("[INFO] Opening Asana login page...")
        await page.goto("https://app.asana.com/")
        await page.wait_for_timeout(3000)

        print("[INFO] Entering email...")
        await page.locator("input[type='email']").fill(ASANA_EMAIL)
        await page.wait_for_timeout(1000)

        print("[INFO] Clicking first Continue...")
        await page.locator("div.LoginEmailForm-continueButton").first.click()
        await page.wait_for_timeout(3000)

        print("[INFO] Entering password...")
        await page.locator("input[type='password']").fill(ASANA_PASSWORD)
        await page.wait_for_timeout(2000)

        print("[INFO] Trying to submit password...")

        # Multiple fallback selectors
        selectors = [
            "div.LoginPasswordForm-continueButton",
            "button.LoginPasswordForm-submitButton",
            "button[type='submit']",
            "//button[contains(., 'Continue')]",
            "//div[contains(., 'Continue') and @role='button']",
        ]

        clicked = False
        for s in selectors:
            try:
                el = page.locator(s)
                if await el.count() > 0:
                    await el.first.click(timeout=5000)
                    print(f"[INFO] Clicked using selector: {s}")
                    clicked = True
                    break
            except Exception:
                pass

        # Final fallback
        if not clicked:
            print("[WARN] Continue button not found. Pressing Enter...")
            await page.keyboard.press("Enter")

        print("[INFO] Waiting for login to complete...")
        await page.wait_for_timeout(8000)

        # STEP 2 — NAVIGATE TO HOME
        print("[INFO] Navigating to Home page...")
        await page.goto("https://app.asana.com/0/home")
        await page.wait_for_timeout(8000)
        await extract_page(page, "home")

        # STEP 3 — PROJECTS
        print("[INFO] Navigating to Projects page...")
        await page.goto("https://app.asana.com/0/projects")
        await page.wait_for_timeout(8000)
        await extract_page(page, "projects")

        # STEP 4 — TASKS
        print("[INFO] Navigating to Tasks page...")
        await page.goto("https://app.asana.com/0/mytasks")
        await page.wait_for_timeout(8000)
        await extract_page(page, "tasks")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(login_and_extract())
