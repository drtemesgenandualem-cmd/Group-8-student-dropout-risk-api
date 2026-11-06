"""Optional browser evidence. Install playwright and use local Google Chrome."""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument('--base-url', default='http://127.0.0.1:8000')
parser.add_argument('--ignore-https-errors', action='store_true', help='Allow CDN assets in an environment with an untrusted HTTPS proxy certificate.')
args = parser.parse_args()
with sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True, args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 1440, 'height': 1050}, device_scale_factor=1, ignore_https_errors=args.ignore_https_errors)
    page.goto(args.base_url+'/docs')
    page.locator('.opblock-post .opblock-summary').wait_for(timeout=30000)
    page.screenshot(path=str(ROOT/'evidence/docs.png'), full_page=True)
    operation = page.locator('.opblock-post')
    operation.locator('.opblock-summary').click()
    operation.get_by_role('button', name='Try it out').click()
    operation.locator('textarea').fill((ROOT/'examples/valid_student.json').read_text())
    operation.get_by_role('button', name='Execute', exact=True).click()
    response = operation.locator('.responses-inner .live-responses-table')
    response.wait_for(timeout=30000)
    assert '200' in response.inner_text()
    assert '0.4128' in response.inner_text()
    response.scroll_into_view_if_needed()
    page.screenshot(path=str(ROOT/'evidence/successful_prediction.png'))
    page.screenshot(path=str(ROOT/'evidence/docs_prediction_full.png'), full_page=True)
    browser.close()
print('Captured live Swagger docs and an executed HTTP 200 prediction.')
