# Patchlane Google Play readiness

**Patchlane is not ready for a public Play release.** The app has been corrected and a review APK has been built, but the public directory has no real listings and there are no provider operations or rider-support processes. Publishing an empty puncture-help directory as an operating service would misrepresent what riders can use today.

## Changes completed

The live status now says **Pilot**, the empty-directory and offline states are distinct, and the sample mechanic/shop path appears only in the clearly labelled fictional demo. Demo requests cannot pretend a mechanic is waiting; sample provider details cannot be saved or submitted. In live mode, a current, consented listing may open the system dialer only after the rider taps. Immediately before that handoff the app re-reads the provider by ID from the same consent-gated public view; expiry, removal, revoked consent, and network errors all block the dialer.

Rider location code and the unused Expo location SDK have been removed. The Android prebuild has only `INTERNET` as an active permission; location, storage, overlay, and vibration permissions are explicitly removed during manifest merge. App-data backup is disabled. The Android package remains `com.kominman.patchlane`, app version `5.0.0`, Android build number `2`, Expo SDK 57 resolves target API **36**, and the app now has a source-controlled launcher/adaptive icon.

The updated checks cover the backend contract, native configuration, demo and pilot browser flows, revoked/expired listings and failed rechecks, empty/error recovery, responsive layouts, and minimum button touch targets. The refreshed screenshot captures are from the web renderer; they are not native-device or store-listing screenshots. The accessibility contrast audit's minimum is **4.78:1**.

## What still blocks launch

**Providers and operations:** the live Supabase view returned an empty array, and the database contains zero providers and zero verification events. No provider consent or evidence was invented. The owner needs a legitimate provider source, real opt-in, verification and renewal procedures, an accountable operator, and a way to support riders and correct or remove inaccurate listings. The current app is an area-based directory, not a booking or dispatch service.

**Privacy and store listing:** the production privacy policy URL and operator contact are unknown, and retention of backend request logs must be confirmed. The policy draft contains placeholders and is not publishable. Complete the Data safety form from the final signed build and confirmed backend/SDK behavior. Prepare an accurate store title, description, service area, content rating, feature graphic, and screenshots captured from an actual Android build. Do not reuse the web QA captures as if they were device screenshots.

**Testing:** install and verify the new internal APK on physical Android devices across supported screen sizes and Android versions. Confirm the system-dialer handoff, keyboard/focus behavior, network-empty/offline states, and the approved Play listing/policy with the operator. [Open the completed EAS internal build](https://expo.dev/accounts/kominman/projects/patchlane-puncture-demo-v5/builds/d1c3274f-f7ca-45ad-8502-cbeb50f0a2af) or [download the APK](https://expo.dev/artifacts/eas/y1r-VeYOEV31b-9Swl12ay2GquDhlVCE-SOQQt5BiEQ.apk). If the Play account is a personal account created after 2023-11-13, Google requires a closed test with at least 12 opted-in testers continuously for 14 days before the account may apply for production access; check the owner's account eligibility.

## Android and dependency status

Google Play's current policy requires new apps and app updates to target API 36 or higher from 2026-08-31 ([official target API rules](https://support.google.com/googleplay/android-developer/answer/11926878?hl=en)). Expo's current prebuild resolves target API 36. The EAS `preview` profile produced the linked **internal APK**; it did not publish or submit the app to Google Play.

The current npm audit reports **15 high findings and no moderate findings** after a scoped, tested UUID 11.1.1 update for Xcode's single `uuid.v4()` use. npm's unforced fix does not clear the Expo/Metro chain. The reviewed [braces advisory](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) says all versions through 3.0.3 are affected and no patched version is published; the [node-forge advisory](https://github.com/advisories/GHSA-86w9-cpqp-85rv) likewise lists versions through 1.4.0 with no patch. Do not use `npm audit fix --force`: npm proposes downgrading the app from Expo 57 to Expo 44 / React Native 0.72. Recheck these advisories when upstream fixes are released and run the full test suite after any update.

## Submission and approval

Google Play requires an accurate Data safety declaration and privacy-policy link ([Data safety guidance](https://support.google.com/googleplay/android-developer/answer/10787469?hl=en)); policy and content declarations are part of app review ([policy setup](https://support.google.com/googleplay/android-developer/answer/9859455?hl=en)). The app must also provide stable and meaningful functionality ([functionality policy](https://support.google.com/googleplay/android-developer/answer/9898783?hl=en)). The official guidance says very limited-functionality apps are not allowed, so launch should wait until the directory contains real service coverage and the service is operational.

Before any public submission, show the owner the exact application ID and version, the final signed permissions and target API, country/availability and pricing, complete store listing and images, content rating/audience/ads answers, provider and contact disclosures, privacy-policy URL/text, Data safety answers, test track/rollout, and the final APK/AAB. Do not publish or submit an official record until the owner has reviewed and explicitly approved that exact payload. See [`PRIVACY_POLICY_DRAFT.md`](./PRIVACY_POLICY_DRAFT.md) for the current unapproved policy draft.
