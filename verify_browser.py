from playwright.sync_api import sync_playwright
from pathlib import Path
import json
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True)
 page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://localhost:8766/');page.screenshot(path=str(Path(__file__).parent/'test-results/desktop.png'),full_page=True)
 page.locator('#search-open').click();page.locator('#query').fill('权限');page.wait_for_selector('.search-result');assert page.locator('.search-result').count()>0;page.keyboard.press('Escape')
 page.goto('http://localhost:8766/practice.html');assert page.locator('.lab output').count()==5
 assert '允许访问' in page.locator('.lab output').nth(0).inner_text()
 page.locator('.lab').nth(0).locator('input').nth(1).fill('beta');assert '拒绝' in page.locator('.lab output').nth(0).inner_text()
 assert '36.0000' in page.locator('.lab output').nth(1).inner_text()
 assert '100.0' in page.locator('.lab output').nth(2).inner_text()
 for i in range(1,10):
  page.goto(f'http://localhost:8766/chapter-{i:02}.html');assert page.locator('article').inner_text();assert page.locator('.katex-error').count()==0
 page.set_viewport_size({'width':390,'height':844});page.goto('http://localhost:8766/chapter-09.html');assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
 page.screenshot(path=str(Path(__file__).parent/'test-results/mobile.png'),full_page=False)
 assert not errors,errors
 browser.close()
print('PASS: nine chapters, math rendering, search, five labs, access denial, known cost/capacity outputs, mobile width, JS errors')
