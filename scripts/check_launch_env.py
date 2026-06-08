import json
import os
from urllib.parse import urlsplit

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


def check_url_alignment(origin_check, gsc_site_check, sitemap_check):
    name = "LAUNCH_URL_ALIGNMENT"
    if not (origin_check["ok"] and gsc_site_check["ok"] and sitemap_check["ok"]):
        return {"name": name, "ok": False, "detail": "SITE_ORIGIN, GSC_SITE_URL, and GSC_SITEMAP_URL must all be valid first"}

    origin = origin_check["detail"]
    gsc_site_url = gsc_site_check["detail"]
    sitemap_url = sitemap_check["detail"]
    origin_host = urlsplit(origin).hostname or ""
    sitemap_host = urlsplit(sitemap_url).hostname or ""

    if sitemap_host.lower() != origin_host.lower():
        return {"name": name, "ok": False, "detail": "GSC_SITEMAP_URL must use the same host as SITE_ORIGIN"}
    if sitemap_url.rstrip("/") != f"{origin}/sitemap.xml":
        return {"name": name, "ok": False, "detail": "GSC_SITEMAP_URL must be SITE_ORIGIN + /sitemap.xml"}
    if gsc_site_url.startswith("sc-domain:"):
        domain = gsc_site_url.removeprefix("sc-domain:").strip().lower()
        if domain != origin_host.lower():
            return {"name": name, "ok": False, "detail": "GSC_SITE_URL sc-domain property must match SITE_ORIGIN host"}
    elif gsc_site_url.rstrip("/") != origin:
        return {"name": name, "ok": False, "detail": "GSC_SITE_URL URL-prefix property must match SITE_ORIGIN"}

    return {"name": name, "ok": True, "detail": "SITE_ORIGIN, GSC_SITE_URL, and GSC_SITEMAP_URL are aligned"}


def audit():
    origin = os.getenv("SITE_ORIGIN", "")
    contact_email = os.getenv("PUBLIC_CONTACT_EMAIL", "")
    contact_url = os.getenv("PUBLIC_CONTACT_URL", "")

    origin_check = check_value("SITE_ORIGIN", normalize_origin, origin)
    contact_email_check = check_value("PUBLIC_CONTACT_EMAIL", normalize_email, contact_email)
    contact_url_check = (
        check_value("PUBLIC_CONTACT_URL", normalize_url, contact_url)
        if contact_url
        else {"name": "PUBLIC_CONTACT_URL", "ok": True, "detail": "not provided"}
    )
    ga4_check = check_value("GA4_MEASUREMENT_ID", normalize_measurement_id, os.getenv("GA4_MEASUREMENT_ID", ""))
    adsense_check = check_value("ADSENSE_PUBLISHER_ID", normalize_publisher_id, os.getenv("ADSENSE_PUBLISHER_ID", ""))
    gsc_site_check = check_value("GSC_SITE_URL", normalize_site_url, os.getenv("GSC_SITE_URL", ""))
    sitemap_check = check_value("GSC_SITEMAP_URL", normalize_sitemap_url, os.getenv("GSC_SITEMAP_URL", ""))

    checks = [
        origin_check,
        contact_email_check,
        contact_url_check,
        ga4_check,
        adsense_check,
        gsc_site_check,
        sitemap_check,
        check_url_alignment(origin_check, gsc_site_check, sitemap_check),
    ]
    checks.extend(check_credentials())

    if contact_email_check["ok"] or contact_url_check["detail"] != "not provided":
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
