export const siteConfig = {
  name: "Cover Clarity Health",
  description:
    "Plain-language health coverage guides for comparing plan costs, enrollment windows, subsidy terms, and care access tradeoffs.",
  defaultUrl: "https://coverclarityhealth.com",
  adsenseClient: "ca-pub-3050601904412736",
  adsTxtLine: "google.com, pub-3050601904412736, DIRECT, f08c47fec0942fa0",
};

export function getSiteUrl() {
  return (process.env.SITE_URL || process.env.NEXT_PUBLIC_SITE_URL || siteConfig.defaultUrl).replace(/\/$/, "");
}

export function absoluteUrl(path = "/") {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${getSiteUrl()}${normalizedPath}`;
}

export function getAdsenseClient() {
  return process.env.NEXT_PUBLIC_ADSENSE_CLIENT || siteConfig.adsenseClient;
}
