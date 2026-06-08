import json
import os

from apply_ads_txt import normalize_publisher_id
from apply_contact_channel import contact_block, normalize_email, normalize_url
from apply_ga4_measurement import normalize_measurement_id
from apply_site_origin import normalize_origin
from gsc_submit_sitemap import _json_from_env_or_file, normalize_site_url, normalize_sitemap_url


def check_value(label, fn, value):
    try:
        normalized = fn(value)
    except (SystemExit, ValueError, FileNotFoundError, json.JSONDecodeError, KeyError) as exc:
        message = str(exc)
        if isinstance(exc, SystemExit):
            message = str(exc.code)
        return {"name": label, "ok": False, "detail": message}
    return {"name": label, "ok": True, "detail": normalized}


def check_credentials():
    checks = []
    for name, fallback in [
        ("GSC_CLIENT_JSON", r"D:\env\adsense_oauth_client.json"),
        ("GSC_TOKEN_JSON", r"D:\env\gsc_token.json"),
    ]:
        try:
            _json_from_env_or_file(name, fallback)
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as exc:
            checks.append({"name": name, "ok": False, "detail": str(exc)})
        else:
            source = "environment" if os.getenv(name) else fallback
            checks.append({"name": name, "ok": True, "detail": f"valid JSON from {source}"})
    return checks


def audit():
    origin = os.getenv("SITE_ORIGIN", "")
    contact_email = os.getenv("PUBLIC_CONTACT_EMAIL", "")
    contact_url = os.getenv("PUBLIC_CONTACT_URL", "")

    checks = [
        check_value("SITE_ORIGIN", normalize_origin, origin),
        check_value("PUBLIC_CONTACT_EMAIL", normalize_email, contact_email),
        check_value("PUBLIC_CONTACT_URL", normalize_url, contact_url)
        if contact_url
        else {"name": "PUBLIC_CONTACT_URL", "ok": True, "detail": "not provided"},
        check_value("GA4_MEASUREMENT_ID", normalize_measurement_id, os.getenv("GA4_MEASUREMENT_ID", "")),
        check_value("ADSENSE_PUBLISHER_ID", normalize_publisher_id, os.getenv("ADSENSE_PUBLISHER_ID", "")),
        check_value("GSC_SITE_URL", normalize_site_url, os.getenv("GSC_SITE_URL", "")),
        check_value("GSC_SITEMAP_URL", normalize_sitemap_url, os.getenv("GSC_SITEMAP_URL", "")),
    ]
    checks.extend(check_credentials())

    if checks[1]["ok"] or checks[2]["detail"] != "not provided":
        try:
            contact_block(normalize_email(contact_email), normalize_url(contact_url))
        except SystemExit as exc:
            checks.append({"name": "PUBLIC_CONTACT_CHANNEL", "ok": False, "detail": str(exc.code)})
        else:
            checks.append({"name": "PUBLIC_CONTACT_CHANNEL", "ok": True, "detail": "public contact channel can be rendered"})
    else:
        checks.append({"name": "PUBLIC_CONTACT_CHANNEL", "ok": False, "detail": "PUBLIC_CONTACT_EMAIL or PUBLIC_CONTACT_URL is required"})

    return {
        "passed": all(item["ok"] for item in checks),
        "checks": checks,
    }


def main():
    report = audit()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["passed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
