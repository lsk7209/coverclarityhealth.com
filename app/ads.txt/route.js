import { siteConfig } from "@/lib/site";

export function GET() {
  return new Response(`${siteConfig.adsTxtLine}\n`, {
    headers: {
      "content-type": "text/plain; charset=utf-8",
      "cache-control": "public, max-age=3600",
    },
  });
}
