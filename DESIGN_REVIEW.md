# Patchlane design review

The rider flow is now organized around one clear action: search by area or landmark. The live header says **Pilot**, not “Live · verified”; the home and empty-results copy tell riders that the provider directory can be empty and that no booking or dispatch occurs. Search does not request device location. The no-results and network-failure states are separate and provide a recovery route.

The live provider profile exposes the public phone action only for rows returned by the current-verification and explicit-consent backend view. Immediately before opening the phone app, the client makes a fresh ID-scoped read from that same view; removal, revoked contact consent, expiry, and network failure all block the handoff. The rider—not Patchlane—chooses whether to place a call. Messaging, booking, payments, and dispatch are not represented as available features.

The local demonstration is clearly labelled `Demo · fictional`. Fake provider data, sample estimates, the request preview, and the shared mechanic/shop listing preview cannot be mistaken for real contact or signup. The listing form accepts only a zero-only sample phone, and no information is saved or sent.

A 1024 px square launcher icon and adaptive foreground reuse the Patchlane tyre-route mark and current warm-paper/charcoal/vermilion palette. Fresh 390 × 844 CSS-pixel web captures cover the demo screens and the pilot home/empty directory; they are QA captures, not native Android store screenshots. The screenshot set does not fabricate a real provider.

The responsive browser checks cover 360, 390, 430, and 768 CSS-pixel widths, no horizontal overflow, minimum 48 px visible button targets, and one primary action on action screens. The contrast audit checks ten text/background pairs; the minimum is **4.78:1**, above the WCAG AA normal-text threshold of 4.5:1. Physical-device and native dialer behavior still need verification with the internal APK.
