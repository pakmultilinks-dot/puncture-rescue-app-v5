#!/usr/bin/env python3
"""Live-mode UI checks using isolated local mocks; no provider fixtures reach Supabase."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
from threading import Thread
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
LIVE_DIST = ROOT / "dist-live"
SCREENSHOTS = ROOT / "screenshots"
MOCK_URL = "https://patchlane-test.invalid"
MOCK_KEY = "sb_publishable_local_test_only"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass


def build_isolated_live_bundle():
    env = os.environ.copy()
    env["EXPO_PUBLIC_SUPABASE_URL"] = MOCK_URL
    env["EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY"] = MOCK_KEY
    subprocess.run(
        ["npx", "expo", "export", "--clear", "--platform", "web", "--output-dir", "dist-live"],
        cwd=ROOT,
        env=env,
        check=True,
    )


def capture(page, filename):
    path = SCREENSHOTS / filename
    page.screenshot(path=str(path), full_page=False, animations="disabled")
    size = page.evaluate("({width: innerWidth, height: innerHeight})")
    assert size == {"width": 390, "height": 844}, f"unexpected capture viewport: {size}"
    return path


def main():
    build_isolated_live_bundle()
    SCREENSHOTS.mkdir(exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(LIVE_DIST)))
    Thread(target=server.serve_forever, daemon=True).start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    requests = []
    mode = {"value": "normal"}
    fixture = {
        "id": "00000000-0000-4000-8000-000000000001",
        "display_name": "Fixture Test Mechanic",
        "public_area_label": "Gulberg, Lahore",
        "public_phone": "+923001234567",
        "verified_at": "2026-10-07T08:00:00Z",
        "verification_valid_until": "2099-10-07T08:00:00Z",
        "updated_at": "2026-10-07T08:00:00Z",
    }

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path=os.environ.get("CHROMIUM_PATH", "/usr/bin/chromium"),
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            context = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
            page = context.new_page()

            def directory_route(route):
                request = route.request
                if request.method == "OPTIONS":
                    route.fulfill(status=204, headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, OPTIONS",
                        "Access-Control-Allow-Headers": "apikey, accept",
                    })
                    return
                parsed = urlparse(request.url)
                query = parse_qs(parsed.query)
                requests.append({
                    "method": request.method,
                    "query": query,
                    "api_key": request.headers.get("apikey"),
                })
                if mode["value"] == "error" or (mode["value"] == "contact-error" and query.get("id")):
                    route.fulfill(status=503, headers={"Access-Control-Allow-Origin": "*"}, body='{"error":"offline"}')
                else:
                    rows = []
                    if query.get("id") == [f"eq.{fixture['id']}"]:
                        rows = [] if mode["value"] == "revoked" else [fixture]
                    elif "Gulberg" in query.get("public_area_label", [""])[0]:
                        rows = [fixture]
                    if rows and mode["value"] == "expired":
                        rows = [{**fixture, "verification_valid_until": "2020-01-01T00:00:00Z"}]
                    route.fulfill(
                        status=200,
                        headers={"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
                        body=json.dumps(rows),
                    )

            page.route(f"{MOCK_URL}/rest/v1/provider_directory**", directory_route)
            page.goto(base_url, wait_until="networkidle")
            expect(page.get_by_text("Pilot", exact=True)).to_be_visible()
            expect(page.get_by_text("Live · verified", exact=True)).to_have_count(0)
            expect(page.get_by_text("Flat tyre?", exact=False)).to_be_visible()
            expect(page.get_by_text("Area-only search.", exact=False)).to_be_visible()
            expect(page.get_by_role("button", name="Mechanic or shop? Preview one sample listing; not signup")).to_have_count(0)
            capture(page, "09-pilot-home-390x844.png")

            page.get_by_role("button", name="Search the pilot directory by area").click()
            expect(page.get_by_label("Area or landmark")).to_be_visible()
            page.get_by_label("Area or landmark").fill("Gulberg")
            page.get_by_role("button", name="Search pilot directory").click()
            expect(page.get_by_text("Verified listings", exact=True)).to_be_visible(timeout=10000)
            expect(page.get_by_text("Fixture Test Mechanic", exact=True)).to_be_visible()
            expect(page.get_by_text("sample distance", exact=True)).to_have_count(0)
            expect(page.get_by_text("sample ETA", exact=True)).to_have_count(0)
            assert requests, "expected a read-only request to the public view"
            first = requests[-1]
            assert first["method"] == "GET", first
            assert first["api_key"] == MOCK_KEY, "the test bundle must use only its isolated publishable mock key"
            assert first["query"].get("select") == ["id,display_name,public_area_label,public_phone,verified_at,verification_valid_until,updated_at"]
            assert first["query"].get("public_area_label") == ["ilike.*Gulberg*"]
            assert first["query"].get("limit") == ["50"]

            page.get_by_role("button", name="Open verified mechanic Fixture Test Mechanic").click()
            expect(page.get_by_text("+923001234567", exact=True)).to_be_visible()
            expect(page.get_by_text("Verification valid until", exact=True)).to_be_visible()
            expect(page.get_by_text("explicitly consented to public contact", exact=False)).to_be_visible()
            expect(page.get_by_role("button", name="Open phone dialer for Fixture Test Mechanic")).to_be_visible()
            expect(page.get_by_text("Calling, messaging and requests are not enabled", exact=False)).to_have_count(0)
            expect(page.get_by_test_id("primary-action")).to_have_count(1)

            mode["value"] = "contact-error"
            page.get_by_role("button", name="Open phone dialer for Fixture Test Mechanic").click()
            expect(page.get_by_text("The current listing could not be checked.", exact=False)).to_be_visible()
            assert requests[-1]["query"].get("id") == [f"eq.{fixture['id']}"]

            mode["value"] = "revoked"
            page.get_by_role("button", name="Open phone dialer for Fixture Test Mechanic").click()
            expect(page.get_by_text("This listing is no longer public with current contact consent and verification.", exact=False)).to_be_visible()
            assert requests[-1]["query"].get("id") == [f"eq.{fixture['id']}"]

            mode["value"] = "expired"
            page.get_by_role("button", name="Patchlane home").click()
            page.get_by_role("button", name="Search the pilot directory by area").click()
            page.get_by_label("Area or landmark").fill("Gulberg")
            page.get_by_role("button", name="Search pilot directory").click()
            expect(page.get_by_text("Verified listings", exact=True)).to_be_visible(timeout=10000)
            page.get_by_role("button", name="Open verified mechanic Fixture Test Mechanic").click()
            page.get_by_role("button", name="Open phone dialer for Fixture Test Mechanic").click()
            expect(page.get_by_text("This listing is no longer currently verified.", exact=False)).to_be_visible()

            mode["value"] = "normal"
            page.get_by_role("button", name="Patchlane home").click()
            page.get_by_role("button", name="Search the pilot directory by area").click()
            page.get_by_label("Area or landmark").fill("Different area")
            page.get_by_role("button", name="Search pilot directory").click()
            expect(page.get_by_text("No verified listings yet", exact=True)).to_be_visible(timeout=10000)
            expect(page.get_by_text("NO CURRENT VERIFIED LISTINGS", exact=True)).to_be_visible()
            expect(page.get_by_text("no one will be dispatched", exact=False)).to_be_visible()
            expect(page.get_by_text("Fixture Test Mechanic", exact=True)).to_have_count(0)
            capture(page, "10-pilot-empty-directory-390x844.png")

            mode["value"] = "error"
            page.get_by_role("button", name="Patchlane home").click()
            page.get_by_role("button", name="Search the pilot directory by area").click()
            page.get_by_label("Area or landmark").fill("Gulberg")
            page.get_by_role("button", name="Search pilot directory").click()
            expect(page.get_by_text("Pilot directory unavailable", exact=True)).to_be_visible(timeout=10000)
            expect(page.get_by_text("DIRECTORY TEMPORARILY UNAVAILABLE", exact=True)).to_be_visible()
            expect(page.get_by_role("button", name="Try again")).to_be_visible()

            context.close()
            browser.close()
            print("PASS  pilot labeling, public-view search, empty/error recovery, fail-closed consent/verification recheck before contact, and absence of rider/demo location features")
            print(f"Fresh pilot UI screenshots written to {SCREENSHOTS}")
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
