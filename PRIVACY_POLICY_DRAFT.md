# Patchlane privacy policy — working draft

> **Draft only. Do not publish or submit this as the Play policy until the operator name, contact details, data-retention facts, and final disclosures have been confirmed and approved.** This draft describes the current Patchlane pilot implementation; it is not legal advice.

**Effective date:** `[confirm before publication]`

**Service operator / data controller:** `[legal name and address]`

**Privacy contact:** `[working email address]`

**Public policy URL:** `[host and approve a stable HTTPS URL]`

## What Patchlane does

Patchlane helps a rider search for motorcycle-puncture assistance by an area or landmark. The current pilot does not create rider accounts, request device location, run background location tracking, take bookings or payments, dispatch mechanics, or provide in-app messaging. If no live backend settings are present, it shows fictional sample data instead; sample requests and provider listings are not sent, saved, or published.

## Information used when searching

When the live pilot is enabled, Patchlane sends the area or landmark typed by the rider to its Supabase-hosted directory so it can find matching public listings. The app requests only a public listing's display name, public area, public phone number, verification date, verification expiry, and update time. The backend is configured in Mumbai, India. Patchlane does not ask for GPS coordinates or save a search-history record in the app.

The network request necessarily reveals connection details such as an IP address to the backend service. **The operator must confirm Supabase's applicable logs, retention period, access controls, and any subprocessors before publication; do not state a retention period until it is verified.** An area query may appear in service request logs according to the provider's configured logging.

## Public provider information and phone calls

A provider's public name, area, and phone number appear only after the provider has explicitly consented to public listing and contact, and the backend confirms current verification. If a rider taps **Open phone dialer**, Patchlane rechecks that provider through the consent-gated public view and then passes its public number to the device's phone app. The rider decides whether to place the call; Patchlane does not place or record the call and does not receive call content or call status. The operator must explain the data sources, consent process, verification/renewal procedure, and provider requests to correct or remove a listing.

## Analytics, advertising, and other collection

The current app code does not include an analytics, advertising, account, payment, or location-tracking SDK. No service-role key is embedded in the app. The operator must recheck the exact production build and any later SDK additions before completing Google Play's Data safety form.

## Data choices and requests

A rider can leave the search flow without creating an account. `[Confirm how a rider can contact the operator with privacy questions or requests, and how those requests are handled.]` Provider listing data can only be published and removed by an authorized operator workflow; the app does not provide provider self-service onboarding or deletion.

## Before this can become the published policy

The owner must supply and approve the operator's legal name, location/address if required, public privacy/support contact, request-handling process, verified service-log retention and subprocessors, provider-consent language, provider data sources, and the final disclosure of every runtime SDK and data flow. The production Play Data safety declarations must match the actual signed release build and backend configuration. Remove this section and all placeholders only after those facts have been confirmed.
