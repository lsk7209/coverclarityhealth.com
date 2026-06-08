# Copy this file locally, replace every placeholder with production values, then run launch commands.
# Do not commit the copied file if it contains real credentials.

$env:SITE_ORIGIN = "https://your-production-domain.example"
$env:PUBLIC_CONTACT_EMAIL = "contact@your-production-domain.example"
$env:PUBLIC_CONTACT_URL = ""
$env:GA4_MEASUREMENT_ID = "G-XXXXXXXXXX"
$env:ADSENSE_PUBLISHER_ID = "pub-3050601904412736"

$env:GSC_SITE_URL = "https://your-production-domain.example/"
$env:GSC_SITEMAP_URL = "https://your-production-domain.example/sitemap.xml"

# Prefer GitHub repository secrets for CI. These local values are for manual verification only.
$env:GSC_CLIENT_JSON = Get-Content D:\env\adsense_oauth_client.json -Raw
$env:GSC_TOKEN_JSON = Get-Content D:\env\gsc_token.json -Raw

npm run launch:check-env
npm run launch:preflight -- --origin $env:SITE_ORIGIN --contact-email $env:PUBLIC_CONTACT_EMAIL --contact-url $env:PUBLIC_CONTACT_URL --ga4-measurement-id $env:GA4_MEASUREMENT_ID --adsense-publisher-id $env:ADSENSE_PUBLISHER_ID
npm run launch:prepare -- --origin $env:SITE_ORIGIN --contact-email $env:PUBLIC_CONTACT_EMAIL --contact-url $env:PUBLIC_CONTACT_URL --ga4-measurement-id $env:GA4_MEASUREMENT_ID --adsense-publisher-id $env:ADSENSE_PUBLISHER_ID --set-github-vars
npm run ready:production
