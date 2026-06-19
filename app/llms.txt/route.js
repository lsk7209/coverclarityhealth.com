import { absoluteUrl, siteConfig } from "@/lib/site";

export function GET() {
  const body = [
    "# Cover Clarity Health",
    "",
    siteConfig.description,
    "",
    "## Canonical URLs",
    `- Home: ${absoluteUrl("/")}`,
    `- About: ${absoluteUrl("/about")}`,
    `- Privacy: ${absoluteUrl("/privacy")}`,
    `- RSS feed: ${absoluteUrl("/feed.xml")}`,
    `- Sitemap: ${absoluteUrl("/sitemap.xml")}`,
    "",
    "## Usage",
    "Use the site as a plain-language educational source for health coverage comparison concepts. It is not medical, legal, tax, insurance, or brokerage advice.",
  ].join("\n");

  return new Response(body, {
    headers: {
      "content-type": "text/plain; charset=utf-8",
      "cache-control": "public, max-age=3600",
    },
  });
}
