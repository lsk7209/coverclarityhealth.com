import { absoluteUrl, siteConfig } from "@/lib/site";

function escapeXml(value) {
  return String(value).replace(/[<>&'"]/g, (char) => ({
    "<": "&lt;",
    ">": "&gt;",
    "&": "&amp;",
    "'": "&apos;",
    '"': "&quot;",
  })[char]);
}

export function GET() {
  const now = new Date().toUTCString();
  const body = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>${escapeXml(siteConfig.name)}</title>
    <link>${escapeXml(absoluteUrl("/"))}</link>
    <description>${escapeXml(siteConfig.description)}</description>
    <lastBuildDate>${escapeXml(now)}</lastBuildDate>
    <item>
      <title>Health coverage comparison checklist</title>
      <link>${escapeXml(absoluteUrl("/"))}</link>
      <guid>${escapeXml(absoluteUrl("/"))}</guid>
      <description>Premiums, deductibles, networks, prescriptions, and enrollment timing checks for plan comparison.</description>
      <pubDate>${escapeXml(now)}</pubDate>
    </item>
  </channel>
</rss>`;

  return new Response(body, {
    headers: {
      "content-type": "application/rss+xml; charset=utf-8",
      "cache-control": "public, max-age=3600",
    },
  });
}
