import { absoluteUrl } from "@/lib/site";

export default function sitemap() {
  const now = new Date();
  return ["/", "/about", "/privacy", "/feed.xml"].map((path) => ({
    url: absoluteUrl(path),
    lastModified: now,
    changeFrequency: path === "/" ? "weekly" : "monthly",
    priority: path === "/" ? 0.9 : 0.5,
  }));
}
