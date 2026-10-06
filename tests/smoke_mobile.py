#!/usr/bin/env python3
"""Local Playwright checks and fresh mobile captures for the v5 review build."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
from threading import Thread

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "screenshots"
BASE_URL = os.environ.get("APP_BASE_URL", "")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass


def mobile_context(browser, width=390):
    return browser.new_context(viewport={"width": width, "height": 844}, device_scale_factor=1, is_mobile=True, has_touch=True)


def mock_location(page, state):
    """Mock web permission/location APIs so the local-only flow is repeatable."""
    script = """(() => {
      const simulatedState = __SIMULATED_STATE__;
      window.__locationAudit = { permissionChecks: 0, positionReads: 0 };
      Object.defineProperty(navigator, 'permissions', { configurable: true, value: { query: async ({ name }) => {
        if (name === 'geolocation') window.__locationAudit.permissionChecks += 1;
        return { state: simulatedState };
      } } });
      Object.defineProperty(navigator, 'geolocation', { configurable: true, value: {
        getCurrentPosition: (success, error) => {
          window.__locationAudit.positionReads += 1;
          if (simulatedState === 'granted') success({ coords: { latitude: 0, longitude: 0, altitude: null, accuracy: 100, altitudeAccuracy: null, heading: null, speed: null }, timestamp: Date.now() });
          else error({ code: 1, message: 'Permission denied' });
        }, watchPosition: () => 1, clearWatch: () => {}
      } });
    })();""".replace("__SIMULATED_STATE__", json.dumps(state))
    page.add_init_script(script)


def start_app(page):
    page.goto(BASE_URL, wait_until="networkidle")
    expect(page.get_by_role("button", name="Patchlane home")).to_be_visible()
    expect(page.get_by_text("Demo · fictional", exact=True)).to_be_visible()
    expect(page.get_by_text("Flat tyre?", exact=False)).to_be_visible()
    expect(page.get_by_text("nothing sent", exact=True)).to_be_visible()


def manual_search(page, area="Central sample area"):
    page.get_by_role("button", name="Use an area or landmark").click()
    page.get_by_label("Area or landmark").fill(area)
    page.get_by_role("button", name="Show sample mechanics").click()


def assert_one_primary(page):
    expect(page.get_by_test_id("primary-action")).to_have_count(1)
    expect(page.get_by_test_id("primary-action")).to_be_visible()


def assert_touch_targets(page, minimum=48):
    for element in page.get_by_role("button").all():
        if element.is_visible():
            bounds = element.evaluate("el => el.getBoundingClientRect().toJSON()")
            label = element.get_attribute("aria-label") or element.inner_text()
            assert bounds["height"] >= minimum, f"{label!r} target is {bounds['height']:.1f}px high"
            assert bounds["width"] >= minimum, f"{label!r} target is {bounds['width']:.1f}px wide"


def assert_no_horizontal_overflow(page, width):
    for selector in ("html", "body"):
        actual = page.locator(selector).evaluate("el => el.scrollWidth")
        assert actual <= width, f"{selector} overflows at {width}px: {actual}px"
    expect(page.get_by_text("Demo · fictional", exact=True)).to_have_count(1)


def capture(page, filename):
    path = SCREENSHOTS / filename
    page.screenshot(path=str(path), full_page=False, animations="disabled")
    size = page.evaluate("({width: innerWidth, height: innerHeight})")
    assert size == {"width": 390, "height": 844}, f"unexpected capture viewport: {size}"
    return path


def test_home_is_focused_and_location_is_opt_in(browser):
    context = mobile_context(browser)
    page = context.new_page()
    mock_location(page, "granted")
    external_requests = []
    page.on("request", lambda req: external_requests.append(req.url) if not req.url.startswith(BASE_URL) else None)
    start_app(page)
    assert_one_primary(page)
    assert page.evaluate("window.__locationAudit.permissionChecks") == 0
    assert page.evaluate("window.__locationAudit.positionReads") == 0
    for forbidden in ("tow truck", "fuel delivery", "battery replacement", "other roadside services"):
        assert forbidden not in page.locator("body").inner_text().lower(), f"scope drift: {forbidden}"
    assert_touch_targets(page)
    assert_no_horizontal_overflow(page, 390)
    capture(page, "01-rider-start-390x844.png")
    page.get_by_role("button", name="Find puncture help using optional one-time location check").click()
    expect(page.get_by_text("Sample mechanics", exact=True)).to_be_visible(timeout=10000)
    assert page.evaluate("window.__locationAudit.permissionChecks") == 1
    assert page.evaluate("window.__locationAudit.positionReads") == 1
    assert "not matched to your location" in page.locator("body").inner_text()
    assert external_requests == [], f"unexpected external requests: {external_requests}"
    context.close()


def test_denied_fallback_and_sample_list(browser):
    context = mobile_context(browser)
    page = context.new_page()
    mock_location(page, "denied")
    start_app(page)
    assert page.evaluate("window.__locationAudit.permissionChecks") == 0
    page.get_by_role("button", name="Find puncture help using optional one-time location check").click()
    expect(page.get_by_text("Location was not available", exact=False)).to_be_visible()
    expect(page.get_by_label("Area or landmark")).to_be_visible()
    assert page.evaluate("window.__locationAudit.permissionChecks") == 1
    assert page.evaluate("window.__locationAudit.positionReads") == 0
    assert_one_primary(page)
    assert_touch_targets(page)
    capture(page, "02-location-denied-fallback-390x844.png")
    page.get_by_label("Area or landmark").fill("Central sample area")
    page.get_by_role("button", name="Show sample mechanics").click()
    expect(page.get_by_text("Sample mechanics", exact=True)).to_be_visible()
    expect(page.get_by_text("Moss Lane Puncture Care", exact=True)).to_be_visible()
    expect(page.get_by_text("Sample window: later today", exact=True)).to_be_visible()
    expect(page.get_by_text("sample distance", exact=True)).to_have_count(2)
    expect(page.get_by_test_id("primary-action")).to_have_count(0)
    assert_touch_targets(page)
    assert_no_horizontal_overflow(page, 390)
    capture(page, "03-nearby-mechanics-390x844.png")
    context.close()


def test_no_results_recovery(browser):
    context = mobile_context(browser)
    page = context.new_page()
    start_app(page)
    manual_search(page, "Harbor sample area")
    expect(page.get_by_text("No sample mechanics yet", exact=True)).to_be_visible()
    expect(page.get_by_text("NO MATCH IN THIS SAMPLE", exact=True)).to_be_visible()
    expect(page.get_by_test_id("primary-action")).to_be_visible()
    assert_one_primary(page)
    assert_touch_targets(page)
    capture(page, "06-no-results-390x844.png")
    page.get_by_test_id("primary-action").click()
    expect(page.get_by_label("Area or landmark")).to_have_value("Harbor sample area")
    context.close()


def test_profile_request_and_cancel_are_local(browser):
    context = mobile_context(browser)
    page = context.new_page()
    external_requests = []
    page.on("request", lambda req: external_requests.append(req.url) if not req.url.startswith(BASE_URL) else None)
    start_app(page)
    manual_search(page)
    page.get_by_role("button", name="Open sample mechanic Moss Lane Puncture Care").click()
    expect(page.get_by_text("Moss Lane Puncture Care", exact=True)).to_be_visible()
    expect(page.get_by_text("000 000 0000", exact=True)).to_be_visible()
    assert "Fictional profile. No call can be placed from this preview." in page.locator("body").inner_text()
    assert_one_primary(page)
    assert_touch_targets(page)
    capture(page, "04-mechanic-profile-390x844.png")
    page.get_by_role("button", name="Preview request").click()
    expect(page.get_by_text("Request preview", exact=True)).to_be_visible()
    expect(page.get_by_text("Waiting for a reply", exact=True)).to_be_visible()
    expect(page.get_by_text("LOCAL PREVIEW", exact=True)).to_be_visible()
    expect(page.get_by_text("no mechanic was contacted", exact=False)).to_be_visible()
    assert_one_primary(page)
    assert_touch_targets(page)
    capture(page, "05-request-cancel-preview-390x844.png")
    page.get_by_role("button", name="Cancel request preview").click()
    expect(page.get_by_text("Preview cancelled", exact=True)).to_be_visible()
    expect(page.get_by_text("Nothing was sent or shared", exact=True)).to_be_visible()
    assert_one_primary(page)
    capture(page, "08-request-cancelled-390x844.png")
    assert external_requests == [], f"unexpected external requests: {external_requests}"
    context.close()


def test_one_shared_fictional_listing(browser):
    context = mobile_context(browser)
    page = context.new_page()
    start_app(page)
    page.get_by_role("button", name="Mechanic or shop? Preview one shared listing").click()
    expect(page.get_by_text("Preview a listing", exact=True)).to_be_visible()
    assert len(page.get_by_role("textbox").all()) == 3, "expected one shared name, phone and coverage-area form"
    body = page.locator("body").inner_text().lower()
    for forbidden in ("provider type", "independent mechanic", "shop signup", "service category", "choose your role"):
        assert forbidden not in body, f"unexpected provider split/category: {forbidden}"
    assert_one_primary(page)
    assert_touch_targets(page)
    capture(page, "07-unified-mechanic-listing-390x844.png")
    page.get_by_role("button", name="Preview listing").click()
    expect(page.get_by_text("Enter a fictional name", exact=False)).to_be_visible()
    expect(page.get_by_text("Use the all-zero sample number: 000 000 0000.", exact=True)).to_be_visible()
    page.get_by_label("Name riders will see").fill("Sample Wheel Help")
    page.get_by_label("Sample phone number").fill("5551234567")
    page.get_by_label("Sample coverage area").fill("Central sample area")
    page.get_by_role("button", name="Preview listing").click()
    expect(page.get_by_text("Use the all-zero sample number: 000 000 0000.", exact=True)).to_be_visible()
    page.get_by_label("Sample phone number").fill("0000000000")
    page.get_by_role("button", name="Preview listing").click()
    expect(page.get_by_text("Preview only", exact=True)).to_be_visible()
    expect(page.get_by_text("No listing was saved, published or sent.", exact=True)).to_be_visible()
    context.close()


def test_responsive_screens_and_touch_targets(browser):
    context = mobile_context(browser)
    page = context.new_page()
    mock_location(page, "denied")
    for width in (360, 390, 430, 768):
        page.set_viewport_size({"width": width, "height": 844})
        start_app(page)
        assert_one_primary(page)
        assert_no_horizontal_overflow(page, width)
        assert_touch_targets(page)
        page.get_by_role("button", name="Find puncture help using optional one-time location check").click()
        expect(page.get_by_label("Area or landmark")).to_be_visible()
        assert_one_primary(page)
        assert_no_horizontal_overflow(page, width)
        assert_touch_targets(page)
        page.get_by_label("Area or landmark").fill("Harbor sample area")
        page.get_by_role("button", name="Show sample mechanics").click()
        expect(page.get_by_text("No sample mechanics yet", exact=True)).to_be_visible()
        assert_one_primary(page)
        assert_no_horizontal_overflow(page, width)
        assert_touch_targets(page)
        page.get_by_test_id("primary-action").click()
        page.get_by_label("Area or landmark").fill("Central sample area")
        page.get_by_role("button", name="Show sample mechanics").click()
        expect(page.get_by_test_id("primary-action")).to_have_count(0)
        assert_no_horizontal_overflow(page, width)
        assert_touch_targets(page)
        page.get_by_role("button", name="Open sample mechanic Moss Lane Puncture Care").click()
        assert_no_horizontal_overflow(page, width)
        assert_touch_targets(page)
        page.get_by_role("button", name="Preview request").click()
        assert_no_horizontal_overflow(page, width)
        assert_touch_targets(page)
        page.get_by_role("button", name="Cancel request preview").click()
        assert_one_primary(page)
        page.goto(BASE_URL, wait_until="networkidle")
        page.get_by_role("button", name="Mechanic or shop? Preview one shared listing").click()
        assert_one_primary(page)
        assert_no_horizontal_overflow(page, width)
        assert_touch_targets(page)
        page.goto(BASE_URL, wait_until="networkidle")
    context.close()


def main():
    global BASE_URL
    SCREENSHOTS.mkdir(exist_ok=True)
    server = None
    if not BASE_URL:
        if not (ROOT / "dist" / "index.html").exists():
            raise SystemExit("Web export missing; run `npm run build:web` first.")
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT / "dist")))
        Thread(target=server.serve_forever, daemon=True).start()
        BASE_URL = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH", "/usr/bin/chromium"), args=["--no-sandbox", "--disable-dev-shm-usage"])
            checks = [
                ("focused puncture-only home and tap-only location", test_home_is_focused_and_location_is_opt_in),
                ("denied-location fallback and fictional sample list", test_denied_fallback_and_sample_list),
                ("no-results recovery", test_no_results_recovery),
                ("profile, single request preview and cancellation", test_profile_request_and_cancel_are_local),
                ("unified mechanic/shop sample listing", test_one_shared_fictional_listing),
                ("responsive widths, one primary action and 48px targets", test_responsive_screens_and_touch_targets),
            ]
            failures = []
            for name, test in checks:
                try:
                    test(browser)
                    print(f"PASS  {name}")
                except Exception as error:
                    failures.append((name, error))
                    print(f"FAIL  {name}: {type(error).__name__}: {error}")
            browser.close()
            if failures:
                raise SystemExit(1)
            print(f"Screenshots written to {SCREENSHOTS}")
    finally:
        if server:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    main()
