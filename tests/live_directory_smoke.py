#!/usr/bin/env python3
"""Live-mode UI checks using an isolated local mock; no provider fixtures reach Supabase."""
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


def mock_location(page):
    page.add_init_script("""(() => {
      window.__locationAudit = { permissionChecks: 0, positionReads: 0 };
      Object.defineProperty(navigator, 'permissions', { configurable: true, value: { query: async ({ name }) => {
        if (name === 'geolocation') window.__locationAudit.permissionChecks += 1;
        return { state: 'granted' };
      } } });
      Object.defineProperty(navigator, 'geolocation', { configurable: true, value: {
        getCurrentPosition: (success) => { window.__locationAudit.positionReads += 1; success({ coords: { latitude: 0, longitude: 0 }, timestamp: Date.now() }); },
        watchPosition: () => 1, clearWatch: () => {}
      } });
    })();""")


def main():
    build_isolated_live_bundle()
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
            mock_location(page)

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
                if mode["value"] == "error":
                    route.fulfill(status=503, headers={"Access-Control-Allow-Origin": "*"}, body='{"error":"offline"}')
                else:
                    rows = [fixture] if "Gulberg" in query.get("public_area_label", [""])[0] else []
                    route.fulfill(
                        status=200,
                        headers={"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
                        body=json.dumps(rows),
                    )

            page.route(f"{MOCK_URL}/rest/v1/provider_directory**", directory_route)
            page.goto(base_url, wait_until="networkidle")
            expect(page.get_by_text("Live · verified", exact=True)).to_be_visible()
            expect(page.get_by_text("Flat tyre?", exact=False)).to_be_visible()
            assert page.evaluate("window.__locationAudit.permissionChecks") == 0

            page.get_by_role("button", name="Search verified mechanics by area").click()
            expect(page.get_by_label("Area or landmark")).to_be_visible()
            assert page.evaluate("window.__locationAudit.permissionChecks") == 0
            page.get_by_label("Area or landmark").fill("Gulberg")
            page.get_by_role("button", name="Search live directory").click()
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
            assert page.evaluate("window.__locationAudit.permissionChecks") == 0
            assert page.evaluate("window.__locationAudit.positionReads") == 0

            page.get_by_role("button", name="Open verified mechanic Fixture Test Mechanic").click()
            expect(page.get_by_text("+923001234567", exact=True)).to_be_visible()
            expect(page.get_by_text("Verification valid until", exact=True)).to_be_visible()
            expect(page.get_by_text("Calling, messaging and requests are not enabled in Patchlane.", exact=False)).to_be_visible()
            expect(page.get_by_test_id("primary-action")).to_have_count(0)

            page.get_by_role("button", name="Patchlane home").click()
            page.get_by_role("button", name="Search verified mechanics by area").click()
            page.get_by_label("Area or landmark").fill("Different area")
            page.get_by_role("button", name="Search live directory").click()
            expect(page.get_by_text("No verified listings yet", exact=True)).to_be_visible(timeout=10000)
            expect(page.get_by_text("NO CURRENT VERIFIED MATCHES", exact=True)).to_be_visible()
            expect(page.get_by_text("Fixture Test Mechanic", exact=True)).to_have_count(0)
            assert page.evaluate("window.__locationAudit.permissionChecks") == 0

            mode["value"] = "error"
            page.get_by_role("button", name="Patchlane home").click()
            page.get_by_role("button", name="Search verified mechanics by area").click()
            page.get_by_label("Area or landmark").fill("Gulberg")
            page.get_by_role("button", name="Search live directory").click()
            expect(page.get_by_text("Directory unavailable", exact=True)).to_be_visible(timeout=10000)
            expect(page.get_by_text("DIRECTORY TEMPORARILY UNAVAILABLE", exact=True)).to_be_visible()
            expect(page.get_by_role("button", name="Try again")).to_be_visible()
            assert page.evaluate("window.__locationAudit.permissionChecks") == 0

            context.close()
            browser.close()
            print("PASS  live Supabase-mode search, whitelist query, no-results/error states, and no-location/no-contact behavior (isolated mock only)")
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
