import json
from collections import defaultdict
from pathlib import Path

MAX_POSTS_PER_DAY = 2
QUEUE_PATH = Path("content/article-queue.json")

queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
by_day = defaultdict(list)

for article in queue:
    published_at = article.get("publishAt")
    if not published_at:
        raise SystemExit(f"missing publishAt: {article.get('slug', 'unknown')}")
    by_day[published_at[:10]].append(article["slug"])

overloaded_days = [
    {"day": day, "count": len(slugs), "slugs": slugs}
    for day, slugs in sorted(by_day.items())
    if len(slugs) > MAX_POSTS_PER_DAY
]

print(json.dumps({
    "articles": len(queue),
    "maxPostsPerDay": MAX_POSTS_PER_DAY,
    "days": len(by_day),
    "overloadedDays": overloaded_days,
}, indent=2))

raise SystemExit(1 if overloaded_days else 0)
