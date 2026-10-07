#!/usr/bin/env python3
"""Static regression checks for Android edge-to-edge and root safe-area layout."""
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "App.tsx").read_text(encoding="utf-8")
package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
android_gradle = (ROOT / "android" / "gradle.properties").read_text(encoding="utf-8")
app_gradle = (ROOT / "android" / "app" / "build.gradle").read_text(encoding="utf-8")
expo_android_plugin = (ROOT / "node_modules" / "expo-modules-core" / "android" / "ExpoModulesCorePlugin.gradle").read_text(encoding="utf-8")
manifest_path = ROOT / "android" / "app" / "src" / "main" / "AndroidManifest.xml"
theme_path = ROOT / "android" / "app" / "src" / "main" / "res" / "values" / "styles.xml"

safe_area_version = package.get("dependencies", {}).get("react-native-safe-area-context")
if safe_area_version != "~5.7.0":
    raise SystemExit(f"FAIL  expected Expo SDK 57 safe-area-context ~5.7.0, found {safe_area_version!r}")
if "SafeAreaProvider, SafeAreaView, initialWindowMetrics" not in source:
    raise SystemExit("FAIL  native safe-area provider, view, or initial metrics import is missing")
if not re.search(
    r"<SafeAreaProvider initialMetrics=\{initialWindowMetrics\}>\s*<PatchlaneApp\s*/>\s*</SafeAreaProvider>",
    source,
):
    raise SystemExit("FAIL  SafeAreaProvider with initial native metrics must wrap the whole app")

root_view = re.search(
    r"<SafeAreaView testID=\"safe-area-root\" style=\{styles\.safeArea\} "
    r"edges=\{\['top', 'bottom', 'left', 'right'\]\}>([\s\S]*?)</SafeAreaView>",
    source,
)
if not root_view:
    raise SystemExit("FAIL  root SafeAreaView must apply native top, bottom, and lateral insets")
root_children = root_view.group(1)
for required in ("<View style={styles.shell}>", "<Header ", "<KeyboardAvoidingView", "renderHome()", "renderArea()", "renderResults()", "renderProfile()", "renderRequest()", "renderListing()"):
    if required not in root_children:
        raise SystemExit(f"FAIL  safe-area root no longer wraps {required}")
if 'testID="app-header"' not in source:
    raise SystemExit("FAIL  app header regression test hook is missing")
if source.count("<ScrollView") != 6:
    raise SystemExit(f"FAIL  expected all six screens to retain independent scrolling, found {source.count('<ScrollView')}")
if "StatusBar style=\"dark\"" not in source:
    raise SystemExit("FAIL  status-bar icon contrast style changed unexpectedly")

if not re.search(r"(?m)^edgeToEdgeEnabled=true\s*$", android_gradle):
    raise SystemExit("FAIL  generated Android project must retain its edge-to-edge configuration")
if "targetSdkVersion rootProject.ext.targetSdkVersion" not in app_gradle:
    raise SystemExit("FAIL  Android app target SDK must remain controlled by Expo's SDK configuration")
if not re.search(r'targetSdkVersion project\.ext\.safeExtGet\("targetSdkVersion", 36\)', expo_android_plugin):
    raise SystemExit("FAIL  Expo SDK target API 36 default changed; revisit Android edge-to-edge behavior")
if "setDecorFitsSystemWindows(window, true)" in source:
    raise SystemExit("FAIL  app code must not disable Android edge-to-edge and mask missing inset handling")

android_ns = "{http://schemas.android.com/apk/res/android}"
manifest = ET.parse(manifest_path).getroot()
activity = manifest.find("./application/activity")
if activity is None or activity.get(android_ns + "windowSoftInputMode") != "adjustResize":
    raise SystemExit("FAIL  Android activity must preserve resize behavior for scrollable keyboard forms")
theme = ET.parse(theme_path).getroot()
app_theme = next((node for node in theme.findall("style") if node.get("name") == "AppTheme"), None)
if app_theme is None:
    raise SystemExit("FAIL  generated Android AppTheme is missing")
transparent = {
    node.get("name"): node.text
    for node in app_theme.findall("item")
    if node.get("name") in ("android:statusBarColor", "android:navigationBarColor")
}
if transparent != {
    "android:statusBarColor": "@android:color/transparent",
    "android:navigationBarColor": "@android:color/transparent",
}:
    raise SystemExit(f"FAIL  expected transparent system bars for edge-to-edge, found {transparent}")

print("PASS  Expo-compatible safe-area provider wraps every route; header and screen content respect dynamic system insets")
print("PASS  Android edge-to-edge, transparent bars, target SDK delegation, and keyboard resize configuration remain intact")
