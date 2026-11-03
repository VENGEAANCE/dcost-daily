# Signup reliability and brand consistency

The newsletter iframe previously depended entirely on a third-party request and had large fixed padding cropped by the host. A blocked or delayed frame left a large empty area and an inconspicuous fallback.

The signup section now retains a visible, branded link to the publication's hosted signup page in the initial HTML, including when JavaScript or the embed is unavailable. The inline form remains Beehiiv-hosted, with its validation and consent behavior intact. It uses the current provider-generated v3 loader without negative-margin cropping. The hosted fallback link carries source/placement UTM parameters. Beehiiv's official v3 loader manages inline-form sizing, challenge states and inbound attribution. A real conversion was not submitted during testing.

The public Beehiiv form was updated through its editor: black surface, dark email field, rounded controls and a bold Helvetica button. Helvetica is the supported sans-serif fallback because Barlow is absent from the provider's font picker. Duplicate embed headings and 80px padding were removed. The publication logo and description now use the same battery identity and offering as the site.

The site's favicon uses that battery mark, and all page footers use the established name without “working name.” Generated footers and cache versions were changed in the generator and rebuilt.

Validation: real Beehiiv form at 1280 and 390 widths, email field fits the frame, hosted fallback remains visible with Beehiiv blocked, and the fallback URL is correct. No subscriber was created. Existing route, calculator, charger filter, reading persistence/focus and fetch-error tests pass at both widths.

Screenshots: [1280](newsletter-1280.png), [390](newsletter-390.png), [blocked embed at 390](newsletter-blocked-390.png).
The newsletter hash target also follows asynchronous digest layout: a resize observer keeps the explicitly requested signup section in place as lazy thumbnails resolve. Any user wheel, touch, pointer, keyboard or hash navigation disconnects it immediately. A delayed-digest regression check passes at both widths and verifies that manual navigation is not pulled back to signup by a later layout change.
