#!/usr/bin/env python3
"""Static checks for privacy-minimized Android release configuration."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
config = json.loads((ROOT / "app.json").read_text(encoding="utf-8"))["expo"]
package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
app_source = (ROOT / "App.tsx").read_text(encoding="utf-8")
android = config.get("android", {})
blocked = set(android.get("blockedPermissions", []))

if "expo-location" in package.get("dependencies", {}):
    raise SystemExit("FAIL  unused expo-location SDK must not be included")
if "expo-system-ui" not in package.get("dependencies", {}):
    raise SystemExit("FAIL  expo-system-ui is required by the configured native appearance")
if any((isinstance(plugin, str) and plugin == "expo-location") or (isinstance(plugin, list) and plugin and plugin[0] == "expo-location") for plugin in config.get("plugins", [])):
    raise SystemExit("FAIL  location permission plugin must not be configured")
if "ACCESS_COARSE_LOCATION" in app_source or "ACCESS_FINE_LOCATION" in app_source or "Location.requestForegroundPermissionsAsync" in app_source:
    raise SystemExit("FAIL  rider location collection code or permissions found in the app")
for permission in (
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.READ_EXTERNAL_STORAGE",
    "android.permission.WRITE_EXTERNAL_STORAGE",
    "android.permission.SYSTEM_ALERT_WINDOW",
    "android.permission.VIBRATE",
):
    if permission not in blocked:
        raise SystemExit(f"FAIL  unnecessary Android permission is not blocked: {permission}")
if android.get("permissions"):
    raise SystemExit("FAIL  app must not add Android permissions")
if config.get("android", {}).get("package") != "com.kominman.patchlane":
    raise SystemExit("FAIL  Android application id changed unexpectedly")
if android.get("allowBackup") is not False:
    raise SystemExit("FAIL  app data backup must remain disabled while the pilot is stateless")
if not isinstance(android.get("versionCode"), int) or android["versionCode"] < 3:
    raise SystemExit("FAIL  Android build number must be explicit and incremented for this install-review APK")
for asset in ("assets/icon.png", "assets/adaptive-icon.png"):
    if not (ROOT / asset).is_file():
        raise SystemExit(f"FAIL  missing launcher icon asset: {asset}")

manifest_path = ROOT / "android" / "app" / "src" / "main" / "AndroidManifest.xml"
if manifest_path.is_file():
    manifest = ET.parse(manifest_path).getroot()
    android_ns = "{http://schemas.android.com/apk/res/android}"
    tools_ns = "{http://schemas.android.com/tools}"
    active = []
    removed = set()
    for node in manifest.findall("uses-permission"):
        name = node.get(android_ns + "name")
        if node.get(tools_ns + "node") == "remove":
            removed.add(name)
        else:
            active.append(name)
    if active != ["android.permission.INTERNET"]:
        raise SystemExit(f"FAIL  unexpected active Android permissions: {active}")
    if not set(blocked) <= removed:
        raise SystemExit("FAIL  generated Android manifest is missing blocked-permission removal directives")

print("PASS  area-only app config, no location SDK, system UI setup, blocked unused permissions, stable package, explicit versionCode, and branded launcher icons")
