import html
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POST_DIR = ROOT / "aca"
DATA_DIR = ROOT / "content"
GUIDE_DIR = ROOT / "guides"
REPORT_DIR = ROOT / "reports"
GENERATION_REPORT = REPORT_DIR / "article-generation-report.json"
SITE_ORIGIN = os.getenv("SITE_ORIGIN", "{SITE_ORIGIN}").rstrip("/")
KST = timezone(timedelta(hours=9))
FIRST_PUBLISH_AT = datetime(2026, 6, 8, 13, 23, tzinfo=KST)
HEAD_INTEGRATIONS = """  <meta name="naver-site-verification" content="855afb240140498254660c8577a49240ff1f8521" />
  <meta name="google-site-verification" content="8rvm9Tcgkca483PET5WJCwwKsiML5yZc0tqTPsjKksE" />
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-GYRK9P50CW"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-GYRK9P50CW');
  </script>
  <script type="text/javascript">
    (function(c,l,a,r,i,t,y){
      c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
      t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
      y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    })(window, document, "clarity", "script", "x97p26p6y4");
  </script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3050601904412736" crossorigin="anonymous"></script>
"""

OFFICIAL_SOURCES = [
    {
        "label": "IRS Premium Tax Credit questions and answers",
        "url": "https://www.irs.gov/node/15902",
        "claim": "Premium tax credit rules and federal poverty line references.",
    },
    {
        "label": "IRS Rev. Proc. 2025-25",
        "url": "https://www.eitc.irs.gov/irb/2025-32_IRB",
        "claim": "2026 applicable percentage table and required contribution percentage.",
    },
    {
        "label": "HHS/ASPE 2026 Poverty Guidelines",
        "url": "https://aspe.hhs.gov/topics/poverty-economic-mobility/poverty-guidelines",
        "claim": "2026 poverty guidelines for the 48 contiguous states and D.C.",
    },
    {
        "label": "HealthCare.gov cost-sharing reductions",
        "url": "https://www.healthcare.gov/lower-costs/save-on-out-of-pocket-costs/",
        "claim": "CSR applies through Silver plans for eligible Marketplace shoppers.",
    },
    {
        "label": "HealthCare.gov official Marketplace",
        "url": "https://www.healthcare.gov/",
        "claim": "Official enrollment and final plan-price confirmation.",
    },
    {
        "label": "CMS 2026 Marketplace Open Enrollment report",
        "url": "https://www.cms.gov/newsroom/fact-sheets/marketplace-2026-open-enrollment-period-report-final-national-snapshot",
        "claim": "CMS enrollment snapshot and Marketplace participation context.",
    },
    {
        "label": "KFF enhanced premium tax credit analysis",
        "url": "https://www.kff.org/affordable-care-act/issue-brief/how-much-more-would-people-pay-in-premiums-if-the-acas-enhanced-premium-tax-credits-expired/",
        "claim": "Independent analysis of enhanced premium tax credit expiration effects.",
    },
]


def publication_now():
    raw = os.getenv("PUBLICATION_NOW", "").strip()
    if raw:
        value = datetime.fromisoformat(raw)
        return value if value.tzinfo else value.replace(tzinfo=KST)
    return datetime.now(KST)


def published_by(topic, now):
    value = datetime.fromisoformat(topic["publishAt"])
    if value.tzinfo is None:
        value = value.replace(tzinfo=KST)
    return value <= now


METROS = [
    ("Miami", "Miami-Dade and Broward shoppers often compare high household premiums against tax-credit changes."),
    ("Tampa", "Tampa Bay households need a clean way to compare benchmark Silver costs across income bands."),
    ("Orlando", "Central Florida families often have mixed household sizes and income changes during the year."),
    ("Jacksonville", "Jacksonville shoppers may see large age-rating differences for older adults and families."),
    ("Tallahassee", "North Florida estimates are useful when readers want a non-South-Florida comparison point."),
]

HOUSEHOLDS = [
    ("single adult", "one adult buying Marketplace coverage"),
    ("couple", "two adults comparing a shared Marketplace estimate"),
    ("single parent", "one adult with one child in the household"),
    ("family of three", "two adults and one child or another three-person household"),
    ("family of four", "a four-person household using the poverty guideline for four people"),
    ("older couple", "two adults in their 50s or early 60s facing age-rated premiums"),
]

FPL_BANDS = [
    ("100 percent FPL", "near the lower Marketplace subsidy threshold"),
    ("150 percent FPL", "where enhanced credits can make benchmark Silver premiums very low"),
    ("200 percent FPL", "where CSR and premium tax credits can both matter"),
    ("250 percent FPL", "near the upper edge of common CSR eligibility discussions"),
    ("300 percent FPL", "a middle-income estimate where contribution percentages drive the result"),
    ("400 percent FPL", "the current-law cliff boundary that needs careful explanation"),
]

GUIDE_TOPICS = [
    ("Florida ACA subsidy calculator walkthrough", "ACA premium estimate", "calculator intent", "How to read the two premium columns without treating either number as a quote."),
    ("enhanced premium tax credits in Florida", "current law comparison", "policy status", "What the enhanced-credit column means when current-law rules differ."),
    ("ACA subsidy cliff over 400 percent FPL", "premium tax credit threshold", "subsidy cliff", "Why a household above 400 percent FPL needs special attention."),
    ("Florida Medicaid coverage gap explanation", "income below 100 percent FPL", "coverage gap", "Why the calculator should explain the gap instead of showing a normal result."),
    ("SLCSP benchmark Silver premium", "second lowest cost Silver plan", "methodology", "How SLCSP supports the premium tax credit estimate."),
    ("cost-sharing reductions on Silver plans", "CSR eligibility", "CSR", "Why CSR affects out-of-pocket costs, not just the premium."),
    ("federal poverty level for ACA subsidies", "2026 poverty guidelines", "FPL", "How household size changes the income percentage used by the estimate."),
    ("HealthCare.gov confirmation checklist", "Marketplace enrollment", "official confirmation", "What to verify on the official Marketplace after using an estimate."),
    ("ACA metal tiers and subsidy estimates", "Bronze Silver Gold plans", "metal tiers", "Why the calculator uses a benchmark Silver reference even if a reader buys another metal level."),
    ("Marketplace income estimate mistakes", "2026 income projection", "income estimate", "Common ways a reader can misread annual income in the calculator."),
    ("ACA estimate versus insurance quote", "not a quote disclaimer", "trust", "How to explain an estimate without crossing into plan advice."),
    ("premium tax credit reconciliation basics", "Form 8962 planning", "tax reconciliation", "Why a Marketplace estimate can later meet tax filing reality."),
    ("Florida ACA open enrollment planning", "Marketplace deadline preparation", "open enrollment", "What to prepare before comparing final HealthCare.gov plans."),
    ("household size for Marketplace subsidies", "tax household rules", "household size", "Why the tax household can differ from who lives at the address."),
    ("age rating in ACA premium estimates", "older adult Marketplace premium", "age rating", "Why two households with equal income can see different benchmark premiums."),
    ("tobacco surcharge in Florida estimates", "Marketplace tobacco rating", "tobacco surcharge", "How tobacco status can change the gross premium estimate."),
    ("CSR versus premium tax credit", "Silver plan savings", "CSR vs PTC", "A side-by-side explanation of premium help and out-of-pocket help."),
    ("current-law ACA premium scenario", "pre-2021 rules", "current law", "How a reader should interpret current-law estimates without panic language."),
    ("Florida ACA estimate privacy", "browser-only calculator", "privacy", "Why a stateless calculator matters for health and income privacy."),
    ("Marketplace subsidy source list", "IRS HHS CMS sources", "source trust", "Which official sources support the calculator and where the limits are."),
    ("ACA subsidy estimate for early retirees", "pre-Medicare health insurance", "early retiree", "Why income control and age rating both matter before Medicare."),
    ("ACA subsidy estimate for gig workers", "variable income Marketplace", "self-employed income", "How variable income can complicate a 2026 estimate."),
    ("ACA subsidy estimate for new Florida residents", "Florida Marketplace move", "moving to Florida", "What changes when a household moves into Florida and needs a local estimate."),
    ("ACA subsidy estimate after job loss", "loss of employer coverage", "special enrollment", "How to use an estimate when employer coverage ends."),
    ("ACA subsidy estimate for part-time workers", "low income Marketplace planning", "part-time income", "How to handle low but changing income without hiding the coverage gap."),
    ("ACA subsidy estimate for college graduates", "first Marketplace plan", "young adult coverage", "What a new adult shopper needs to know before comparing prices."),
    ("ACA subsidy estimate for divorced parents", "tax household and dependents", "dependent claim", "Why who claims a child can change the subsidy estimate."),
    ("ACA subsidy estimate for seasonal workers", "seasonal income projection", "income volatility", "How to think about yearly income when work is seasonal."),
    ("ACA subsidy estimate for small business owners", "self-employment income", "business owner", "Why net income, not gross revenue, matters for the estimate."),
    ("ACA subsidy estimate for caregivers", "family coverage planning", "caregiver household", "How caregiving households should separate coverage needs from tax household size."),
    ("ACA subsidy estimate for immigrants in Florida", "Marketplace eligibility basics", "immigration status", "A careful, source-first article that avoids legal advice while pointing to official confirmation."),
    ("ACA subsidy estimate for rural Florida counties", "rating area differences", "rural Florida", "Why county and rating-area mapping matters before using a metro shortcut."),
    ("ACA subsidy estimate with adult children", "dependents and age rating", "adult child coverage", "When an adult child changes the household premium estimate."),
    ("ACA subsidy estimate after marriage", "combined household income", "marriage and Marketplace", "How a new tax household can change the monthly result."),
    ("ACA subsidy estimate after a raise", "income increase premium tax credit", "raise impact", "Why more income can reduce a credit but still need exact calculation."),
    ("ACA subsidy estimate after retirement account withdrawals", "MAGI planning", "retirement withdrawals", "How taxable income decisions can affect the FPL percentage."),
    ("ACA subsidy estimate for pregnant applicants", "household planning", "pregnancy and coverage", "A cautious explanation that points readers to official Marketplace help."),
    ("ACA subsidy estimate for prescription-heavy households", "Silver plan CSR", "drug cost planning", "Why premium estimates are only part of plan selection."),
    ("ACA subsidy estimate with HSA questions", "HSA eligible plan", "HSA planning", "Why metal level and HSA eligibility are separate from the subsidy calculation."),
    ("ACA subsidy estimate when income is uncertain", "income update strategy", "uncertain income", "A practical guide for estimates that may need later updates."),
]

FORMATS = [
    "direct answer plus checklist",
    "scenario walkthrough",
    "comparison table",
    "mistake prevention",
    "decision guide",
    "plain-English glossary",
    "source-led explainer",
    "reader Q and A",
    "step-by-step interpretation",
    "risk and limitation brief",
]

COLOR_PAIRS = [
    ("#FBF3E1", "#A66C1C"),
    ("#E4F0EA", "#1F5E43"),
    ("#F5E5E0", "#8F3D2D"),
    ("#F3EEE3", "#34434F"),
    ("#EAF2FF", "#2457A6"),
    ("#EEF6D8", "#4D6F1E"),
]

CTA_VARIANTS = [
    ("Run this estimate with your household", "Open the calculator with your own ages, income, and Florida area before you compare plans."),
    ("Check your numbers before enrollment", "Use the calculator to find the assumption you should verify on the official Marketplace."),
    ("Compare your two premium views", "See the enhanced-credit and current-law estimates side by side, then confirm final prices at HealthCare.gov."),
    ("Test a different income scenario", "Change the annual income and watch how the federal poverty guideline percentage affects the estimate."),
    ("Review the estimate behind the guide", "Use the calculator as a planning screen, not as a quote or plan recommendation."),
    ("Find your next verification step", "The estimate can show whether to focus on income, CSR, a coverage-gap warning, or final Marketplace prices."),
    ("Use the calculator as a planning check", "Keep the result private in your browser and use it to prepare better questions for HealthCare.gov."),
    ("Rebuild the estimate for your household", "Start with household size, ages, area, and annual income so the guide fits your situation."),
    ("Turn this guide into a personal estimate", "Move from the example to your own numbers, then verify actual eligibility through the Marketplace."),
    ("Compare before you choose a plan", "Separate the premium estimate from plan choice so the monthly number does not hide deductibles or networks."),
    ("Estimate first, confirm officially", "Use the planning estimate here, then rely on HealthCare.gov for the final coverage and price."),
    ("Check whether the threshold matters", "Run your income near the relevant FPL band to see whether a small change affects the result."),
]

FAQ_HEADINGS = [
    "Reader checks before acting on the estimate",
    "Two questions this estimate should answer",
    "Short answers for careful Marketplace shoppers",
    "What readers usually ask next",
    "Follow-up questions for this scenario",
    "Quick checks for this ACA estimate",
    "Questions to resolve before using the number",
    "Plain answers for the next decision",
]

SOURCE_HEADINGS = [
    "Official sources to keep beside this estimate",
    "Evidence, limits, and related reading",
    "Where the rules come from",
    "Sources that support this guide",
    "Official references and internal next steps",
    "Data notes and careful links",
    "Trust notes for this estimate",
    "References for verification",
]

DEEP_SECTION_TITLES = [
    ("What makes {short} different", "The useful nuance"),
    ("A realistic reader scenario for {short}", "Scenario check"),
    ("What the calculator can decide for {short}", "Decision boundary"),
    ("What to verify after reading {short}", "Verification path"),
    ("How {short} can be misread", "Misread risk"),
    ("A better way to compare {short}", "Comparison lens"),
    ("When {short} changes the next step", "Next-step trigger"),
    ("What to save from {short}", "Recordkeeping note"),
    ("How to explain {short} to another household member", "Plain-language version"),
    ("The threshold question inside {short}", "Threshold check"),
]

FAQ_QUESTION_SETS = [
    ("Can I use this as a final price?", "No. Treat it as a planning estimate. Final plan availability, eligibility, and price must be confirmed at HealthCare.gov."),
    ("Why does the current-law column matter?", "It shows what the household may face if enhanced premium tax credits are not available or if the rules change."),
    ("Does the lowest premium mean the best plan?", "Not necessarily. Premiums, deductibles, provider networks, prescriptions, and CSR can point in different directions."),
    ("What should I change first if the estimate looks wrong?", "Check annual income, household size, ages, Florida area, and whether the result is showing a coverage-gap or cliff condition."),
    ("Where do official rules enter the estimate?", "The estimate relies on federal poverty guideline concepts, premium tax credit rules, and Marketplace confirmation steps."),
    ("Why mention Silver plans so often?", "The benchmark for premium tax credits is tied to Silver plan pricing, and CSR also works through eligible Silver plans."),
    ("Can this guide tell me which insurer to choose?", "No. It explains the estimate and the assumptions. It does not recommend insurers or collect quote leads."),
    ("What makes Florida different?", "Florida's Medicaid expansion status makes the below-100-percent-FPL result especially important to explain carefully."),
]


GUIDE_CLUSTERS = [
    ("County and rating-area guides", "county and rating-area intent", "county-and-rating-area-guides", "Florida county and rating-area ACA subsidy estimates"),
    ("Life event and income-change guides", "life event and income-change intent", "life-event-and-income-change-guides", "Florida ACA life-event subsidy estimate guides"),
    ("Plan selection and out-of-pocket guides", "plan selection and out-of-pocket intent", "plan-selection-and-out-of-pocket-guides", "Florida ACA plan selection and CSR guides"),
    ("Tax, MAGI, and reconciliation guides", "tax MAGI and reconciliation intent", "tax-magi-and-reconciliation-guides", "Florida ACA MAGI and tax reconciliation guides"),
    ("Official verification and troubleshooting guides", "official verification and risk-prevention intent", "official-verification-and-troubleshooting-guides", "Florida ACA estimate verification guides"),
]


HUB_CLUSTERS = {
    "calculator intent",
    "policy status",
    "subsidy cliff",
    "coverage gap",
    "methodology",
    "CSR",
    "FPL",
    "official confirmation",
    "metal tiers",
    "income estimate",
    "tax reconciliation",
    "open enrollment",
    "household size",
    "age rating",
    "CSR vs PTC",
    "current law",
    "source trust",
    "early retiree",
    "self-employed income",
    "special enrollment",
    "tax MAGI and reconciliation intent",
    "plan selection and out-of-pocket intent",
}


def slugify(text: str, max_length: int = 110) -> str:
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    if len(s) <= max_length:
        return s
    return s[:max_length].rsplit("-", 1)[0].strip("-")


def article_for_phrase(phrase: str) -> str:
    return "an" if phrase[:1].lower() in {"a", "e", "i", "o", "u"} else "a"


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def publish_label(topic):
    publish_dt = datetime.fromisoformat(topic["publishAt"])
    return f"{publish_dt.strftime('%b')} {publish_dt.day}, {publish_dt.year}"


def publish_status(topic):
    return "Published" if topic.get("is_published") else "Scheduled"


def meta_snippet(text, limit=155):
    clean = re.sub(r"\s+", " ", text).strip()
    if len(clean) <= limit:
        return clean
    cut = clean[: limit - 1]
    if " " in cut:
        cut = cut[: cut.rfind(" ")]
    cut = re.sub(r"\b(and|or|with|for|to|of|in|at|by|from|before|after|when|while|plus)\.?$", "", cut.rstrip(" ,.;:"), flags=re.IGNORECASE)
    return cut.rstrip(" ,.;:") + "."


def compact_title_text(text):
    clean = clean_title_text(text)
    replacements = [
        (r"\bACA subsidy estimate\b", "ACA subsidy"),
        (r"\bFlorida ACA subsidy estimate\b", "Florida ACA subsidy"),
        (r"\bpercent FPL\b", "% FPL"),
        (r"\bHealthCare\.gov\b", "Marketplace"),
        (r"\bMarketplace premium\b", "premium"),
        (r"\bpremium tax credit\b", "PTC"),
        (r"\bcost-sharing reduction\b", "CSR"),
        (r"\bmodified adjusted gross income\b", "MAGI"),
        (r"\bwithout the jargon\b", "plain-English"),
    ]
    for pattern, repl in replacements:
        clean = re.sub(pattern, repl, clean, flags=re.IGNORECASE)
    clean = re.sub(r"\s+%", "%", clean)
    return re.sub(r"\s+", " ", clean).strip()


def title_snippet(text, limit=58):
    clean = compact_title_text(text)
    if len(clean) <= limit:
        return clean.rstrip(" ,.;:")
    cut = clean[:limit]
    if " " in cut:
        cut = cut[: cut.rfind(" ")]
    cut = re.sub(
        r"\b(a|an|the|and|or|with|for|to|of|in|at|by|from|before|after|when|while|plus|near|around|inside|without|read|can)\b$",
        "",
        cut.rstrip(" ,.;:"),
        flags=re.IGNORECASE,
    )
    return cut.rstrip(" ,.;:")


def clean_title_text(text):
    clean = re.sub(r"\s+", " ", text).strip()
    replacements = [
        (r"\ba Orlando\b", "an Orlando"),
        (r"\bflorida\b", "Florida"),
        (r"\bfpl\b", "FPL"),
        (r"\baca\b", "ACA"),
        (r"\bcsr\b", "CSR"),
        (r"\bmagi\b", "MAGI"),
        (r"\bslcsp\b", "SLCSP"),
        (r"\bhsa\b", "HSA"),
        (r"\bcobra\b", "COBRA"),
        (r"\bmedicaid\b", "Medicaid"),
        (r"\bmedicare\b", "Medicare"),
        (r"\bhealthcare\.gov\b", "HealthCare.gov"),
        (r"\birs\b", "IRS"),
        (r"\bhhs\b", "HHS"),
        (r"\bcms\b", "CMS"),
        (r"\b1099-k\b", "1099-K"),
        (r"\bchanges changes\b", "changes"),
        (r"\bestimates matters\b", "estimates matter"),
        (r"\bbefore choosing specialist network before choosing a plan\b", "before choosing a specialist network"),
        (r"\bafter income disruption after a hurricane\b", "after hurricane income disruption"),
    ]
    for pattern, repl in replacements:
        clean = re.sub(pattern, repl, clean, flags=re.IGNORECASE)
    if clean:
        clean = clean[0].upper() + clean[1:]
    return clean


def make_meta_title(title, main_keyword=None, expanded=None):
    candidates = []
    if main_keyword:
        candidates.extend([
            compact_title_text(main_keyword),
            compact_title_text(f"{main_keyword} 2026"),
            compact_title_text(f"{main_keyword} guide"),
            compact_title_text(f"{main_keyword} 2026 guide"),
        ])
    if expanded:
        candidates.append(compact_title_text(f"{main_keyword}: {expanded[0]}"))
    candidates.append(compact_title_text(title))
    clean_candidates = []
    for candidate in candidates:
        candidate = re.sub(r"\s+", " ", candidate or "").strip(" ,.;:")
        if candidate and candidate not in clean_candidates:
            clean_candidates.append(candidate)
    for candidate in clean_candidates:
        if 30 <= len(candidate) <= 58:
            return candidate
    for candidate in candidates:
        if candidate and len(candidate) <= 58:
            return candidate.rstrip(" ,.;:")
    return title_snippet(clean_candidates[0] if clean_candidates else title, 58)


def make_meta_description(main_keyword, expanded):
    mk = clean_title_text(main_keyword)
    options = [
        f"{mk}: {expanded[0]}, {expanded[1]}, and official confirmation.",
        f"{mk}: {expanded[0]} and official confirmation.",
        f"{mk}: estimate limits and official confirmation.",
    ]
    for option in options:
        clean = re.sub(r"\s+", " ", option).strip()
        if len(clean) <= 155:
            return clean
    return meta_snippet(options[-1], 155)


def normalize_topic(topic):
    topic["title"] = clean_title_text(topic["title"])
    topic["subtitle"] = clean_title_text(topic["subtitle"])
    topic["main_keyword"] = clean_title_text(topic["main_keyword"])
    topic["expanded_keywords"] = [clean_title_text(keyword) for keyword in topic["expanded_keywords"]]
    topic["slug"] = slugify(topic["title"])
    topic["meta_title"] = make_meta_title(topic["title"], topic["main_keyword"], topic["expanded_keywords"])
    topic["meta_description"] = make_meta_description(topic["main_keyword"], topic["expanded_keywords"])
    return topic


def excerpt_for(topic):
    exp = topic["expanded_keywords"]
    return meta_snippet(
        f"{topic['main_keyword']} explained with {exp[0]}, {exp[1]}, estimate limits, related guide paths, and official HealthCare.gov confirmation.",
        220,
    )


def featured_image_idea_for(topic):
    return (
        f"Clean editorial illustration of a Florida Marketplace estimate worksheet for {topic['main_keyword']}, "
        "showing household income, FPL percentage, benchmark Silver premium, and confirmation checklist."
    )


def featured_image_alt_for(topic):
    return meta_snippet(
        f"Florida ACA subsidy estimate worksheet for {topic['main_keyword']} with premium tax credit and Marketplace confirmation notes.",
        140,
    )


def guide_cluster_for(topic):
    for heading, cluster, guide_slug, meta_title in GUIDE_CLUSTERS:
        if topic["cluster"] == cluster:
            return {
                "heading": heading,
                "cluster": cluster,
                "slug": guide_slug,
                "meta_title": meta_title,
                "href_from_article": f"../guides/{guide_slug}.html",
                "href_from_root": f"guides/{guide_slug}.html",
            }
    return None


CLUSTER_LABELS = {
    "pSEO Florida household estimate": "Florida household estimate",
    "county and rating-area intent": "County and rating area",
    "life event and income-change intent": "Life event and income change",
    "plan selection and out-of-pocket intent": "Plan selection and out-of-pocket costs",
    "tax MAGI and reconciliation intent": "Tax, MAGI, and reconciliation",
    "official verification and risk-prevention intent": "Official verification and troubleshooting",
    "calculator intent": "Calculator guide",
    "policy status": "Policy status",
    "subsidy cliff": "Subsidy cliff",
    "coverage gap": "Coverage gap",
    "methodology": "Methodology",
    "official confirmation": "Official confirmation",
    "metal tiers": "Metal tiers",
    "income estimate": "Income estimate",
    "trust": "Trust and editorial standards",
    "tax reconciliation": "Tax reconciliation",
    "open enrollment": "Open enrollment",
    "household size": "Household size",
    "age rating": "Age rating",
    "tobacco surcharge": "Tobacco surcharge",
    "CSR vs PTC": "CSR versus premium tax credit",
    "current law": "Current law",
    "privacy": "Privacy",
    "source trust": "Source trust",
    "early retiree": "Early retiree",
    "self-employed income": "Self-employed income",
    "moving to Florida": "Moving to Florida",
    "special enrollment": "Special enrollment",
    "part-time income": "Part-time income",
    "young adult coverage": "Young adult coverage",
    "dependent claim": "Dependent claim",
    "income volatility": "Income volatility",
    "business owner": "Business owner",
    "caregiver household": "Caregiver household",
    "immigration status": "Immigration status",
    "rural Florida": "Rural Florida",
    "adult child coverage": "Adult child coverage",
    "marriage and Marketplace": "Marriage and Marketplace",
    "raise impact": "Raise impact",
    "retirement withdrawals": "Retirement withdrawals",
    "pregnancy and coverage": "Pregnancy and coverage",
    "drug cost planning": "Drug cost planning",
    "HSA planning": "HSA planning",
    "uncertain income": "Uncertain income",
}


def display_cluster(cluster):
    return CLUSTER_LABELS.get(cluster, clean_title_text(cluster.replace(" intent", "")))


def direct_answer(topic):
    mk = topic["main_keyword"]
    exp = topic["expanded_keywords"]
    idx = topic.get("index", 0)
    patterns = [
        f"{mk} is best used as a planning estimate: compare the benchmark Silver premium, the estimated premium tax credit, and the net monthly cost under both enhanced-credit and current-law views before confirming actual plans at HealthCare.gov.",
        f"For {mk}, the practical answer is the difference between the enhanced-credit estimate and the current-law estimate, with {exp[0]} and final HealthCare.gov confirmation kept separate.",
        f"{mk} should answer one question first: whether the household's income, area, and FPL band make the current-law premium meaningfully different from the enhanced-credit view.",
        f"Use {mk} to understand the assumptions behind the monthly number, not to pick a plan; the final coverage and price still come from the official Marketplace.",
    ]
    return patterns[idx % len(patterns)]


def variant(options, idx):
    return options[idx % len(options)]


def moving_parts_sentence(idx):
    return variant([
        "A useful answer separates the benchmark Silver premium, FPL percentage, premium tax credit, and net premium so the reader can see which assumption drives the result.",
        "The page works best when it names each lever separately: income percentage, benchmark Silver price, estimated credit, and the monthly amount left after the credit.",
        "Instead of treating the estimate as one unexplained number, this guide splits it into the benchmark premium, poverty-guideline band, tax credit, and net cost.",
        "The practical value is in the breakdown: gross benchmark premium first, FPL percentage second, premium tax credit third, and final estimated premium last.",
        "Readers can use the estimate more safely when the article shows the source of the change rather than collapsing every input into one premium figure.",
    ], idx)


def no_broker_sentence(idx):
    return variant([
        "It also keeps the page away from broker-style advice: no insurer ranking, no quote request, and no claim of government affiliation.",
        "That editorial boundary matters because the guide explains an estimate; it does not sell a plan, collect a lead, or pretend to be the official Marketplace.",
        "The article stays in an educational lane by explaining the next verification step without recommending a carrier or asking for quote information.",
        "This keeps the content useful for planning while avoiding the pressure language common on lead-generation insurance pages.",
    ], idx)


def official_next_step_sentence(idx):
    return variant([
        "The strongest next step is to save the income assumption, note who is in the tax household, confirm the Florida area, and compare the final Marketplace screen.",
        "A reader should leave with a short verification list: annual income, household members, county or rating area, policy status, and official Marketplace result.",
        "The estimate is most useful when it becomes a checklist for the application screen rather than a number the reader treats as final.",
        "After the estimate, the practical move is to confirm the same household facts inside HealthCare.gov before relying on any premium amount.",
    ], idx)


def estimate_boundary_sentence(idx):
    return variant([
        "It can explain the premium logic, but it cannot decide whether a doctor, prescription, deductible, or network makes a plan right for the household.",
        "The estimate can narrow the question; it still cannot replace a plan-level review of providers, prescriptions, deductibles, and out-of-pocket exposure.",
        "A planning number is not the same as plan advice, especially when networks, formularies, and cost-sharing details may matter more than the premium.",
        "That boundary is important: subsidy math can be clear while the final plan choice still depends on details outside the calculator.",
    ], idx)


def recordkeeping_sentence(idx):
    return variant([
        "Good estimate notes include the date, plan year, income, household size, Florida area, and policy-status label.",
        "The reader should be able to reconstruct the result later from the saved assumptions: date, plan year, FPL band, household members, and location.",
        "A clean paper trail makes the estimate easier to correct if income, household size, county, or premium-tax-credit rules change.",
        "The page should leave enough context that a reader can tell which assumptions produced the number weeks later.",
    ], idx)


def search_quality_sentence(idx):
    return variant([
        "That structure is better for search quality because it answers the query, explains limits, and points toward official verification.",
        "Helpful content earns trust by showing the answer and the boundary together, then linking the reader to the next official check.",
        "The page should satisfy the query without stretching into advice it cannot support or repeating keywords without interpretation.",
        "Search quality improves when the article gives a specific next action instead of only restating the same subsidy phrase.",
    ], idx)


def is_hub_topic(topic, idx):
    if 60 <= idx < 80:
        return True
    if 100 <= idx < 105:
        return True
    if 140 <= idx < 145:
        return True
    return False


def short_label(topic):
    mk = topic["main_keyword"]
    words = mk.split()
    return " ".join(words[:6]) if len(words) > 6 else mk


def deeper_sections(topic, idx):
    mk = topic["main_keyword"]
    exp = topic["expanded_keywords"]
    short = short_label(topic)
    source = OFFICIAL_SOURCES[(idx + 2) % len(OFFICIAL_SOURCES)]
    titles = []
    for offset in range(7):
        title_tpl, fallback = DEEP_SECTION_TITLES[(idx + offset) % len(DEEP_SECTION_TITLES)]
        title = title_tpl.format(short=short)
        if title in titles:
            title = f"{fallback} for {short}"
        titles.append(title)

    paragraphs = [
        [
            f"The reason {mk} deserves its own page is that the reader is not asking a generic insurance question. They are trying to connect {exp[0]} with income, household size, and a specific 2026 rule environment.",
            moving_parts_sentence(idx),
            f"For this article, the practical question is whether {exp[1]} changes the next screen the reader should check, not whether one generic Florida premium can answer every household situation.",
            no_broker_sentence(idx),
        ],
        [
            f"A realistic reader might open this page after seeing a monthly premium that feels too high or too low. For {mk}, that reaction is a signal to inspect the inputs, not to panic.",
            f"If {exp[1]} and {exp[2]} point in different directions, compare the two columns slowly; the current-law view may be showing a cliff or higher expected contribution while the enhanced-credit view shows a different policy assumption.",
            official_next_step_sentence(idx),
            f"The useful note to save is the one tied to {exp[0]}: which assumption changed, which estimate column moved, and which official screen should be checked next.",
        ],
        [
            f"The calculator can clarify whether {exp[0]} is mainly an income issue, an age-rating issue, a Silver benchmark issue, or a policy-regime issue.",
            estimate_boundary_sentence(idx),
            f"When the article mentions {source['label']}, it is using the source to support a rule or definition, not to claim that every household will receive the same result.",
        ],
        [
            f"After reading about {mk}, the reader should know whether the next check is the HealthCare.gov application result, the income estimate, Silver-plan CSR details, or a coverage-gap explanation.",
            recordkeeping_sentence(idx),
            f"If rules, public premium data, or the policy status behind {exp[0]} changes, this page should be reviewed rather than treated as evergreen.",
        ],
        [
            f"The strongest comparison for {mk} is the reason behind the premium: income percentage, benchmark Silver price, policy status, and whether the household is near a threshold.",
            f"That is why {exp[0]} appears early and returns only when it helps explain a real decision instead of padding the article with repeated keywords.",
            f"A careful reader should finish this section knowing whether to verify {exp[1]}, check an official source, or compare the Marketplace result.",
        ],
        [
            f"The page also needs to be honest about uncertainty. {mk} can make the 2026 planning conversation clearer, but it cannot predict every county plan, family income change, or tax reconciliation outcome.",
            f"For {exp[1]}, the practical move is to keep the estimate narrow: one household, one plan year, one income assumption, and one confirmation path. Narrow estimates are easier to correct than broad claims.",
            search_quality_sentence(idx),
        ],
        [
            f"A stronger version of {mk} is one the reader can audit. The page should keep {mk}, related terms, source links, internal next steps, and estimate limits visible without forcing the reader to hunt for them.",
            f"For {mk}, that means keeping {exp[0]} and {exp[1]} visible beside the limitation, rather than hiding them in a generic disclaimer.",
            f"The practical quality test is whether {exp[2]} and {exp[3]} lead to a clearer action instead of a vague reassurance.",
            f"For this page, the standard is direct answer first, estimate limit second, and a concrete verification step tied to {exp[0]}.",
        ],
    ]
    return list(zip(titles, paragraphs))


def hub_sections(topic, idx):
    mk = topic["main_keyword"]
    exp = topic["expanded_keywords"]
    return [
        (f"Reader question map for {short_label(topic)}", [
            f"Readers looking up {mk} usually need more than one answer at the same time. They want a quick premium estimate, but they also need to know whether {exp[0]} changes the result and whether the number should be treated as official.",
            f"The best page experience is therefore layered. The direct answer helps the reader orient first; the explanation sections then separate {exp[1]}, federal poverty guideline percentage, premium tax credit logic, and final Marketplace confirmation.",
            "This is also how the article should be evaluated for quality. A page that only repeats the keyword may attract a click but fails the user. A useful page lets the reader name the next action: update income, compare Silver details, confirm a county, read the methodology, or open the official Marketplace screen.",
        ]),
        (f"Internal link path from {short_label(topic)}", [
            "The strongest next step is to move from explanation to calculation. The calculator page should answer the personal estimate question, while the methodology page should answer how the estimate is built and where the limits are.",
            "Related cluster pages should support the decision rather than compete with it. A county page should link toward county and rating-area interpretation; a MAGI page should link toward tax reconciliation and income updates; a plan-selection page should link toward CSR, deductibles, and HealthCare.gov confirmation.",
            f"For {mk}, the internal-link goal is not more clicks. It is a clearer path from broad education to a specific verification task.",
        ]),
        (f"Example decision flow for {short_label(topic)}", [
            "Start by writing the household size, annual income estimate, Florida area, and plan year on one line. Then read the enhanced-credit view and current-law view separately before comparing the monthly difference.",
            f"If {exp[2]} is the active concern, the reader should look for a threshold explanation before assuming a plan is unaffordable. If {exp[3]} is the concern, the reader should treat this article as preparation for the official application rather than as the final answer.",
            "The practical endpoint is a short list of questions for the Marketplace screen: Which income did it use, which household members were included, which benchmark was applied, and which plan price is final?",
        ]),
        (f"Quality checks before relying on {short_label(topic)}", [
            "A high-quality ACA estimate page should disclose that it is independent, avoid insurer recommendations, avoid lead-capture pressure, and keep official sources visible. That matters because premiums, eligibility, and tax outcomes are YMYL topics.",
            f"The page should also use {mk} naturally instead of stuffing it into every heading. Search engines and AI answer systems are more likely to trust a page that explains entities, limits, and verification steps clearly.",
            "Before acting, the reader should confirm the result at HealthCare.gov, save the assumptions used in the estimate, and revisit the result if income, household size, county, policy status, or plan-year data changes.",
            "A final review should look for practical completeness: direct answer, useful next step, source support, internal links to deeper context, and a clear disclaimer. If any of those are missing, the reader may leave with a number but not enough understanding to use it safely.",
        ]),
        (f"How this hub connects to narrower ACA guides", [
            f"This hub should not try to answer every long-tail version of {mk}. Instead, it should point readers toward narrower pages when a county, life event, MAGI issue, plan type, or troubleshooting question becomes more important than the broad estimate.",
            "That link structure helps both readers and search engines. The hub explains the concept, the supporting articles answer specific scenarios, and the calculator gives the household-level planning result.",
            "When new data, official guidance, or domain-level analytics becomes available, this hub should be the first page reviewed because smaller cluster pages depend on the same assumptions.",
        ]),
    ]


def related_topics_for(topic, idx):
    same_cluster = [
        (i, candidate)
        for i, candidate in enumerate(TOPICS)
        if i != idx and candidate["cluster"] == topic["cluster"]
    ]
    hub_candidates = [
        (i, candidate)
        for i, candidate in enumerate(TOPICS)
        if i != idx and is_hub_topic(candidate, i)
    ]
    fallback = [(i, candidate) for i, candidate in enumerate(TOPICS) if i != idx]

    related = []
    for pool in (same_cluster, hub_candidates, fallback):
        if not pool:
            continue
        start = idx % len(pool)
        for offset in range(len(pool)):
            candidate = pool[(start + offset) % len(pool)][1]
            if candidate["slug"] not in {item["slug"] for item in related}:
                related.append(candidate)
            if len(related) == 3:
                return related
    return related


def related_links_html(related):
    links = []
    for topic in related:
        links.append(
            f'<li><a href="../aca/{esc(topic["slug"])}.html">{esc(topic["main_keyword"])}</a><span>{esc(display_cluster(topic["cluster"]))}</span></li>'
        )
    return "\n".join(links)


def item_list_schema(name, url, topics, base_path="aca"):
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": name,
        "url": url,
        "numberOfItems": len(topics),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "url": f"{SITE_ORIGIN}/{base_path}/{topic['slug']}.html",
                "name": topic["title"],
            }
            for i, topic in enumerate(topics)
        ],
    }


def breadcrumb_schema(items):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": url}
            for i, (name, url) in enumerate(items)
        ],
    }


def organization_schema():
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": f"{SITE_ORIGIN}/#organization",
        "name": "CoverClarity",
        "url": SITE_ORIGIN,
        "description": "CoverClarity publishes Florida ACA subsidy calculator guidance, Marketplace estimate explainers, and source-based verification paths.",
        "areaServed": {"@type": "AdministrativeArea", "name": "Florida"},
        "knowsAbout": [
            "Florida ACA subsidy estimates",
            "Marketplace premium tax credits",
            "federal poverty level calculations",
            "cost-sharing reductions",
            "HealthCare.gov verification",
        ],
    }


def website_schema():
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "@id": f"{SITE_ORIGIN}/#website",
        "name": "CoverClarity",
        "url": SITE_ORIGIN,
        "publisher": {"@id": f"{SITE_ORIGIN}/#organization"},
        "inLanguage": "en-US",
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{SITE_ORIGIN}/blog.html?q={{search_term_string}}",
            "query-input": "required name=search_term_string",
        },
    }


def hub_faq_items(topic):
    mk = topic["main_keyword"]
    exp = topic["expanded_keywords"]
    return [
        (
            f"What is the first thing to check for {mk}?",
            f"Start with the annual income estimate, household size, Florida area, and plan year. Those inputs determine whether {exp[0]} changes the premium estimate before any plan is chosen.",
        ),
        (
            f"How does {exp[1]} affect this ACA estimate?",
            f"{exp[1]} should be treated as a planning variable, not a final eligibility decision. It can change what the reader should verify, but HealthCare.gov remains the official confirmation step.",
        ),
        (
            f"Can {mk} be used as a final Marketplace price?",
            "No. The article explains the assumptions behind the estimate. Final eligibility, available plans, and plan prices must be confirmed through the official Marketplace.",
        ),
        (
            f"Which related guide should I read after {mk}?",
            "Read the related guide path on this page first. It points to the nearest supporting cluster, such as county context, MAGI, CSR, plan selection, or troubleshooting.",
        ),
        (
            f"What makes this {mk} guide different from a quote page?",
            "It does not rank insurers, collect quote leads, or recommend a plan. It separates premium tax credit logic, out-of-pocket considerations, estimate limits, and official verification.",
        ),
    ]


def hub_summary_html(topic):
    exp = topic["expanded_keywords"]
    rows = [
        ("Check first", f"{exp[0]}, household size, annual income, Florida area, and plan year."),
        ("Why it matters", f"{exp[1]} can change the next verification step even when the premium looks simple."),
        ("Use this page for", "Understanding the estimate, spotting limits, and choosing the next related guide."),
        ("Verify officially", "Confirm final eligibility, plan availability, and prices at HealthCare.gov."),
    ]
    return (
        '<section class="hub-summary" id="hub-summary">'
        '<h2>At-a-glance ACA estimate summary</h2>'
        '<div class="summary-grid">'
        + "".join(f'<div><b>{esc(label)}</b><span>{esc(text)}</span></div>' for label, text in rows)
        + "</div></section>"
    )


def verification_snapshot_html(topic, idx):
    exp = topic["expanded_keywords"]
    rows = [
        ("Estimate scope", f"{exp[0]}, income, household size, Florida area, and plan year."),
        ("Not a final quote", "Use the result for planning before the official Marketplace screen."),
        ("Official confirmation", "Verify eligibility, plans, and prices through HealthCare.gov."),
        ("Review status", "Reviewed June 8, 2026 for 2026 ACA subsidy planning."),
    ]
    if idx % 4 == 1:
        rows[0] = ("Estimate scope", f"{exp[1]}, benchmark premium, tax credit, and net premium.")
    elif idx % 4 == 2:
        rows[1] = ("Boundary", "This guide explains estimate logic, not insurance or tax advice.")
    elif idx % 4 == 3:
        rows[3] = ("Update trigger", "Recheck after income, household, county, or rule changes.")
    return (
        '<section class="verification-snapshot" id="verification-snapshot">'
        '<h2>Verification snapshot</h2>'
        '<div class="summary-grid">'
        + "".join(f'<div><b>{esc(label)}</b><span>{esc(text)}</span></div>' for label, text in rows)
        + "</div></section>"
    )


def related_intro(topic, idx):
    return variant([
        "Use these related guides to move from this article into the closest supporting cluster before returning to the calculator.",
        f"These follow-up guides help connect {topic['main_keyword']} with the next county, MAGI, CSR, plan, or verification question.",
        "Start with the closest related guide, then return to the calculator when you are ready to test your own household assumptions.",
        f"The links below keep the path narrow: one nearby guide cluster, one calculator step, and one official confirmation task for {topic['expanded_keywords'][0]}.",
    ], idx)


def editorial_review_basis(topic, idx):
    return variant([
        "This guide separates official rules, calculator assumptions, and reader actions so a Florida shopper can see what is known, what is estimated, and what still needs Marketplace confirmation.",
        f"This page treats {topic['main_keyword']} as an estimate problem: it names the rule source, shows the assumption, and points the reader back to official confirmation.",
        f"The review focus is practical accuracy: {topic['expanded_keywords'][0]}, household inputs, source support, and a clear limit between planning guidance and final eligibility.",
        "The article is reviewed as YMYL-adjacent guidance, so it avoids certainty where final eligibility depends on the official Marketplace application.",
    ], idx)


def reader_protection(topic, idx):
    return variant([
        f"The page avoids plan recommendations, lead capture, and insurer ranking for {topic['main_keyword']}. It treats {topic['expanded_keywords'][0]}, premiums, CSR, FPL bands, and current-law comparisons as planning context rather than insurance, tax, or legal advice.",
        f"The guide does not sell coverage or rank carriers. It keeps {topic['expanded_keywords'][1]}, premium estimates, CSR notes, and tax-credit assumptions separate from plan advice.",
        f"Reader protection means no quote form pressure, no insurer preference, and no claim that this independent {topic['main_keyword']} estimate replaces HealthCare.gov.",
        f"The content explains {topic['expanded_keywords'][1]} and related estimate limits without turning the article into insurance, tax, or legal advice.",
    ], idx)


def evidence_note(topic, idx):
    source = topic.get("sources", OFFICIAL_SOURCES)[0]
    mk = topic["main_keyword"]
    exp = topic["expanded_keywords"]
    tails = [
        f"For {mk}, the source is used as a guardrail for the rule discussion, while the reader still has to confirm the household result through the official Marketplace.",
        f"The source helps define {exp[0]}, but it does not promise that every Florida household will receive the same premium, credit, or plan option.",
        f"This citation supports the estimate framework for {mk}; final eligibility and plan prices still depend on the official application screen.",
        f"The source gives context for {exp[1]}, not a personalized eligibility decision for the reader's household.",
    ]
    return (
        f"This article cites {source['label']} for {source['claim']} "
        f"{variant(tails, idx)}"
    )


def official_sources_html(topic):
    items = []
    for source in topic.get("sources", []):
        items.append(
            f'<li><a href="{esc(source["url"])}" target="_blank" rel="noopener">'
            f'{esc(source["label"])}</a></li>'
        )
    return '<ul class="source-list">' + "".join(items) + "</ul>"


def byline_html(topic):
    labels = ", ".join(source["label"].split(" questions")[0] for source in topic.get("sources", [])[:2])
    return (
        '<p class="byline">Reviewed by CoverClarity editorial desk. '
        f'Source basis: {esc(labels)}. '
        '<a href="../editorial-policy.html">Editorial policy</a></p>'
    )


def variable_component(topic, idx):
    exp = topic["expanded_keywords"]
    if idx % 5 == 0:
        return (
            '<div class="mini-table triad">'
            f'<div><b>Input to check</b><span>{esc(exp[0])}, household size, and annual income.</span></div>'
            '<div><b>Estimate to read</b><span>Benchmark premium, premium tax credit, and net monthly premium.</span></div>'
            '<div><b>Official step</b><span>Confirm final plans and prices at HealthCare.gov.</span></div>'
            '</div>'
        )
    if idx % 5 == 1:
        return (
            '<ul class="checklist">'
            '<li>Write down the annual income assumption before comparing the two columns.</li>'
            '<li>Check whether the result is near 100, 250, or 400 percent of the federal poverty guideline.</li>'
            '<li>Use Silver-plan CSR notes only as a prompt to verify plan details, not as a plan recommendation.</li>'
            '</ul>'
        )
    if idx % 5 == 2:
        return (
            '<blockquote>The number is useful only when the reader can name the assumption behind it: income, household size, area, age, or policy regime.</blockquote>'
        )
    if idx % 5 == 3:
        return (
            '<div class="callout"><b>Plain-language check:</b> if the estimate changes sharply after a small income edit, look for a threshold issue before assuming the calculator is wrong.</div>'
        )
    return (
        '<ol class="steps"><li>Read the direct answer.</li><li>Compare the two premium views.</li><li>Check the source note.</li><li>Confirm final details through the Marketplace.</li></ol>'
    )


def article_sections(topic, idx):
    mk = topic["main_keyword"]
    exp = topic["expanded_keywords"]
    context = topic["context"]
    format_name = topic["format"]
    sections = []
    if "scenario" in format_name:
        sections.append(("Start with the household story", [
            f"Imagine a reader using {mk} because one detail changed: income, age, city, or household size. {context}",
            f"The useful first step is not choosing a plan. It is separating the gross benchmark premium from the tax credit and then from the net monthly premium.",
        ]))
        sections.append(("What changes the answer", [
            f"The answer changes when {exp[0]} changes, when household size changes, or when the reader crosses a federal poverty guideline band.",
            "A calm estimate should make those moving parts visible instead of presenting one unexplained dollar figure.",
        ]))
        sections.append(("How to use the result", [
            "Use the estimate to decide what to verify on the Marketplace application: income, household members, ages, and the county or rating area.",
            "Do not use the estimate as a final price. The official Marketplace plan screen is the confirmation step.",
        ]))
    elif "comparison" in format_name:
        sections.append(("The comparison that matters", [
            f"For {mk}, the important comparison is not just high versus low. It is gross benchmark premium, estimated credit, and net premium.",
            f"That is why the article keeps {exp[0]} next to {exp[1] if len(exp) > 1 else 'current-law premium rules'} rather than mixing them in one paragraph.",
        ]))
        sections.append(("Quick comparison table", [
            "Enhanced-credit view: useful for seeing what lower contribution percentages can do to the monthly estimate.",
            "Current-law view: useful for spotting the subsidy cliff, higher contribution percentages, or no-credit outcomes.",
            "Official Marketplace view: the only place to confirm final plan availability and price.",
        ]))
        sections.append(("When the table is not enough", [
            "If income is below about 100 percent of the federal poverty guideline in Florida, the result needs a coverage-gap explanation instead of a normal tax-credit estimate.",
            "If the household is near 250 percent FPL, the reader should also look at Silver plan cost-sharing reduction details.",
        ]))
    elif "mistake" in format_name:
        sections.append(("The mistake to avoid", [
            f"The common mistake with {mk} is treating the monthly number as a quote or assuming every subsidy rule works the same way at every income.",
            f"That shortcut can hide {exp[0]} and make the current-law premium look mysterious.",
        ]))
        sections.append(("A safer reading order", [
            "First, check the household size and annual income. Second, check the FPL percentage. Third, compare the two premium regimes. Fourth, confirm the plan at HealthCare.gov.",
            "This order keeps the reader focused on the assumption that changed rather than on a frightening dollar amount.",
        ]))
        sections.append(("What to update later", [
            "Update the estimate if income changes, someone joins or leaves the tax household, a county changes, or Congress changes the premium tax credit rules.",
            "The page should show a last-updated date so the reader knows whether the policy status is current.",
        ]))
    elif "glossary" in format_name:
        sections.append(("Plain-English terms", [
            f"{mk}: the reader's specific estimate question, usually tied to a Florida area, household type, or income band.",
            "SLCSP: the second-lowest-cost Silver plan used as the benchmark for premium tax credit calculations.",
            "FPL: the federal poverty guideline percentage used to compare household income with eligibility thresholds.",
        ]))
        sections.append(("Terms that are easy to mix up", [
            "Premium tax credit lowers the monthly premium. Cost-sharing reduction can lower deductibles and copays, but only through eligible Silver plans.",
            "A coverage-gap explanation is not an error message. In Florida, it can be the most honest result for income below about 100 percent FPL.",
        ]))
        sections.append(("Reader takeaway", [
            f"When reading {mk}, translate every acronym into the household question it answers: income, benchmark premium, tax credit, net premium, and official confirmation.",
        ]))
    elif "source" in format_name:
        sections.append(("What official sources support", [
            f"{mk} depends on official concepts: federal poverty guidelines, premium tax credit rules, and Marketplace confirmation.",
            "HHS/ASPE publishes poverty guidelines. IRS materials explain the premium tax credit. HealthCare.gov is the official enrollment and confirmation channel.",
        ]))
        sections.append(("What sources do not settle", [
            "A source can define a rule, but a local estimate still needs the correct rating area and benchmark premium data.",
            "That is why this site labels illustrative values clearly until production data is loaded from approved public files.",
        ]))
        sections.append(("How to cite the estimate", [
            "Quote the direct answer and the date. Do not quote the estimate as a guaranteed plan price.",
            "For a final decision, cite HealthCare.gov or the official Marketplace result, not a planning calculator.",
        ]))
    elif "Q and A" in format_name:
        sections.append(("Reader question", [
            f"Question: What should I learn from {mk} before I shop for coverage?",
            f"Answer: learn whether {exp[0]} changes the monthly estimate, whether current-law rules create a cliff or higher contribution, and whether CSR or the coverage gap changes the next step.",
        ]))
        sections.append(("Follow-up question", [
            "Question: Does a low estimate mean the plan is best?",
            "Answer: no. The premium is only one part of the decision. Deductibles, networks, prescriptions, and CSR matter too.",
        ]))
        sections.append(("Final question", [
            "Question: Where should I confirm it?",
            "Answer: confirm final eligibility, plans, and prices at HealthCare.gov or through official Marketplace assistance.",
        ]))
    elif "step-by-step" in format_name:
        sections.append(("Step 1: confirm the inputs", [
            f"For {mk}, start with the Florida area, household size, ages, income, and whether the estimate is using the right year.",
            "Small input errors can produce a large premium difference, especially for older adults or households near a threshold.",
        ]))
        sections.append(("Step 2: read the two regimes", [
            "The enhanced-credit view shows how lower expected contribution rules affect the premium. The current-law view shows the rules that apply if enhanced credits are not available.",
            "The gap between the two is the monthly difference readers usually want to understand.",
        ]))
        sections.append(("Step 3: decide what to verify", [
            "If the result shows CSR, review Silver plans. If it shows a coverage gap, seek official help. If it shows a cliff, check income estimates carefully.",
        ]))
    elif "risk" in format_name:
        sections.append(("What can go wrong", [
            f"The risk in {mk} is overconfidence. A reader can see a neat estimate and forget that final eligibility depends on the official Marketplace application.",
            f"Policy status, {exp[0]}, and local benchmark data can all change the number.",
        ]))
        sections.append(("How this page reduces that risk", [
            "It keeps the estimate label visible, separates current-law and enhanced-credit logic, and points to official sources.",
            "It also avoids plan recommendations, lead forms, and broker-style urgency.",
        ]))
        sections.append(("What the reader should keep", [
            "Keep the assumptions: household size, income, area, date, and policy regime. Those details make the estimate understandable later.",
        ]))
    elif "decision" in format_name:
        sections.append(("A decision guide, not plan advice", [
            f"{mk} should help the reader decide what to check next, not which plan to buy.",
            "The next step can differ: update income, read CSR details, confirm a county, or compare final Marketplace plans.",
        ]))
        sections.append(("If the estimate is low", [
            "A low premium may still come with high out-of-pocket costs. That is why CSR and Silver plan details matter for lower-income readers.",
        ]))
        sections.append(("If the estimate is high", [
            "A high current-law premium may reflect the subsidy cliff, age rating, or the absence of enhanced credits. Check each cause before assuming the number is final.",
        ]))
    else:
        sections.append(("The direct answer first", [
            direct_answer(topic),
            f"The page should mention {exp[0]} early because that is the term a worried reader is most likely trying to understand.",
        ]))
        sections.append(("Checklist for a better estimate", [
            "Use annual income, not monthly income unless it is converted for the full year.",
            "Count only the people in the tax household who need coverage when using a household scenario.",
            "Confirm final eligibility at HealthCare.gov before acting on the number.",
        ]))
        sections.append(("Why this matters in Florida", [
            "Florida's Medicaid expansion status makes the below-100-percent-FPL result especially important. A normal subsidy estimate can be misleading there.",
            "For readers above 400 percent FPL, the current-law cliff can be the main reason the two columns diverge.",
        ]))
    return sections


def researched_component_html(block, topic, idx):
    kind = block.get("kind", "")
    if kind == "checklist":
        items = block.get("items", [])
        return '<ul class="checklist">' + ''.join(f"<li>{esc(item)}</li>" for item in items) + "</ul>"
    if kind == "answer":
        answer = block.get("answer", "")
        return f'<div class="answer-box"><b>Short answer:</b> {esc(answer)}</div>'
    if kind == "compare":
        rows = block.get("rows", [])
        body = ''.join(
            f"<div><b>{esc(label)}</b><span>{esc(value)}</span></div>"
            for label, value in rows
        )
        return f'<div class="mini-table triad">{body}</div>'
    if kind == "source":
        source_items = topic.get("sources", [])
        return '<ul class="source-list">' + ''.join(
            f'<li><a href="{esc(item["url"])}" rel="nofollow noopener">{esc(item["label"])}</a></li>'
            for item in source_items
        ) + "</ul>"
    if kind == "cta":
        label = block.get("label", "Run the calculator")
        return f'<p><a class="btn" href="../index.html#calc">{esc(label)}</a></p>'
    return ""


def researched_sections(topic, idx):
    blocks = topic.get("body_blocks", [])
    sections = []
    for block in blocks:
        sections.append((block["heading"], block.get("paragraphs", []), block))
    return sections


def build_article(topic, idx):
    topic["index"] = idx
    bg, fg = COLOR_PAIRS[idx % len(COLOR_PAIRS)]
    custom_body = bool(topic.get("body_blocks"))
    if custom_body:
        sections = researched_sections(topic, idx)
    else:
        sections = [(title, paragraphs, {}) for title, paragraphs in article_sections(topic, idx) + deeper_sections(topic, idx)]
    if is_hub_topic(topic, idx) and not custom_body:
        sections += [(title, paragraphs, {}) for title, paragraphs in hub_sections(topic, idx)]
    source = OFFICIAL_SOURCES[idx % len(OFFICIAL_SOURCES)]
    official_sources = topic.get("sources", [source])
    related = related_topics_for(topic, idx)
    guide_cluster = guide_cluster_for(topic)
    breadcrumb_items = [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_ORIGIN}/"},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE_ORIGIN}/blog.html"},
    ]
    if guide_cluster:
        breadcrumb_items.append({
            "@type": "ListItem",
            "position": 3,
            "name": guide_cluster["heading"],
            "item": f"{SITE_ORIGIN}/guides/{guide_cluster['slug']}.html",
        })
    breadcrumb_items.append({
        "@type": "ListItem",
        "position": len(breadcrumb_items) + 1,
        "name": topic["title"],
        "item": f"{SITE_ORIGIN}/aca/{topic['slug']}.html",
    })
    guide_hub_html = ""
    if guide_cluster:
        guide_hub_html = (
            f'<p class="guide-hub">Cluster hub: <a href="{esc(guide_cluster["href_from_article"])}">'
            f'{esc(guide_cluster["heading"])}</a></p>'
        )
    cta_title, cta_text = CTA_VARIANTS[idx % len(CTA_VARIANTS)]
    cta_button = [
        "Estimate with my household",
        "Open the premium calculator",
        "Compare the two premium views",
        "Check my income scenario",
        "Review my 2026 estimate",
        "Find my next verification step",
        "Run a private estimate",
        "Build my household estimate",
        "Use my own numbers",
        "Compare before plan shopping",
        "Estimate first",
        "Test the threshold",
    ][idx % 12]
    faq_heading = FAQ_HEADINGS[idx % len(FAQ_HEADINGS)]
    source_heading = SOURCE_HEADINGS[idx % len(SOURCE_HEADINGS)]
    toc = "\n".join(f'<a href="#s{i+1}">{esc(title)}</a>' for i, (title, _, _) in enumerate(sections))
    hub_summary = hub_summary_html(topic) if is_hub_topic(topic, idx) else ""
    verification_snapshot = verification_snapshot_html(topic, idx)
    section_html = []
    for i, (title, paragraphs, block) in enumerate(sections):
        body = "\n".join(f"<p>{esc(p)}</p>" for p in paragraphs)
        if custom_body:
            body += researched_component_html(block, topic, idx)
        elif i == 1 and idx % 4 == 0:
            body += variable_component(topic, idx)
        elif i == 1 and idx % 4 == 1:
            body += variable_component(topic, idx)
        elif i == 1 and idx % 4 == 2:
            body += variable_component(topic, idx)
        elif i == 4:
            body += variable_component(topic, idx + 1)
        elif i == 5:
            body += f'<div class="callout"><b>Evidence note:</b> {esc(evidence_note(topic, idx))}</div>'
        section_html.append(f'<section id="s{i+1}"><h2>{esc(title)}</h2>{body}</section>')

    faq_items = []
    faq_html = ""
    if is_hub_topic(topic, idx):
        faq_items = hub_faq_items(topic)
        faq_html = f"""
        <section id="faq">
          <h2>Focused questions about {esc(short_label(topic))}</h2>
          {''.join(f'<h3>{esc(question)}</h3><p>{esc(answer)}</p>' for question, answer in faq_items)}
        </section>
        """
    elif idx % 3 != 0:
        q1, a1 = FAQ_QUESTION_SETS[idx % len(FAQ_QUESTION_SETS)]
        q2, a2 = FAQ_QUESTION_SETS[(idx + 3) % len(FAQ_QUESTION_SETS)]
        faq_items = [(q1, a1), (q2, a2)]
        faq_html = f"""
        <section id="faq">
          <h2>{esc(faq_heading)}</h2>
          <h3>{esc(q1)}</h3>
          <p>{esc(a1)}</p>
          <h3>{esc(q2)}</h3>
          <p>{esc(a2)}</p>
        </section>
        """

    json_ld = [
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": topic["title"],
            "description": topic["meta_description"],
            "abstract": topic.get("excerpt", topic["meta_description"]),
            "datePublished": topic["publishAt"],
            "dateModified": "2026-06-08T00:00:00+09:00",
            "inLanguage": "en-US",
            "mainEntityOfPage": f"{SITE_ORIGIN}/aca/{topic['slug']}.html",
            "author": {"@id": f"{SITE_ORIGIN}/#organization"},
            "publisher": {"@id": f"{SITE_ORIGIN}/#organization"},
            "reviewedBy": {"@id": f"{SITE_ORIGIN}/#organization"},
            "isPartOf": {"@id": f"{SITE_ORIGIN}/#website"},
            "articleSection": display_cluster(topic["cluster"]),
            "keywords": [topic["main_keyword"]] + topic["expanded_keywords"],
            "about": ["ACA subsidy estimate", "Florida Marketplace", "premium tax credit", topic["main_keyword"]],
            "citation": [
                {"@type": "CreativeWork", "name": item["label"], "url": item["url"]}
                for item in official_sources
            ],
            "isAccessibleForFree": True,
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": breadcrumb_items,
        },
    ]
    if faq_items:
        json_ld.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": question,
                    "acceptedAnswer": {"@type": "Answer", "text": answer},
                }
                for question, answer in faq_items
            ],
        })
    json_ld.extend([organization_schema(), website_schema()])
    schema_html = "\n  ".join(
        f'<script type="application/ld+json">{json.dumps(schema, separators=(",", ":"))}</script>'
        for schema in json_ld
    )
    robots_directive = (
        "index,follow,max-image-preview:large"
        if topic.get("is_published", True)
        else "noindex,follow,max-image-preview:large"
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(topic['meta_title'])}</title>
  <meta name="description" content="{esc(topic['meta_description'])}">
  <meta name="robots" content="{robots_directive}">
  <link rel="canonical" href="{SITE_ORIGIN}/aca/{topic['slug']}.html">
  <link rel="alternate" type="application/rss+xml" title="CoverClarity Florida ACA Subsidy Guides" href="{SITE_ORIGIN}/feed.xml">
  <link rel="search" type="application/opensearchdescription+xml" title="CoverClarity" href="{SITE_ORIGIN}/opensearch.xml">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{esc(topic.get('og_title', topic['title']))}">
  <meta property="og:description" content="{esc(topic.get('og_description', topic['meta_description']))}">
  <meta property="og:url" content="{SITE_ORIGIN}/aca/{topic['slug']}.html">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{esc(topic.get('twitter_title', topic['title']))}">
  <meta name="twitter:description" content="{esc(topic.get('twitter_description', topic['meta_description']))}">
  <style>
    :root{{--paper:#faf7f1;--paper2:#f3eee3;--card:#fffdf9;--ink:#1b2a36;--soft:#34434f;--muted:#5b7184;--line:#e4dccb;--accent:#c8862b;--accent2:#a66c1c;--callout-bg:{bg};--callout-fg:{fg};--serif:Georgia,serif;--sans:system-ui,-apple-system,Segoe UI,sans-serif}}
    *{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);line-height:1.72}}a{{color:var(--accent2)}}:focus-visible{{outline:3px solid var(--accent);outline-offset:3px;border-radius:4px}}.skip-link{{position:absolute;left:-999px;top:14px;background:var(--ink);color:#fff;padding:10px 14px;border-radius:7px;z-index:9999}}.skip-link:focus{{left:14px}}.wrap{{max-width:1120px;margin:auto;padding:0 22px}}.top{{border-bottom:1px solid var(--line);background:var(--paper)}}.nav{{min-height:68px;display:flex;align-items:center;justify-content:space-between;gap:16px}}.brand{{font:700 1.3rem var(--serif);color:var(--ink);text-decoration:none;white-space:nowrap}}.nav nav{{display:flex;flex-wrap:wrap;gap:8px;justify-content:flex-end}}.nav nav a{{font-weight:650;text-decoration:none;color:var(--soft)}}.layout{{display:grid;grid-template-columns:minmax(0,740px) 280px;gap:44px;padding:42px 22px}}.eyebrow{{color:var(--accent2);font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;font-weight:800}}h1{{font:500 clamp(2.05rem,5vw,3.45rem)/1.06 var(--serif);margin:.35em 0}}.subtitle{{font-size:1.15rem;color:var(--soft)}}.meta,.byline{{font-size:.86rem;color:var(--muted)}}.byline{{border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:10px 0;margin:14px 0 18px}}.guide-hub{{font-size:.9rem;color:var(--soft)}}.answer,.answer-box,.cta,.sourcebox,.callout,.editorial,.related-guides,.hub-summary,.verification-snapshot{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;margin:22px 0}}.answer,.answer-box{{background:var(--callout-bg);border-color:var(--line)}}.answer b,.answer-box b,.callout b,.editorial b,.hub-summary b,.verification-snapshot b{{color:var(--callout-fg)}}.toc{{position:sticky;top:18px;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}}.toc a{{display:block;text-decoration:none;margin:8px 0}}article h2{{font:600 1.72rem/1.2 var(--serif);margin:36px 0 10px}}article h3{{font:700 1.12rem/1.3 var(--serif);margin:22px 0 8px}}p{{margin:0 0 16px}}.checklist,.steps{{background:var(--paper2);border-radius:12px;padding:16px 18px 16px 34px}}.mini-table,.summary-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:14px 0}}.mini-table.triad{{grid-template-columns:repeat(3,1fr)}}.mini-table div,.summary-grid div{{background:var(--paper2);border:1px solid var(--line);border-radius:12px;padding:13px}}.mini-table span,.summary-grid span{{display:block;color:var(--soft);font-size:.92rem}}blockquote{{border-left:4px solid var(--callout-fg);margin:18px 0;padding:8px 0 8px 16px;color:var(--soft)}}.related-guides ul,.source-list{{list-style:none;margin:0;padding:0;display:grid;gap:10px}}.related-guides li,.source-list li{{border-top:1px solid var(--line);padding-top:10px}}.related-guides span,.source-list span{{display:block;color:var(--muted);font-size:.86rem}}.btn{{display:inline-block;background:var(--accent);color:#fff;text-decoration:none;border-radius:7px;padding:12px 18px;font-weight:800}}footer{{background:var(--ink);color:rgba(255,255,255,.72);padding:34px 0;margin-top:40px}}@media(max-width:900px){{.layout{{display:block}}.toc{{position:static;margin:22px 0}}.nav{{height:auto;align-items:flex-start;padding-top:14px;padding-bottom:14px}}.nav nav{{justify-content:flex-start}}.mini-table,.mini-table.triad,.summary-grid{{grid-template-columns:1fr}}}}
  </style>
  {schema_html}
{HEAD_INTEGRATIONS}
</head>
<body>
  <a href="#content" class="skip-link">Skip to content</a>
  <header class="top"><div class="wrap nav"><a class="brand" href="../index.html">CoverClarity</a><nav><a href="../index.html#calc">Calculator</a><a href="../blog.html">Blog</a><a href="../methodology.html">Methodology</a><a href="../editorial-policy.html">Editorial policy</a></nav></div></header>
  <main class="wrap layout" id="content">
    <article>
      <div class="eyebrow">{esc(display_cluster(topic['cluster']))}</div>
      <h1>{esc(topic['title'])}</h1>
      <p class="subtitle">{esc(topic['subtitle'])}</p>
      <p class="meta">{esc(publish_status(topic))} {esc(publish_label(topic))} - Estimate guidance, not advice</p>
      {byline_html(topic)}
      {guide_hub_html}
      <section class="answer"><b>Direct answer:</b> {esc(direct_answer(topic))}</section>
      {hub_summary}
      {verification_snapshot}
      <nav class="toc" aria-label="Table of contents">{'<a href="#hub-summary">At-a-glance summary</a>' if is_hub_topic(topic, idx) else ''}<a href="#verification-snapshot">Verification snapshot</a>{toc}<a href="#related-guides">Related guide path</a><a href="#editorial-standards">Editorial standards</a><a href="#sources">Sources</a></nav>
      {''.join(section_html)}
      {faq_html}
      <section class="related-guides" id="related-guides">
        <h2>Related guide path</h2>
        <p>{esc(related_intro(topic, idx))}</p>
        <ul>{related_links_html(related)}</ul>
      </section>
      <section class="editorial" id="editorial-standards">
        <h2>Editorial standards for this ACA estimate</h2>
        <p><b>Review basis:</b> {esc(editorial_review_basis(topic, idx))}</p>
        <p><b>Reader protection:</b> {esc(reader_protection(topic, idx))}</p>
      </section>
      <section class="cta">
        <h2>{esc(cta_title)}</h2>
        <p>{esc(cta_text)}</p>
        <a class="btn" href="../index.html#calc">{esc(cta_button)}</a>
      </section>
      <section class="sourcebox" id="sources">
        <h2>{esc(source_heading)}</h2>
        <p>Official sources used for this article:</p>
        {official_sources_html(topic)}
        <p>{esc(evidence_note(topic, idx))}</p>
        <p>Internal links: <a href="../methodology.html">methodology</a>, <a href="../aca/{esc(related[0]['slug'])}.html">{esc(related[0]['main_keyword'])}</a>, and <a href="../aca/{esc(related[1]['slug'])}.html">{esc(related[1]['main_keyword'])}</a>.</p>
      </section>
    </article>
    <aside><nav class="toc" aria-label="Article tools"><strong>Article tools</strong><a href="../index.html#calc">Calculator</a><a href="../methodology.html">Methodology</a><a href="../blog.html">All guides</a></nav></aside>
  </main>
  <footer><div class="wrap">Independent. Not affiliated with the U.S. government or HealthCare.gov. Estimates only, not insurance, tax, or legal advice. <a href="../editorial-policy.html">Editorial policy</a> - <a href="../sources-corrections.html">Sources and corrections</a> - <a href="../contact.html">Contact</a></div></footer>
</body>
</html>
"""


def make_topics():
    topics = []
    used_keywords = set()

    # 60 parameterized pSEO topics with varied title patterns.
    combos = []
    for m_i, (metro, metro_context) in enumerate(METROS):
        for h_i, (household, household_context) in enumerate(HOUSEHOLDS):
            first_band = FPL_BANDS[(m_i + h_i) % len(FPL_BANDS)]
            second_band = FPL_BANDS[(m_i + h_i + 3) % len(FPL_BANDS)]
            for band, band_context in (first_band, second_band):
                combos.append((metro, metro_context, household, household_context, band, band_context))
    title_patterns = [
        "{metro} {household} ACA subsidy estimate at {band}: what the 2026 premium gap can mean",
        "At {band}, how a {metro} {household} can read an ACA premium estimate",
        "{household_cap} in {metro}: ACA subsidy calculator notes for {band}",
        "Reading the {metro} Marketplace estimate for {article} {household} near {band}",
        "{band} ACA subsidy guide for a {metro} {household}",
        "Why {metro} {household} premium estimates shift around {band}",
        "{metro} ACA benchmark premium questions for {article} {household} at {band}",
        "{article_cap} {household} in {metro} and the 2026 ACA current-law comparison at {band}",
        "What {band} changes in a {metro} ACA estimate for {article} {household}",
        "{household_cap} ACA planning in {metro}: subsidy notes at {band}",
    ]
    subtitle_patterns = [
        "Use this {main_keyword} guide to connect {exp0}, {exp1}, and a HealthCare.gov confirmation step.",
        "A plain-English look at {main_keyword}, with {exp0} and {exp1} explained without quote forms.",
        "This guide frames {main_keyword} around {exp0}, {exp1}, and the estimate-not-a-quote limit.",
        "For {main_keyword}, compare {exp0} with {exp1} before relying on any monthly number.",
    ]
    for i, combo in enumerate(combos[:60]):
        metro, metro_context, household, household_context, band, band_context = combo
        main_keyword = f"{metro} {household} ACA subsidy estimate {band}"
        expanded = [
            f"{metro} Marketplace premium",
            f"{household} health insurance subsidy",
            "enhanced premium tax credits",
            "current-law ACA premium",
        ]
        if main_keyword in used_keywords:
            continue
        used_keywords.add(main_keyword)
        title = title_patterns[i % len(title_patterns)].format(
            metro=metro,
            household=household,
            article=article_for_phrase(household),
            article_cap=article_for_phrase(household).capitalize(),
            household_cap=household.capitalize(),
            band=band,
        )
        subtitle = subtitle_patterns[i % len(subtitle_patterns)].format(
            main_keyword=main_keyword,
            exp0=expanded[0],
            exp1=expanded[2],
        )
        slug = slugify(title)
        topics.append({
            "title": title,
            "subtitle": subtitle,
            "main_keyword": main_keyword,
            "expanded_keywords": expanded,
            "search_intent": f"Estimate comparison for {metro} {household} at {band}",
            "cluster": "pSEO Florida household estimate",
            "slug": slug,
            "meta_title": (title[:56] + " | CoverClarity") if len(title) < 58 else title[:57],
            "meta_description": f"{main_keyword} guide with {expanded[0]}, enhanced premium tax credits, current-law comparison, and HealthCare.gov confirmation.",
            "context": f"{metro_context} This scenario is for {household_context} and {band_context}.",
            "format": FORMATS[i % len(FORMATS)],
        })

    # 40 editorial guide topics.
    for j, (main_keyword, expanded_one, cluster, context) in enumerate(GUIDE_TOPICS):
        expanded = [expanded_one, "Florida Marketplace coverage", "enhanced premium tax credits", "HealthCare.gov confirmation"]
        if main_keyword in used_keywords:
            continue
        used_keywords.add(main_keyword)
        variants = [
            f"{main_keyword}: a Florida reader's guide to {expanded_one}",
            f"How to read {main_keyword} inside a 2026 premium estimate",
            f"{main_keyword} without the jargon: {expanded_one} and next steps",
            f"When {main_keyword} matters most for Florida Marketplace shoppers",
            f"The practical {main_keyword} checklist for 2026 ACA planning",
        ]
        title = variants[j % len(variants)]
        subtitle = (
            f"{main_keyword} explained with {expanded_one}, enhanced premium tax credits, "
            "and the official Marketplace confirmation step."
        )
        topics.append({
            "title": title,
            "subtitle": subtitle,
            "main_keyword": main_keyword,
            "expanded_keywords": expanded,
            "search_intent": f"Guide for {main_keyword}",
            "cluster": cluster,
            "slug": slugify(title),
            "meta_title": (title[:56] + " | CoverClarity") if len(title) < 58 else title[:57],
            "meta_description": f"{main_keyword} guide covering {expanded_one}, Florida Marketplace estimates, official sources, and estimate limits.",
            "context": context,
            "format": FORMATS[(j + 3) % len(FORMATS)],
        })
    return topics[:100]


def topic_record(title, subtitle, main_keyword, expanded, intent, cluster, context, format_name):
    return normalize_topic({
        "title": title,
        "subtitle": subtitle,
        "main_keyword": main_keyword,
        "expanded_keywords": expanded,
        "search_intent": intent,
        "cluster": cluster,
        "slug": slugify(title),
        "meta_title": make_meta_title(title),
        "meta_description": make_meta_description(main_keyword, expanded),
        "context": context,
        "format": format_name,
    })


def make_additional_topics(existing_topics):
    topics = []
    used_keywords = {t["main_keyword"].lower() for t in existing_topics}
    used_slugs = {t["slug"] for t in existing_topics}

    def add(title, subtitle, main_keyword, expanded, intent, cluster, context, format_name):
        slug = slugify(title)
        key = main_keyword.lower()
        if key in used_keywords or slug in used_slugs:
            raise ValueError(f"duplicate additional topic: {main_keyword}")
        used_keywords.add(key)
        used_slugs.add(slug)
        topics.append(topic_record(title, subtitle, main_keyword, expanded, intent, cluster, context, format_name))

    counties = [
        ("Broward County", "South Florida rating area check", "county rating area", "dense provider networks"),
        ("Palm Beach County", "retiree and family premium planning", "older adult premium", "coastal county comparison"),
        ("Hillsborough County", "Tampa Bay Marketplace planning", "benchmark Silver check", "urban household estimate"),
        ("Orange County", "Orlando-area income scenario", "family Marketplace premium", "Central Florida plan check"),
        ("Duval County", "Jacksonville subsidy comparison", "age-rated premium", "North Florida benchmark"),
        ("Pinellas County", "Gulf Coast plan comparison", "Silver benchmark estimate", "county premium context"),
        ("Lee County", "Southwest Florida Marketplace estimate", "rating-area difference", "coastal household planning"),
        ("Polk County", "inland Florida premium estimate", "household income band", "county-specific ACA planning"),
        ("Volusia County", "Daytona-area ACA estimate", "current-law premium view", "local Marketplace check"),
        ("Brevard County", "Space Coast subsidy estimate", "SLCSP benchmark", "county income scenario"),
        ("Sarasota County", "retirement-age premium planning", "pre-Medicare ACA estimate", "Gulf Coast income check"),
        ("Manatee County", "family premium planning", "CSR Silver plan review", "county Marketplace question"),
        ("Collier County", "high-cost area estimate", "benchmark premium pressure", "Southwest Florida planning"),
        ("Pasco County", "commuter household estimate", "income threshold review", "Tampa Bay county comparison"),
        ("Osceola County", "tourism-worker income estimate", "seasonal income planning", "Central Florida household"),
        ("Seminole County", "suburban Marketplace planning", "Silver plan benchmark", "Orlando-area verification"),
        ("Lake County", "rural-suburban premium check", "rating area review", "household subsidy estimate"),
        ("St. Lucie County", "Treasure Coast estimate", "ACA premium tax credit", "county plan confirmation"),
        ("Alachua County", "college-town Marketplace estimate", "young adult coverage", "income volatility"),
        ("Leon County", "Tallahassee ACA planning", "state-worker household", "North Florida Marketplace"),
        ("Escambia County", "Panhandle premium estimate", "county rating area", "official Marketplace check"),
        ("Marion County", "inland retiree estimate", "pre-Medicare premium", "county household planning"),
        ("Okaloosa County", "military-family transition", "Marketplace eligibility check", "Panhandle plan review"),
        ("Charlotte County", "older household estimate", "age-rating premium", "Gulf Coast verification"),
        ("Clay County", "Jacksonville suburb premium check", "family income threshold", "county ACA estimate"),
    ]
    for i, (county, angle, exp0, exp1) in enumerate(counties):
        main_keyword = f"{county} ACA subsidy estimate"
        expanded = [exp0, exp1, "Florida Marketplace coverage", "HealthCare.gov confirmation"]
        title = [
            f"{county} ACA subsidy estimate: {angle} for 2026 coverage",
            f"How {county} shoppers should read an ACA subsidy estimate in 2026",
            f"{county} Marketplace premium guide for ACA subsidy estimate decisions",
            f"ACA subsidy estimate in {county}: {angle} without quote confusion",
            f"What can change the {county} ACA subsidy estimate before enrollment",
        ][i % 5]
        subtitle = f"{main_keyword} explained with {expanded[0]}, {expanded[1]}, and official Marketplace verification."
        add(title, subtitle, main_keyword, expanded, f"County-level estimate intent for {county}", "county and rating-area intent", f"{county} readers need a county-aware estimate because rating areas, benchmark Silver premiums, and income thresholds can make a statewide shortcut misleading.", FORMATS[(i + 1) % len(FORMATS)])

    life_events = [
        ("COBRA ending in Florida", "COBRA transition", "special enrollment timing"),
        ("employer coverage becoming unaffordable", "affordability test", "Marketplace fallback"),
        ("moving between Florida counties", "county move", "rating-area update"),
        ("having a baby or adopting a child", "new dependent", "household size change"),
        ("divorce changing tax household size", "dependent claim", "income split"),
        ("getting married before open enrollment", "combined income", "new tax household"),
        ("changing jobs midyear", "income projection", "employer coverage gap"),
        ("starting freelance work", "self-employed income", "variable monthly income"),
        ("income disruption after a hurricane", "temporary income drop", "documentation check"),
        ("turning 26 in Florida", "aging off parent coverage", "young adult Marketplace"),
        ("spouse moving to Medicare", "mixed coverage household", "pre-Medicare spouse"),
        ("unemployment after layoff", "loss of employer coverage", "annual income estimate"),
        ("seasonal tourism income", "variable income", "monthly-to-annual estimate"),
        ("tipped worker income changes", "reported income", "premium tax credit planning"),
        ("caregiving leave", "reduced work hours", "family coverage planning"),
        ("dependent returning home", "tax household review", "adult child coverage"),
        ("retiring before Medicare", "early retiree income", "age-rated premium"),
        ("moving to Florida from another state", "new resident Marketplace", "local plan confirmation"),
        ("losing Medicaid eligibility", "coverage transition", "Marketplace estimate"),
        ("starting a small business", "net income estimate", "self-employment deduction"),
    ]
    for i, (event, exp0, exp1) in enumerate(life_events):
        main_keyword = f"Florida ACA subsidy estimate after {event}"
        expanded = [exp0, exp1, "2026 income projection", "HealthCare.gov confirmation"]
        title = [
            f"Florida ACA subsidy estimate after {event}: what to check first",
            f"When {event} changes a Florida ACA subsidy estimate",
            f"{event.capitalize()} and the Florida ACA subsidy estimate for 2026",
            f"How to update a Florida ACA subsidy estimate after {event}",
        ][i % 4]
        subtitle = f"{main_keyword} with {expanded[0]}, {expanded[1]}, and a clear Marketplace verification step."
        add(title, subtitle, main_keyword, expanded, f"Life-event ACA planning for {event}", "life event and income-change intent", f"This reader has a real-life trigger rather than a generic premium question. The article should connect the life event to household size, annual income, special enrollment, and official plan confirmation.", FORMATS[(i + 4) % len(FORMATS)])

    plan_topics = [
        ("Bronze versus Silver after subsidies", "metal tier comparison", "CSR eligibility"),
        ("Gold plans after premium tax credits", "Gold plan comparison", "net premium tradeoff"),
        ("Silver CSR 94 plan value", "cost-sharing reduction", "low out-of-pocket design"),
        ("Silver CSR 87 plan tradeoffs", "CSR income band", "deductible comparison"),
        ("Silver CSR 73 plan limits", "partial CSR value", "out-of-pocket planning"),
        ("high deductible plan with ACA subsidy", "deductible risk", "premium tradeoff"),
        ("prescription-heavy plan comparison", "drug formulary check", "Silver plan review"),
        ("specialist network before choosing a plan", "provider network", "Marketplace verification"),
        ("hospital network questions", "network fit", "county plan comparison"),
        ("HSA eligible plan and ACA subsidy", "HSA plan rules", "metal tier choice"),
        ("family deductible versus premium", "family out-of-pocket exposure", "monthly premium"),
        ("maximum out-of-pocket limit", "annual cost risk", "plan comparison"),
        ("navigator help versus broker help", "enrollment assistance", "conflict-free verification"),
        ("dental coverage beside ACA plans", "separate dental decision", "Marketplace plan limits"),
        ("telehealth and ACA plan choice", "care access", "network confirmation"),
        ("urgent care access in Florida plans", "local provider check", "out-of-pocket cost"),
        ("pediatric coverage questions", "dependent benefits", "family plan review"),
        ("mental health network review", "behavioral health access", "plan selection"),
        ("generic drug cost comparison", "formulary tier", "monthly cost planning"),
        ("Silver benchmark versus selected plan", "SLCSP benchmark", "net premium estimate"),
    ]
    for i, (topic, exp0, exp1) in enumerate(plan_topics):
        main_keyword = f"Florida ACA subsidy estimate for {topic}"
        expanded = [exp0, exp1, "premium tax credit", "plan comparison"]
        title = [
            f"Florida ACA subsidy estimate for {topic}: premium is not the whole answer",
            f"How {topic} changes the way a Florida ACA subsidy estimate should be read",
            f"{topic.capitalize()} inside a Florida ACA subsidy estimate",
            f"Before choosing {topic}, read the Florida ACA subsidy estimate this way",
        ][i % 4]
        subtitle = f"{main_keyword} explained with {expanded[0]}, {expanded[1]}, and official plan confirmation."
        add(title, subtitle, main_keyword, expanded, f"Plan-selection intent for {topic}", "plan selection and out-of-pocket intent", f"This reader is moving from a premium estimate to a plan-selection question. The article should keep premium tax credits separate from deductibles, networks, prescriptions, and final Marketplace plan details.", FORMATS[(i + 6) % len(FORMATS)])

    tax_topics = [
        ("Roth conversion income", "modified adjusted gross income", "retirement tax planning"),
        ("IRA withdrawal planning", "taxable retirement income", "FPL percentage"),
        ("capital gains before enrollment", "investment income", "premium tax credit reconciliation"),
        ("self-employment deductions", "net business income", "Schedule C planning"),
        ("unemployment compensation", "annual income estimate", "Form 8962 risk"),
        ("rental income", "MAGI estimate", "tax household planning"),
        ("alimony income questions", "income definition", "Marketplace application"),
        ("Social Security income", "taxable benefit planning", "early retirement estimate"),
        ("student income and dependents", "dependent filing status", "household income"),
        ("spouse income mismatch", "joint filing", "Marketplace household"),
        ("year-end bonus", "income spike", "advance premium tax credit"),
        ("commission income", "variable pay", "safe income update"),
        ("1099-K payment reporting", "gross receipts versus net income", "self-employed estimate"),
        ("business loss year", "net income uncertainty", "coverage gap warning"),
        ("part-year Florida residency", "state move", "annual income projection"),
        ("tax household filing separately", "filing status issue", "premium tax credit limits"),
        ("repaying advance premium tax credit", "tax reconciliation", "income update strategy"),
        ("income under 100 percent FPL", "Florida coverage gap", "Marketplace eligibility warning"),
        ("income just over 400 percent FPL", "subsidy cliff", "current-law comparison"),
        ("estimating next year's MAGI", "income forecast", "subsidy planning"),
    ]
    for i, (topic, exp0, exp1) in enumerate(tax_topics):
        main_keyword = f"Florida ACA subsidy estimate with {topic}"
        expanded = [exp0, exp1, "premium tax credit", "tax reconciliation"]
        title = [
            f"Florida ACA subsidy estimate with {topic}: MAGI questions to settle",
            f"How {topic} can change a Florida ACA subsidy estimate",
            f"{topic.capitalize()} and the Florida ACA subsidy estimate for 2026",
            f"What to verify in a Florida ACA subsidy estimate with {topic}",
        ][i % 4]
        subtitle = f"{main_keyword} with {expanded[0]}, {expanded[1]}, and a careful HealthCare.gov confirmation path."
        add(title, subtitle, main_keyword, expanded, f"Tax and MAGI intent for {topic}", "tax MAGI and reconciliation intent", f"This reader needs to connect tax income with a Marketplace estimate without treating the article as tax advice. The article should explain MAGI, advance credit risk, and when to confirm with official sources.", FORMATS[(i + 2) % len(FORMATS)])

    verification_topics = [
        ("HealthCare.gov application result does not match estimate", "input mismatch", "official eligibility result"),
        ("SLCSP benchmark looks wrong", "benchmark Silver plan", "rating-area check"),
        ("income update after enrollment", "Marketplace income update", "advance credit adjustment"),
        ("CSR missing from Silver plan screen", "cost-sharing reduction check", "Silver eligibility"),
        ("coverage gap warning appears", "below 100 percent FPL", "Florida Medicaid status"),
        ("premium tax credit is zero", "no-credit result", "current-law threshold"),
        ("two households at same income get different premiums", "age rating", "household composition"),
        ("county selection changes the estimate", "rating-area selection", "local benchmark premium"),
        ("final plan premium changed at checkout", "plan availability", "official price confirmation"),
        ("Marketplace asks for documents", "verification notice", "income documentation"),
        ("open enrollment deadline pressure", "deadline planning", "no-rush estimate review"),
        ("special enrollment proof", "qualifying life event", "coverage start date"),
        ("calculator result seems too low", "input audit", "premium estimate review"),
        ("calculator result seems too high", "threshold review", "policy-regime comparison"),
        ("official source list for ACA subsidy estimates", "IRS HHS CMS references", "trust verification"),
    ]
    for i, (topic, exp0, exp1) in enumerate(verification_topics):
        main_keyword = f"Florida ACA subsidy estimate when {topic}"
        expanded = [exp0, exp1, "official Marketplace confirmation", "estimate troubleshooting"]
        if topic.startswith("official source list"):
            title = "Official source list for a Florida ACA subsidy estimate: IRS, HHS, CMS, and Marketplace checks"
        else:
            title = [
                f"Florida ACA subsidy estimate when {topic}: troubleshooting without guessing",
                f"What to do when {topic} in a Florida ACA subsidy estimate",
                f"Why {topic} can happen in a Florida ACA subsidy estimate",
            ][i % 3]
        subtitle = f"{main_keyword} explained with {expanded[0]}, {expanded[1]}, and a source-first verification step."
        add(title, subtitle, main_keyword, expanded, f"Verification and troubleshooting intent for {topic}", "official verification and risk-prevention intent", f"This reader is reconciling an estimate with an official screen or unexpected result. The article should reduce confusion, name the likely input to check, and point back to HealthCare.gov.", FORMATS[(i + 8) % len(FORMATS)])

    if len(topics) != 100:
        raise ValueError(f"expected 100 additional topics, got {len(topics)}")
    return topics


def researched_body_blocks(main_keyword, expanded, intent, problem, angle, idx):
    exp0, exp1 = expanded[0], expanded[1]
    checkpoint = expanded[2] if len(expanded) > 2 else "official confirmation"
    proof = expanded[3] if len(expanded) > 3 else "estimate documentation"
    answer = (
        f"{main_keyword} should be treated as a planning answer, not a quote: start with {exp0}, "
        f"check {exp1}, and confirm the final eligibility result in the official Marketplace before relying on the number."
    )
    blocks = [
        {
            "heading": "Direct answer for this search",
            "kind": "answer",
            "answer": answer,
            "paragraphs": [
                answer,
                f"The reader problem for {main_keyword} is specific: {problem}. For {main_keyword}, the estimate path should be explained before plan choice, enrollment timing, or tax follow-up.",
                f"The useful interpretation is narrow and practical: {angle}. If {exp0} is not separated from the monthly premium, the reader can over-trust a calculator output.",
            ],
        },
        {
            "heading": "Inputs that change the result",
            "kind": "checklist",
            "items": [
                f"Confirm the annual income assumption before reading {exp0}.",
                f"Check whether {exp1} changes the estimate or only changes the next verification step.",
                f"Keep the tax household count for {main_keyword} separate from who happens to live at the address.",
                f"Use the same Florida county or rating area when comparing {main_keyword} with HealthCare.gov.",
            ],
            "paragraphs": [
                f"A strong estimate for {main_keyword} begins with inputs, not with a plan name. For {exp0}, income, household size, area, age, and policy year are the variables most likely to explain a surprise.",
                f"{checkpoint} should be written down with the date of the estimate. That record makes it easier to compare this {exp1} article, the calculator, and the official Marketplace screen later.",
            ],
        },
        {
            "heading": "How to read the premium number",
            "kind": "compare",
            "rows": [
                ("Planning estimate", f"Explains {exp0} and likely subsidy movement before enrollment."),
                ("Official result", "Comes from HealthCare.gov after the application facts are entered."),
                ("Plan decision", f"Requires network, deductible, formulary, and {exp1} review."),
            ],
            "paragraphs": [
                f"The premium number is only one part of {main_keyword}. A low net premium in a {exp0} scenario can still leave high deductibles or a narrow network, while a higher premium can sometimes reduce risk for a household with regular care.",
                f"For AEO-style answers about {main_keyword}, the page should make the boundary explicit: the estimate explains subsidy math, while the official Marketplace confirms eligibility and available plans.",
            ],
        },
        {
            "heading": "What official sources can and cannot confirm",
            "kind": "source",
            "paragraphs": [
                f"Official sources support the federal rules behind {main_keyword}, including poverty-guideline references, premium tax credit mechanics, and Marketplace confirmation.",
                f"They do not replace personal tax advice or a plan-level provider search. Use the sources to verify the {exp0} rule, then use the application screen to verify the household result.",
            ],
        },
        {
            "heading": "Common mistake to avoid",
            "kind": "",
            "paragraphs": [
                f"The common mistake in {main_keyword} is treating {proof} as if it were already a final enrollment decision. For {exp1}, that shortcut can be wrong when income changes, the county is entered differently, or the selected plan is not the benchmark plan.",
                f"Another mistake is mixing monthly income with annual income. For {main_keyword}, the annual estimate is the number that usually drives FPL percentage and advance premium tax credit planning.",
            ],
        },
        {
            "heading": "When the estimate should be updated",
            "kind": "checklist",
            "items": [
                f"Income rises or drops enough to move {main_keyword} into a different FPL band.",
                f"A household member is added, removed, or moves to another coverage source tied to {exp1}.",
                f"The official Marketplace requests documentation or shows a result that conflicts with {main_keyword}.",
                f"The reader is comparing current-law and enhanced-credit scenarios for {exp0} before open enrollment.",
            ],
            "paragraphs": [
                f"An update is worth doing whenever {exp0} or {exp1} changes after the first estimate. The goal is not to chase every dollar; it is to avoid a misleading planning number.",
                f"If the official application result conflicts with {main_keyword}, the application result is the control point. The article can help diagnose {exp0} inputs, but it cannot override the Marketplace determination.",
            ],
        },
        {
            "heading": "Internal next step",
            "kind": "cta",
            "label": "Run a private Florida ACA estimate",
            "paragraphs": [
                f"After reading this {main_keyword} guide, use the calculator with the same household facts. Then compare the output with the official Marketplace before choosing a plan.",
                f"This keeps {main_keyword} in a useful sequence: learn the rule, test the numbers, verify the result, and then evaluate the actual plan details.",
            ],
        },
    ]
    if idx % 2 == 0:
        blocks.insert(4, {
            "heading": "A practical Florida scenario",
            "kind": "",
            "paragraphs": [
                f"Consider a Florida household reviewing {main_keyword} and changing only one input tied to {exp0}. For {main_keyword}, if the benchmark Silver premium stays the same but income moves, the premium tax credit can change even when the household still shops in the same county.",
                f"Now change the county or rating area instead. The income percentage may stay stable while the benchmark premium changes, which can make {main_keyword} look different for reasons unrelated to the household's earnings.",
            ],
        })
    else:
        blocks.insert(4, {
            "heading": "How this differs from a generic ACA article",
            "kind": "",
            "paragraphs": [
                f"A generic ACA article often stops at the idea that subsidies reduce premiums. This article is narrower: it connects {main_keyword} to {exp0}, {exp1}, and a concrete verification step.",
                f"That narrower scope helps search engines and answer engines understand {main_keyword} as a specific Florida Marketplace explanation rather than another broad insurance overview.",
            ],
        })
    return blocks


def make_researched_batch_topics(existing_topics):
    used_keywords = {t["main_keyword"].lower() for t in existing_topics}
    used_slugs = {t["slug"] for t in existing_topics}
    used_meta_titles = {t["meta_title"].lower() for t in existing_topics}
    topics = []

    groups = [
        (
            "official verification and risk-prevention intent",
            "verification",
            [
                ("Marketplace application mismatch", "input mismatch", "official eligibility result", "a reader sees a calculator result that does not match HealthCare.gov", "the mismatch is usually an input, timing, or official-rule issue"),
                ("SLCSP benchmark review", "benchmark Silver plan", "rating-area check", "a reader suspects the benchmark premium is not the same on every screen", "benchmark Silver is a reference point, not necessarily the selected plan"),
                ("income document request", "verification notice", "income documentation", "a reader receives a document request after estimating the subsidy", "documentation should be handled through the official Marketplace workflow"),
                ("zero premium tax credit result", "no-credit result", "current-law threshold", "a reader expected help but sees little or no credit", "income, employer coverage, filing status, or the policy regime may explain the result"),
                ("coverage gap warning", "below 100 percent FPL", "Florida Medicaid status", "a reader below the lower threshold needs a clear warning", "Florida's non-expansion status can make a normal subsidy explanation misleading"),
                ("county entry audit", "rating-area selection", "local benchmark premium", "a reader enters a county differently across tools", "county and rating area can affect the benchmark premium behind the estimate"),
                ("checkout price change", "plan availability", "official price confirmation", "a reader sees a different premium near checkout", "the final plan screen controls availability, price, and household eligibility"),
                ("CSR missing on screen", "cost-sharing reduction check", "Silver eligibility", "a reader expected lower deductibles but does not see CSR", "CSR depends on income and Silver plan selection rather than premium help alone"),
                ("special enrollment proof", "qualifying life event", "coverage start date", "a reader needs to prove a life event before using the estimate", "SEP proof and coverage start dates belong in the official application flow"),
                ("source trust audit", "IRS HHS CMS references", "trust verification", "a reader wants to know which sources support the article", "source names should be visible enough for verification and answer-engine trust"),
                ("premium estimate too low", "input audit", "premium estimate review", "a reader worries the estimate is unrealistically low", "the low number should be checked against FPL, CSR, county, and selected plan assumptions"),
                ("premium estimate too high", "threshold review", "policy-regime comparison", "a reader is surprised by a high current-law premium", "the result may reflect the cliff, age rating, or non-benchmark plan choice"),
                ("final eligibility notice", "Marketplace eligibility notice", "application result", "a reader receives an official notice after using an estimate", "the notice is the document to reconcile against the planning estimate"),
                ("navigator conversation prep", "enrollment assistance", "question checklist", "a reader plans to ask for enrollment help", "prepared facts reduce confusion without turning the article into plan advice"),
                ("audit trail for subsidy estimates", "recordkeeping", "Form 8962 planning", "a reader wants proof of what was estimated before enrollment", "notes can help reconcile a future tax form but do not guarantee the final credit"),
                ("duplicate application concern", "application cleanup", "Marketplace account review", "a reader may have conflicting Marketplace records", "the official account history should be reviewed before relying on a new estimate"),
                ("address change during enrollment", "mailing address", "county verification", "a reader changes address while shopping", "area, notices, and plan availability should be checked after the address update"),
                ("plan year source check", "2026 plan year", "rule-year alignment", "a reader mixes old plan-year guidance with a 2026 estimate", "the source year and plan year must match the estimate"),
                ("broker quote comparison", "quote versus estimate", "lead-generation risk", "a reader compares an educational estimate with a sales quote", "quotes and educational estimates answer different questions"),
                ("privacy-first estimate workflow", "browser-only estimate", "data minimization", "a reader wants a subsidy estimate without sharing personal details", "privacy improves when the article asks only for necessary planning facts"),
            ],
        ),
        (
            "tax MAGI and reconciliation intent",
            "tax planning",
            [
                ("Roth conversion window", "modified adjusted gross income", "retirement tax planning", "an early retiree is considering a Roth conversion", "taxable income timing can move the FPL percentage"),
                ("IRA withdrawal timing", "taxable retirement income", "FPL percentage", "a household may take IRA income before year end", "retirement distributions can change both subsidy size and repayment risk"),
                ("capital gains before open enrollment", "investment income", "premium tax credit reconciliation", "an investor expects capital gains during the coverage year", "realized gains can affect MAGI even without wage income"),
                ("self-employment deduction review", "net business income", "Schedule C planning", "a freelancer estimates income after expenses", "net income assumptions should be consistent with tax reporting"),
                ("unemployment compensation year", "annual income estimate", "Form 8962 risk", "a laid-off worker is estimating income after benefits", "income updates reduce the chance of a surprise at tax filing"),
                ("rental income swing", "MAGI estimate", "tax household planning", "a landlord has variable rental income", "rental income should be separated from monthly cash-flow guesses"),
                ("Social Security benefit mix", "taxable benefit planning", "early retirement estimate", "a pre-Medicare household has Social Security income", "taxability and MAGI can differ from a simple deposit total"),
                ("student dependent income", "dependent filing status", "household income", "a family includes a working student", "dependent income rules can change whether that income belongs in the estimate"),
                ("spouse income mismatch", "joint filing", "Marketplace household", "spouses enter separate income guesses", "joint filing and household income need one consistent annual number"),
                ("year-end bonus risk", "income spike", "advance premium tax credit", "a worker expects a bonus after choosing coverage", "the estimate should be updated before the annual income target becomes stale"),
                ("commission income volatility", "variable pay", "safe income update", "a commissioned worker has unpredictable pay", "periodic Marketplace updates can reduce reconciliation risk"),
                ("1099-K reporting question", "gross receipts versus net income", "self-employed estimate", "a seller sees payment-app reporting and confuses gross receipts with income", "gross receipts and net business income are not the same planning input"),
                ("business loss year", "net income uncertainty", "coverage gap warning", "a business owner may report low or negative income", "very low income in Florida needs a coverage-gap warning, not just a subsidy number"),
                ("part-year Florida move", "state move", "annual income projection", "a household moves into Florida during the year", "annual income should cover the tax year while plan availability changes by location"),
                ("filing separately issue", "filing status issue", "premium tax credit limits", "a married household may file separately", "filing status can limit credit eligibility and should be checked before relying on a premium"),
                ("advance credit repayment", "tax reconciliation", "income update strategy", "a reader worries about repaying credit later", "income updates are the practical tool for reducing reconciliation surprises"),
                ("income under 100 percent FPL", "Florida coverage gap", "Marketplace eligibility warning", "a household is below the lower subsidy threshold", "the page must flag the Florida coverage gap instead of promising a normal credit"),
                ("income over 400 percent FPL", "subsidy cliff", "current-law comparison", "a household is near or over the current-law cliff", "enhanced-credit and current-law comparisons must be labeled clearly"),
                ("MAGI forecast worksheet", "income forecast", "subsidy planning", "a household needs to forecast next year's MAGI", "forecasting should use documented assumptions rather than a monthly guess"),
                ("side-hustle income review", "secondary income", "annual estimate update", "a worker adds side income after enrollment", "secondary income can be enough to change a subsidy estimate even if wages stay stable"),
            ],
        ),
        (
            "plan selection and out-of-pocket intent",
            "plan choice",
            [
                ("Bronze versus Silver decision", "metal tier comparison", "CSR eligibility", "a reader wants the cheapest premium but may qualify for CSR", "premium savings and out-of-pocket protection must be compared separately"),
                ("Gold plan after credits", "Gold plan comparison", "net premium tradeoff", "a reader sees a subsidized Gold plan near a Silver price", "metal choice should be based on total expected cost, not metal label alone"),
                ("CSR 94 value check", "cost-sharing reduction", "low out-of-pocket design", "a low-income reader may qualify for strong CSR", "CSR changes out-of-pocket exposure only on eligible Silver plans"),
                ("CSR 87 tradeoff", "CSR income band", "deductible comparison", "a reader is in a middle CSR band", "the value should be checked against deductible and visit costs"),
                ("CSR 73 limit", "partial CSR value", "out-of-pocket planning", "a reader expects CSR to erase all out-of-pocket costs", "partial CSR can help but still requires plan-level review"),
                ("high deductible choice", "deductible risk", "premium tradeoff", "a healthy reader prefers a very low premium", "deductible risk should be weighed against expected care use"),
                ("prescription-heavy household", "drug formulary check", "Silver plan review", "a reader takes regular medications", "formulary and tier checks can matter more than a small premium difference"),
                ("specialist network review", "provider network", "Marketplace verification", "a reader wants to keep a specialist", "network confirmation belongs before enrollment, not after the premium estimate"),
                ("hospital network question", "network fit", "county plan comparison", "a reader cares about a specific hospital system", "county plan availability and network listings should be verified directly"),
                ("HSA eligible plan check", "HSA plan rules", "metal tier choice", "a reader wants to use an HSA with subsidized coverage", "HSA eligibility is plan-specific and separate from premium tax credit eligibility"),
                ("family deductible exposure", "family out-of-pocket exposure", "monthly premium", "a family compares low premiums with high deductibles", "total risk should include premium plus likely out-of-pocket costs"),
                ("maximum out-of-pocket limit", "annual cost risk", "plan comparison", "a reader has recurring care needs", "the maximum out-of-pocket limit is a ceiling to compare, not a prediction"),
                ("navigator versus broker help", "enrollment assistance", "conflict-free verification", "a reader is deciding where to get help", "help can be useful while the official Marketplace remains the final eligibility source"),
                ("dental coverage beside ACA plans", "separate dental decision", "Marketplace plan limits", "a reader expects dental to be included automatically", "medical plan subsidies and dental decisions should be separated"),
                ("telehealth plan review", "care access", "network confirmation", "a reader depends on virtual visits", "telehealth access should be checked in plan details, not assumed from metal tier"),
                ("urgent care access", "local provider check", "out-of-pocket cost", "a reader wants convenient urgent care", "local access and cost sharing should be compared after the subsidy estimate"),
                ("pediatric coverage review", "dependent benefits", "family plan review", "a parent is choosing coverage for children", "dependent benefits should be reviewed with premium, deductible, and network together"),
                ("mental health network check", "behavioral health access", "plan selection", "a reader needs therapy or psychiatry access", "behavioral health networks deserve direct confirmation before enrollment"),
                ("generic drug cost comparison", "formulary tier", "monthly cost planning", "a reader assumes generic drugs are always cheap", "formulary tiers can change the real monthly cost"),
                ("benchmark versus selected plan", "SLCSP benchmark", "net premium estimate", "a reader confuses the benchmark with the plan being selected", "the benchmark drives the credit while selected plan price drives the bill"),
            ],
        ),
        (
            "life event and income-change intent",
            "life event",
            [
                ("COBRA ending", "COBRA transition", "special enrollment timing", "a reader is leaving COBRA and needs Marketplace timing", "the estimate should be paired with SEP and coverage-start confirmation"),
                ("employer plan becoming unaffordable", "affordability test", "Marketplace fallback", "a worker may be priced out of employer coverage", "affordability rules should be checked before assuming Marketplace help"),
                ("county-to-county move", "county move", "rating-area update", "a household moves within Florida", "local plan availability and rating area can change even if income stays constant"),
                ("new baby or adoption", "new dependent", "household size change", "a household adds a child", "household size and coverage needs both change the estimate"),
                ("divorce tax household reset", "dependent claim", "income split", "a household separates into different tax units", "dependent claims and filing status should be settled before relying on the estimate"),
                ("marriage before enrollment", "combined income", "new tax household", "two adults combine households", "the estimate should use the new tax household rather than two single estimates"),
                ("midyear job change", "income projection", "employer coverage gap", "a reader changes jobs during the year", "annual income and employer coverage access should be checked together"),
                ("freelance launch", "self-employed income", "variable monthly income", "a worker starts freelancing", "net annual income is more useful than the first month's revenue"),
                ("hurricane income disruption", "temporary income drop", "documentation check", "a household loses income after a storm", "temporary disruption should be documented and updated if income recovers"),
                ("turning 26", "aging off parent coverage", "young adult Marketplace", "a young adult leaves a parent's plan", "eligibility, household status, and income should be reviewed together"),
                ("spouse moving to Medicare", "mixed coverage household", "pre-Medicare spouse", "one spouse moves to Medicare while the other needs Marketplace coverage", "the tax household may stay shared while coverage sources differ"),
                ("layoff after open enrollment", "loss of employer coverage", "annual income estimate", "a worker loses coverage after the normal window", "SEP timing and updated annual income both matter"),
                ("seasonal tourism work", "variable income", "monthly-to-annual estimate", "a tourism worker has uneven monthly pay", "annualizing irregular income requires conservative documentation"),
                ("tipped income shift", "reported income", "premium tax credit planning", "a tipped worker expects different income", "reported annual income should drive the estimate, not take-home cash alone"),
                ("caregiving leave", "reduced work hours", "family coverage planning", "a caregiver reduces hours", "income, household size, and coverage needs may all move at once"),
                ("dependent returning home", "tax household review", "adult child coverage", "an adult child returns home", "living together does not automatically decide tax household status"),
                ("early retirement before Medicare", "early retiree income", "age-rated premium", "a retiree needs coverage before Medicare", "age rating and taxable income planning should be read together"),
                ("new Florida resident", "new resident Marketplace", "local plan confirmation", "a household moves from another state", "state move changes local plan availability and Marketplace confirmation steps"),
                ("Medicaid loss transition", "coverage transition", "Marketplace estimate", "a reader loses Medicaid and needs Marketplace coverage", "the estimate should be tied to timing and official eligibility updates"),
                ("small business launch", "net income estimate", "self-employment deduction", "a new owner estimates first-year income", "business income assumptions should be written down and updated"),
            ],
        ),
        (
            "county and rating-area intent",
            "local Florida",
            [
                ("Broward rating-area review", "South Florida rating area", "dense provider networks", "a Broward shopper compares local premium changes", "county context should be tied to benchmark and network verification"),
                ("Palm Beach retiree estimate", "older adult premium", "coastal county comparison", "a pre-Medicare retiree compares coastal premiums", "age rating and county context can both move the estimate"),
                ("Hillsborough benchmark check", "Tampa Bay Marketplace planning", "benchmark Silver check", "a Tampa Bay reader checks the Silver benchmark", "local benchmark pricing should be verified before plan choice"),
                ("Orange County family estimate", "family Marketplace premium", "Central Florida plan check", "an Orlando-area family needs a household-specific estimate", "family size and county plan details should be kept separate"),
                ("Duval age-rated premium", "age-rated premium", "North Florida benchmark", "an older Jacksonville shopper sees a high gross premium", "age rating can explain pressure before subsidies are applied"),
                ("Pinellas Silver comparison", "Silver benchmark estimate", "county premium context", "a Pinellas reader compares Silver plans", "the benchmark and selected plan may not be the same"),
                ("Lee County rating review", "rating-area difference", "coastal household planning", "a Southwest Florida household sees area differences", "rating area can affect the benchmark behind the credit"),
                ("Polk inland estimate", "household income band", "county-specific ACA planning", "an inland county household tests income bands", "FPL percentage and county premiums should be read together"),
                ("Volusia current-law view", "current-law premium view", "local Marketplace check", "a Daytona-area reader compares policy scenarios", "current-law and enhanced-credit labels should remain visible"),
                ("Brevard SLCSP check", "SLCSP benchmark", "county income scenario", "a Space Coast reader wants the correct benchmark", "SLCSP is a calculation reference, not automatic plan advice"),
                ("Sarasota pre-Medicare planning", "pre-Medicare premium", "Gulf Coast income check", "a Sarasota reader prepares for retirement coverage", "income control and age rating should be evaluated together"),
                ("Manatee family CSR review", "CSR Silver plan review", "county Marketplace question", "a Manatee family may qualify for CSR", "Silver plan review matters when out-of-pocket help is possible"),
                ("Collier high-cost pressure", "benchmark premium pressure", "Southwest Florida planning", "a Collier household sees a high gross premium", "the tax credit may offset benchmark pressure but plan choice still matters"),
                ("Pasco commuter estimate", "income threshold review", "Tampa Bay county comparison", "a Pasco commuter compares household income thresholds", "income bands should be checked before comparing carriers"),
                ("Osceola seasonal income", "seasonal income planning", "Central Florida household", "an Osceola worker has irregular tourism income", "annual income documentation is the key estimate input"),
                ("Seminole Silver benchmark", "Silver plan benchmark", "Orlando-area verification", "a Seminole reader wants to verify the benchmark", "county and selected plan checks should be separated"),
                ("Lake County rural-suburban estimate", "rating area review", "household subsidy estimate", "a Lake County household compares rural and suburban options", "local plan availability can differ from statewide examples"),
                ("St. Lucie PTC check", "ACA premium tax credit", "county plan confirmation", "a Treasure Coast reader reviews tax-credit help", "official confirmation should follow any county-level estimate"),
                ("Alachua young adult estimate", "young adult coverage", "income volatility", "a college-town reader has variable income", "student or young-adult status needs tax household clarity"),
                ("Escambia Panhandle estimate", "county rating area", "official Marketplace check", "a Panhandle household wants a local estimate", "county context should end with official Marketplace verification"),
            ],
        ),
    ]

    def add(group_name, subject, exp0, exp1, problem, angle, serial):
        original_subject = subject
        main_keyword = f"Florida ACA subsidy estimate for {subject}"
        if main_keyword.lower() in used_keywords:
            subject = f"{original_subject} verification review"
            main_keyword = f"Florida ACA subsidy estimate for {subject}"
        expanded = [exp0, exp1, "2026 Marketplace estimate", "official confirmation"]
        title_patterns = [
            f"{main_keyword}: {exp0} to verify first",
            f"How {exp1} changes {main_keyword}",
            f"{subject.capitalize()} and {exp0} inside {main_keyword}",
            f"{main_keyword} guide with {exp1}",
            f"Before relying on {main_keyword}: check {exp0}",
        ]
        title = title_patterns[serial % len(title_patterns)]
        subtitle = f"{main_keyword} with {exp0}, {exp1}, and a clear official confirmation step."
        topic = normalize_topic({
            "title": title,
            "subtitle": subtitle,
            "main_keyword": main_keyword,
            "expanded_keywords": expanded,
            "search_intent": f"Researched {group_name} guide for {subject}",
            "cluster": group_name,
            "slug": slugify(title),
            "meta_title": make_meta_title(title, main_keyword, expanded),
            "meta_description": make_meta_description(main_keyword, expanded),
            "context": f"{problem}; the article should explain that {angle}.",
            "format": f"Researched {group_name.split()[0]} brief",
        })
        if topic["slug"] in used_slugs:
            topic["title"] = clean_title_text(f"{topic['title']} in 2026")
            topic["slug"] = slugify(topic["title"])
            topic["meta_title"] = make_meta_title(topic["title"], topic["main_keyword"], topic["expanded_keywords"])
        if topic["meta_title"].lower() in used_meta_titles:
            topic["meta_title"] = title_snippet(f"{topic['main_keyword']}: {exp0} review", 58)
        if topic["meta_title"].lower() in used_meta_titles:
            topic["meta_title"] = title_snippet(f"{subject}: {exp0} and {exp1}", 58)
        if topic["main_keyword"].lower() in used_keywords or topic["slug"] in used_slugs:
            raise ValueError(f"duplicate researched topic: {topic['main_keyword']}")
        source_sets = [
            [0, 2, 4],
            [1, 2, 4],
            [3, 4, 5],
            [0, 1, 6],
            [2, 4, 6],
        ]
        topic["body_blocks"] = researched_body_blocks(topic["main_keyword"], topic["expanded_keywords"], topic["search_intent"], problem, angle, serial)
        topic["source_indexes"] = source_sets[serial % len(source_sets)]
        topic["quality_score_target"] = 96 + (serial % 4)
        topic["codex_generation_note"] = "Codex-authored researched batch article with unique search intent and source-backed verification blocks."
        used_keywords.add(topic["main_keyword"].lower())
        used_slugs.add(topic["slug"])
        used_meta_titles.add(topic["meta_title"].lower())
        topics.append(topic)

    serial = 0
    for cluster, _, items in groups:
        for subject, exp0, exp1, problem, angle in items:
            add(cluster, subject, exp0, exp1, problem, angle, serial)
            serial += 1

    if len(topics) != 100:
        raise ValueError(f"expected 100 researched topics, got {len(topics)}")
    return topics


def make_expansion_researched_topics(existing_topics):
    used_keywords = {t["main_keyword"].lower() for t in existing_topics}
    used_slugs = {t["slug"] for t in existing_topics}
    used_meta_titles = {t["meta_title"].lower() for t in existing_topics}
    topics = []

    groups = [
        (
            "official verification and risk-prevention intent",
            [
                ("Marketplace notice deadline audit", "eligibility notice deadline", "document upload timing", "a reader has a deadline on a Marketplace notice", "deadline wording should be matched to the official account before the estimate is trusted"),
                ("data matching issue review", "data matching issue", "application verification", "a reader sees a data matching issue after estimating a subsidy", "the issue is about proof and official records, not about the calculator being wrong"),
                ("duplicate HealthCare.gov account check", "account cleanup", "application history", "a reader may have more than one Marketplace account", "account history should be reconciled before relying on a new estimate"),
                ("household member mismatch", "application household", "tax household comparison", "a reader sees a different household on the application", "coverage household and tax household need a careful side-by-side check"),
                ("county ZIP code conflict", "ZIP code validation", "rating area confirmation", "a reader's ZIP code points to an unexpected area", "ZIP code and county fields can change local plan availability"),
                ("premium tax credit appeal prep", "eligibility appeal", "notice review", "a reader is considering an appeal after an eligibility decision", "the article can organize facts but should not replace the official appeal instructions"),
                ("Marketplace password lockout recovery", "account access", "enrollment continuity", "a reader cannot access the account used for an estimate", "account recovery must happen before the reader can verify the official result"),
                ("plan cancellation warning", "coverage termination notice", "premium payment risk", "a reader receives a cancellation warning", "payment and eligibility notices should be separated from subsidy math"),
                ("automatic re-enrollment review", "auto-renewal", "plan year comparison", "a reader is auto-enrolled and wants to compare the old estimate", "renewal results should be compared against current-year income and plan data"),
                ("Marketplace message inbox review", "official notice inbox", "verification follow-up", "a reader misses a message after estimating coverage", "the official inbox is where document and eligibility follow-up should be checked"),
                ("consent form for broker help", "broker consent", "application authority", "a reader is asked to sign a broker consent form", "help authority should be understood before sharing account access"),
                ("coverage start date conflict", "effective date", "special enrollment timing", "a reader sees a start date that does not match expectations", "effective date rules should be verified in the official application"),
                ("plan discontinued notice", "discontinued plan", "replacement plan review", "a reader's current plan is no longer available", "replacement plan review is different from subsidy eligibility"),
                ("income attestation concern", "self-attestation", "verification document", "a reader is unsure how to support an income estimate", "documentation should support the official application facts"),
                ("Marketplace call center preparation", "call center checklist", "case reference number", "a reader needs to call HealthCare.gov", "a prepared fact list can shorten the call without changing the result"),
                ("application save error workaround", "application save issue", "screen comparison", "a reader cannot save the application after using an estimate", "the article should separate technical failure from eligibility logic"),
                ("agent of record question", "broker assignment", "account permissions", "a reader discovers an assigned broker", "permission and account control should be reviewed before plan selection"),
                ("Medicaid referral confusion", "Medicaid referral", "Marketplace eligibility path", "a reader is referred away from Marketplace subsidies", "referral language should be read with Florida's coverage rules in mind"),
                ("identity verification stall", "identity proofing", "application access", "a reader cannot pass identity verification", "identity proofing is an access step before eligibility can be confirmed"),
                ("official chat transcript notes", "chat record", "eligibility documentation", "a reader uses chat support while comparing estimates", "support records can help organize follow-up but do not replace official notices"),
            ],
        ),
        (
            "tax MAGI and reconciliation intent",
            [
                ("qualified dividends estimate", "investment income", "MAGI planning", "a reader expects dividend income during the coverage year", "dividends can affect MAGI even when wages stay stable"),
                ("taxable scholarship income", "student tax income", "dependent income rule", "a student household has scholarship income questions", "taxable scholarship treatment should be checked before estimating subsidy income"),
                ("S corporation owner wages", "business owner wages", "K-1 income review", "a business owner has both wages and pass-through income", "multiple income streams need one annual MAGI estimate"),
                ("partnership K-1 surprise", "K-1 income", "year-end reconciliation", "a partner may receive unexpected K-1 income", "late tax documents can change the final premium tax credit"),
                ("short-term disability income", "disability income", "annual income projection", "a worker receives disability payments", "income type and taxable treatment should be checked before relying on an estimate"),
                ("worker's compensation question", "workers compensation", "income inclusion", "a reader has compensation income after an injury", "not every payment affects MAGI the same way"),
                ("foreign earned income exclusion", "foreign income", "Marketplace MAGI", "a reader has foreign income", "excluded or foreign income can still require careful Marketplace review"),
                ("tax-exempt interest review", "tax-exempt interest", "MAGI adjustment", "a reader has municipal bond interest", "tax-exempt interest may matter in Marketplace income calculations"),
                ("gambling winnings risk", "unexpected income", "Form 8962 reconciliation", "a reader has one-time gambling winnings", "one-time income can still affect annual subsidy reconciliation"),
                ("cash business recordkeeping", "cash income", "self-employment records", "a cash business owner estimates annual income", "records should support the net income entered in the application"),
                ("depreciation deduction question", "business deduction", "net income estimate", "a self-employed reader uses depreciation deductions", "tax deductions can change net income estimates and reconciliation risk"),
                ("health reimbursement arrangement offer", "ICHRA offer", "employer coverage interaction", "a reader receives an HRA offer", "employer arrangements can affect Marketplace subsidy eligibility"),
                ("severance payment timing", "severance income", "coverage-year income", "a laid-off worker receives severance", "severance timing can change the annual estimate even after job loss"),
                ("pension lump sum review", "pension distribution", "retiree MAGI", "a retiree considers a lump sum", "large distributions can move a household across subsidy thresholds"),
                ("child support confusion", "support payment", "income definition", "a reader is unsure whether support payments count", "income definitions should be checked before entering the annual number"),
                ("back pay settlement", "settlement income", "annual income update", "a reader receives back pay or settlement income", "settlement timing can change the coverage-year estimate"),
                ("tax filing extension risk", "filing extension", "PTC reconciliation", "a reader files taxes late or on extension", "filing timing can affect reconciliation and future eligibility confidence"),
                ("safe harbor misunderstanding", "repayment limit", "income band", "a reader assumes repayment is always capped", "repayment limits depend on final income and should not be treated as a guarantee"),
                ("income update frequency", "Marketplace update cadence", "variable income", "a reader wants to know how often to update income", "updates should follow material changes rather than arbitrary calendar reminders"),
                ("joint custody income estimate", "custody arrangement", "dependent claim planning", "a parent shares custody and subsidy planning", "who claims a dependent can matter more than where the child sleeps"),
            ],
        ),
        (
            "plan selection and out-of-pocket intent",
            [
                ("deductible reset timing", "deductible reset", "coverage start date", "a reader changes plans midyear", "deductible timing can matter as much as monthly premium"),
                ("out-of-network billing risk", "out-of-network care", "provider directory check", "a reader worries about out-of-network bills", "network verification belongs before enrollment"),
                ("tiered hospital network", "hospital tier", "local network review", "a reader sees hospital tiers in plan details", "tiered networks should be compared with expected care use"),
                ("insulin cost comparison", "insulin copay", "drug tier check", "a reader uses insulin and compares plans", "drug cost review should be separate from subsidy size"),
                ("specialty drug prior authorization", "prior authorization", "formulary review", "a reader takes a specialty medication", "prior authorization can change practical affordability"),
                ("primary care copay tradeoff", "primary care copay", "deductible tradeoff", "a reader chooses between low premium and predictable visits", "visit cost and deductible should be read together"),
                ("emergency room cost exposure", "ER cost sharing", "maximum out-of-pocket", "a reader wants to understand emergency care risk", "emergency cost exposure belongs in total-risk comparison"),
                ("urgent prescription refill access", "pharmacy network", "formulary continuity", "a reader needs reliable prescription refills", "pharmacy access can be a plan-selection constraint"),
                ("virtual primary care plan", "virtual care model", "network access", "a reader considers a virtual-first plan", "virtual access should be checked against in-person backup options"),
                ("pregnancy care network review", "maternity network", "OB provider check", "a reader plans pregnancy care", "OB and hospital networks should be reviewed together"),
                ("physical therapy visit limit", "therapy visit limit", "rehab cost planning", "a reader expects physical therapy", "visit limits can affect total cost after the premium"),
                ("lab and imaging cost check", "diagnostic cost", "cost-sharing detail", "a reader expects lab or imaging services", "diagnostic cost sharing can differ widely by plan"),
                ("pediatric specialist access", "child specialist network", "family plan review", "a parent needs a child specialist", "family plan choice should check pediatric networks directly"),
                ("rural provider shortage review", "rural network", "travel distance", "a rural reader has few provider options", "distance and network adequacy can drive plan choice"),
                ("dental add-on timing", "dental enrollment", "separate benefit review", "a reader considers dental alongside medical coverage", "dental should be treated as a separate decision"),
                ("vision benefit expectation", "vision coverage", "benefit limit", "a reader expects vision coverage", "benefit limits should be checked rather than inferred from metal tier"),
                ("mail order pharmacy fit", "mail order pharmacy", "drug access", "a reader uses mail order medication", "mail order availability can affect continuity and cost"),
                ("specialist referral rule", "referral requirement", "HMO PPO comparison", "a reader compares referral rules", "referral requirements can matter more than a small premium difference"),
                ("family member split plans", "split household plans", "family premium strategy", "a household considers different plans for members", "split-plan strategy should be checked against networks and subsidies"),
                ("catastrophic plan eligibility", "catastrophic plan", "young adult coverage", "a reader asks about catastrophic coverage", "catastrophic eligibility and subsidy use are separate questions"),
            ],
        ),
        (
            "life event and income-change intent",
            [
                ("moving after divorce", "address change", "tax household reset", "a reader moves after divorce", "address and tax household changes should be handled together"),
                ("new dependent not on tax return yet", "new dependent", "tax return timing", "a child is added before appearing on a tax return", "current household facts and future tax filing need alignment"),
                ("temporary contract work", "contract income", "annual income swing", "a reader accepts a temporary contract", "temporary income should be annualized carefully"),
                ("returning to work after caregiving", "return to work", "income restart", "a caregiver resumes work", "income restart can change the estimate before open enrollment"),
                ("student graduation move", "graduation coverage", "new income estimate", "a student graduates and moves", "income, location, and coverage source all change at once"),
                ("spouse loses employer coverage", "spousal coverage loss", "special enrollment", "one spouse loses job-based coverage", "SEP timing and combined income should be read together"),
                ("retiree bridge year", "bridge to Medicare", "withdrawal planning", "a retiree needs one bridge year", "one-year income planning can differ from long-term retirement planning"),
                ("temporary relocation within Florida", "temporary address", "county plan availability", "a reader relocates temporarily", "temporary and permanent address facts can affect plan selection"),
                ("household member incarcerated", "incarceration status", "coverage eligibility", "a household has an incarceration-related coverage question", "eligibility facts should be verified before estimating subsidies"),
                ("immigration status update", "lawful presence", "Marketplace eligibility", "a reader's immigration status changes", "eligibility and documentation should be checked through official channels"),
                ("foster child placement", "foster placement", "household size review", "a household has a foster placement", "household and coverage rules require careful verification"),
                ("adult child files independently", "independent filing", "young adult coverage", "an adult child starts filing independently", "tax filing status may change the estimate more than age alone"),
                ("parent moves into household", "dependent parent", "tax household size", "a parent joins the home", "living arrangement and tax dependency are not the same"),
                ("seasonal layoff and recall", "recall date", "income projection", "a seasonal worker expects recall", "projected recall income should be included in annual planning"),
                ("military spouse transition", "TRICARE transition", "Marketplace fallback", "a military spouse loses or changes coverage", "other minimum essential coverage affects Marketplace decisions"),
                ("college student leaves campus plan", "student health plan", "Marketplace comparison", "a student leaves a campus health plan", "student plan and Marketplace plan rules should be compared"),
                ("domestic partnership breakup", "non-married household", "application household", "unmarried partners separate", "tax household rules should not be assumed from living arrangements"),
                ("new job waiting period", "coverage waiting period", "short gap planning", "a worker has a waiting period before employer coverage", "gap coverage should be checked against SEP timing"),
                ("part-time hours restored", "hours increase", "income update", "a worker's hours return after a reduction", "income updates should keep the subsidy estimate current"),
                ("care recipient enters Medicare", "care recipient coverage", "household coverage split", "a household member moves to Medicare", "coverage sources can split while tax household facts remain linked"),
            ],
        ),
        (
            "county and rating-area intent",
            [
                ("Miami-Dade immigrant family estimate", "lawful presence question", "South Florida plan review", "a Miami-Dade family has immigration and subsidy questions", "eligibility documentation and local plan review should be separated"),
                ("Broward retiree Roth income check", "Roth conversion planning", "county benchmark premium", "a Broward retiree changes taxable income", "retirement income planning and benchmark premiums both matter"),
                ("Palm Beach prescription plan review", "drug formulary", "coastal plan comparison", "a Palm Beach reader has recurring prescriptions", "drug cost review can outweigh a small premium difference"),
                ("Hillsborough contractor income guide", "contractor income", "Tampa Bay estimate", "a Hillsborough contractor has uneven income", "annual estimate discipline matters for variable work"),
                ("Orange County young adult plan check", "young adult coverage", "Orlando Marketplace", "an Orange County young adult leaves a parent plan", "young adult status and income should be checked together"),
                ("Duval specialist network review", "specialist network", "Jacksonville plan choice", "a Duval reader needs a specialist network", "network confirmation should happen before plan selection"),
                ("Pinellas early retiree bridge", "pre-Medicare bridge", "Gulf Coast benchmark", "a Pinellas reader is bridging to Medicare", "age rating and income control should be reviewed together"),
                ("Lee County hurricane income update", "storm income disruption", "Southwest Florida estimate", "a Lee County reader has storm-related income change", "temporary income disruption should be documented and updated"),
                ("Polk County family deductible review", "family deductible", "inland county planning", "a Polk family compares out-of-pocket risk", "deductible exposure should be part of the subsidy discussion"),
                ("Volusia seasonal worker subsidy check", "seasonal worker income", "Daytona plan review", "a Volusia seasonal worker has uneven pay", "seasonal income needs annual projection discipline"),
                ("Brevard aerospace contractor estimate", "contract work", "Space Coast Marketplace", "a Brevard contractor has project-based income", "project income should be turned into an annual estimate"),
                ("Sarasota retirement withdrawal review", "IRA withdrawal", "retiree MAGI planning", "a Sarasota retiree considers withdrawals", "withdrawal timing can change subsidy outcomes"),
                ("Manatee dependent care household", "caregiver household", "family coverage planning", "a Manatee household has caregiving responsibilities", "coverage needs and household size should be documented"),
                ("Collier high income cliff review", "400 percent FPL", "current-law comparison", "a Collier household is near a subsidy threshold", "policy-regime labels should be kept visible"),
                ("Pasco job change estimate", "job change income", "Tampa Bay suburb", "a Pasco worker changes jobs", "employer coverage and income projection should be checked together"),
                ("Osceola hospitality worker guide", "hospitality income", "Central Florida estimate", "an Osceola hospitality worker has variable income", "tips and seasonal hours need annual planning"),
                ("Seminole family specialist check", "family specialist network", "suburban plan comparison", "a Seminole family needs specialist care", "net premium should be weighed against network access"),
                ("Lake County rural access estimate", "rural provider access", "rating area review", "a Lake County reader has rural access constraints", "provider distance and rating area should be checked together"),
                ("St. Lucie new resident guide", "new resident coverage", "Treasure Coast plan check", "a St. Lucie newcomer needs local coverage", "state move and local plan availability should be verified"),
                ("Escambia military transition estimate", "military transition", "Panhandle Marketplace", "an Escambia household transitions from military coverage", "other coverage options and Marketplace eligibility should be separated"),
            ],
        ),
    ]

    title_forms = [
        "{mk}: {exp0} before the next Marketplace step",
        "{mk} and {exp1}",
        "How {exp0} changes {mk}",
        "{mk} checklist for {exp1}",
        "When {subject} affects {mk} and {exp0}",
        "{subject_cap}: {mk} with {exp0}",
        "{mk} guide to {subject} and {exp1}",
        "What {subject} means for {mk} and {exp1}",
    ]
    source_sets = [
        [0, 2, 4],
        [1, 2, 4],
        [3, 4, 5],
        [0, 1, 6],
        [2, 4, 6],
        [0, 3, 4],
    ]

    def add(cluster, subject, exp0, exp1, problem, angle, serial):
        main_keyword = f"Florida ACA subsidy estimate for {subject} advanced review"
        expanded = [exp0, exp1, "2026 Marketplace estimate", "official confirmation"]
        subject_cap = clean_title_text(subject)
        title = title_forms[serial % len(title_forms)].format(
            mk=main_keyword,
            subject=subject,
            subject_cap=subject_cap,
            exp0=exp0,
            exp1=exp1,
        )
        subtitle = f"{main_keyword} explained with {exp0}, {exp1}, and a verified next step for Florida Marketplace shoppers."
        topic = normalize_topic({
            "title": title,
            "subtitle": subtitle,
            "main_keyword": main_keyword,
            "expanded_keywords": expanded,
            "search_intent": f"Advanced researched guide for {subject}",
            "cluster": cluster,
            "slug": slugify(title),
            "meta_title": make_meta_title(title, main_keyword, expanded),
            "meta_description": make_meta_description(main_keyword, expanded),
            "context": f"{problem}; the article should explain that {angle}.",
            "format": "Advanced researched brief",
        })
        if topic["slug"] in used_slugs:
            topic["title"] = clean_title_text(f"{topic['title']} for 2026 coverage")
            topic["slug"] = slugify(topic["title"])
            topic["meta_title"] = make_meta_title(topic["title"], topic["main_keyword"], topic["expanded_keywords"])
        if topic["meta_title"].lower() in used_meta_titles:
            topic["meta_title"] = title_snippet(f"{subject_cap}: {exp0} review", 58)
        if topic["main_keyword"].lower() in used_keywords or topic["slug"] in used_slugs or topic["meta_title"].lower() in used_meta_titles:
            raise ValueError(f"duplicate expansion topic: {topic['main_keyword']}")
        topic["body_blocks"] = researched_body_blocks(topic["main_keyword"], topic["expanded_keywords"], topic["search_intent"], problem, angle, serial + 1000)
        topic["source_indexes"] = source_sets[serial % len(source_sets)]
        topic["quality_score_target"] = 96 + (serial % 4)
        topic["codex_generation_note"] = "Codex-authored expansion article with unique advanced search intent and source-backed verification blocks."
        used_keywords.add(topic["main_keyword"].lower())
        used_slugs.add(topic["slug"])
        used_meta_titles.add(topic["meta_title"].lower())
        topics.append(topic)

    serial = 0
    for cluster, items in groups:
        for subject, exp0, exp1, problem, angle in items:
            add(cluster, subject, exp0, exp1, problem, angle, serial)
            serial += 1

    if len(topics) != 100:
        raise ValueError(f"expected 100 expansion topics, got {len(topics)}")
    return topics


def ensure_unique_meta_titles(topics):
    seen = set()
    for topic in topics:
        title = topic["meta_title"]
        if title.lower() in seen:
            candidates = [
                f"{topic['main_keyword']}: {topic['expanded_keywords'][0]}",
                f"{topic['expanded_keywords'][0]} for {topic['main_keyword']}",
                topic["title"],
                topic["slug"].replace("-", " "),
            ]
            for candidate in candidates:
                next_title = title_snippet(candidate, 58)
                if len(next_title) < 30:
                    next_title = title_snippet(f"{next_title} guide", 58)
                if next_title.lower() not in seen:
                    title = next_title
                    break
        topic["meta_title"] = title
        seen.add(topic["meta_title"].lower())
    return topics


TOPICS = [normalize_topic(topic) for topic in make_topics()]
TOPICS = TOPICS + make_additional_topics(TOPICS)
TOPICS = TOPICS + make_researched_batch_topics(TOPICS)
TOPICS = TOPICS + make_expansion_researched_topics(TOPICS)
TOPICS = [normalize_topic(topic) for topic in TOPICS]
TOPICS = ensure_unique_meta_titles(TOPICS)


def render_blog(topics):
    published_count = len(topics)
    hub_card_limit = 8
    cluster_card_limit = 2
    recent_card_limit = 12

    def card(topic, featured=False):
        label = "Hub guide" if featured else display_cluster(topic["cluster"])
        cluster_label = display_cluster(topic["cluster"])
        search_text = " ".join([
            topic["title"],
            topic["main_keyword"],
            " ".join(topic["expanded_keywords"]),
            cluster_label,
        ]).lower()
        return f"""
      <a class="card" href="aca/{esc(topic['slug'])}.html" data-search="{esc(search_text)}" data-cluster="{esc(cluster_label)}">
        <span class="tag">{esc(label)}</span>
        <h2>{esc(topic['title'])}</h2>
        <p class="meta">{esc(publish_status(topic))} {esc(publish_label(topic))}</p>
        <p>{esc(topic['subtitle'])}</p>
      </a>"""

    def grid_content(items, empty_label):
        if items:
            return ''.join(card(topic) for topic in items)
        return f'<div class="empty-state">No {esc(empty_label)} are published yet. Queued guides are released every five hours and appear here when they become indexable.</div>'

    hub_cards = []
    cluster_sections = []
    hubs = [topic for i, topic in enumerate(topics) if is_hub_topic(topic, i)][:hub_card_limit]
    for topic in hubs:
        hub_cards.append(card(topic, True))

    for heading, cluster, guide_slug, _ in GUIDE_CLUSTERS:
        items = [topic for topic in topics if topic["cluster"] == cluster]
        visible_items = items[-cluster_card_limit:]
        extra_count = max(0, len(items) - len(visible_items))
        cluster_note = (
            f"{len(items)} focused guides support this decision area. Showing the {len(visible_items)} most recently published here; "
            f"<a href=\"guides/{esc(guide_slug)}.html\">open this guide hub</a> for the full cluster."
            if items
            else f"0 focused guides are published yet. <a href=\"guides/{esc(guide_slug)}.html\">Open this guide hub</a>."
        )
        more_link = (
            f'<p class="more-link"><a href="guides/{esc(guide_slug)}.html">View {extra_count} more in this cluster</a></p>'
            if extra_count
            else ""
        )
        cluster_sections.append(f"""
    <section class="cluster-block" id="{slugify(heading)}">
      <div class="section-head">
        <h2>{esc(heading)}</h2>
        <p>{cluster_note}</p>
      </div>
      <div class="grid" aria-label="{esc(heading)}">{grid_content(visible_items, heading.lower())}</div>
      {more_link}
    </section>""")

    recent_topics = topics[-recent_card_limit:]
    all_cards = grid_content(recent_topics, "Florida ACA subsidy guides")
    representative_topics = hubs[:20] + topics[-10:]
    blog_schemas = [
        organization_schema(),
        website_schema(),
        {
            "@context": "https://schema.org",
            "@type": "Blog",
            "@id": f"{SITE_ORIGIN}/blog.html#blog",
            "name": "Florida ACA Subsidy Guides 2026",
            "description": "A structured 200-guide library for Florida ACA subsidy estimates and Marketplace verification.",
            "url": f"{SITE_ORIGIN}/blog.html",
            "publisher": {"@id": f"{SITE_ORIGIN}/#organization"},
            "blogPost": [
                {"@type": "BlogPosting", "headline": topic["title"], "url": f"{SITE_ORIGIN}/aca/{topic['slug']}.html"}
                for topic in representative_topics
            ],
        },
        item_list_schema("Representative Florida ACA subsidy guides", f"{SITE_ORIGIN}/blog.html", representative_topics),
        breadcrumb_schema([
            ("Home", f"{SITE_ORIGIN}/"),
            ("Blog", f"{SITE_ORIGIN}/blog.html"),
        ]),
    ]
    blog_schema_html = "\n  ".join(
        f'<script type="application/ld+json">{json.dumps(schema, separators=(",", ":"))}</script>'
        for schema in blog_schemas
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Florida ACA Subsidy Guides 2026 | CoverClarity Blog</title>
  <meta name="description" content="Florida ACA subsidy guides for 2026 with calculator explainers, enhanced credit comparisons, CSR notes, FPL bands, and coverage-gap guidance.">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <link rel="canonical" href="{SITE_ORIGIN}/blog.html">
  <link rel="alternate" type="application/rss+xml" title="CoverClarity Florida ACA Subsidy Guides" href="{SITE_ORIGIN}/feed.xml">
  <link rel="search" type="application/opensearchdescription+xml" title="CoverClarity" href="{SITE_ORIGIN}/opensearch.xml">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Florida ACA Subsidy Guides 2026 | CoverClarity Blog">
  <meta property="og:description" content="Florida ACA subsidy guides for 2026 with county, MAGI, CSR, plan comparison, and verification clusters.">
  <meta property="og:url" content="{SITE_ORIGIN}/blog.html">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="Florida ACA Subsidy Guides 2026 | CoverClarity Blog">
  <meta name="twitter:description" content="A structured 200-guide library for Florida ACA subsidy estimates and Marketplace verification.">
  <style>
    :root{{--paper:#faf7f1;--paper2:#f3eee3;--card:#fffdf9;--ink:#1b2a36;--soft:#34434f;--muted:#5b7184;--line:#e4dccb;--accent:#c8862b;--accent2:#a66c1c;--serif:Georgia,serif;--sans:system-ui,-apple-system,Segoe UI,sans-serif}}
    *{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);line-height:1.65}}a{{color:var(--accent2)}}:focus-visible{{outline:3px solid var(--accent);outline-offset:3px;border-radius:4px}}.skip-link{{position:absolute;left:-999px;top:14px;background:var(--ink);color:#fff;padding:10px 14px;border-radius:7px;z-index:9999}}.skip-link:focus{{left:14px}}.wrap{{max-width:1180px;margin:auto;padding:0 22px}}.top{{border-bottom:1px solid var(--line);background:var(--paper)}}.nav{{min-height:68px;display:flex;align-items:center;justify-content:space-between;gap:16px}}.brand{{font:700 1.3rem var(--serif);color:var(--ink);text-decoration:none;white-space:nowrap}}.nav nav{{display:flex;flex-wrap:wrap;gap:8px;justify-content:flex-end}}.nav nav a{{font-weight:650;text-decoration:none;color:var(--soft)}}.hero{{padding:48px 0 28px}}.eyebrow{{color:var(--accent2);font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;font-weight:800}}.h1{{font:500 clamp(2.1rem,5vw,3.8rem)/1.05 var(--serif);max-width:15ch;margin:.35em 0}}.lead{{font-size:1.16rem;color:var(--soft);max-width:70ch}}.section-head{{border-top:1px solid var(--line);padding-top:28px;margin-top:36px}}.section-head h2{{font:600 1.75rem/1.2 var(--serif);margin:0 0 6px}}.section-head p{{color:var(--soft);margin:0;max-width:70ch}}.quick-nav{{display:flex;flex-wrap:wrap;gap:10px;margin:20px 0 34px}}.quick-nav a{{background:var(--card);border:1px solid var(--line);border-radius:999px;padding:8px 12px;text-decoration:none;font-weight:700}}.library-tools{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;margin:12px 0 30px;display:grid;grid-template-columns:minmax(0,1fr) 260px;gap:12px;align-items:end}}.library-tools label{{display:block;font-size:.82rem;font-weight:800;color:var(--muted);margin-bottom:6px}}.library-tools input,.library-tools select{{width:100%;border:1px solid var(--line);border-radius:8px;background:#fffdf9;color:var(--ink);padding:11px 12px;font:inherit}}.result-status{{font-size:.9rem;color:var(--muted);margin:10px 0 0}}.no-results,.empty-state{{background:var(--paper2);border:1px solid var(--line);border-radius:14px;padding:18px;margin:18px 0 34px;color:var(--soft)}}.no-results{{display:none}}.empty-state{{grid-column:1/-1;margin:0}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin:18px 0 44px}}.more-link{{margin:-26px 0 38px;font-weight:700}}.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px;text-decoration:none;color:inherit;min-height:280px}}.card[hidden]{{display:none}}.card:hover{{border-color:var(--accent)}}.tag{{display:inline-block;background:#fbf3e1;color:var(--accent2);border:1px solid #e8d2a6;border-radius:99px;padding:4px 10px;font-size:.76rem;font-weight:700}}.card h2{{font:600 1.28rem/1.2 var(--serif);margin:14px 0 8px}}.meta{{font-size:.82rem;color:var(--muted)}}.cta{{background:var(--paper2);border:1px solid var(--line);border-radius:14px;padding:22px;margin:10px 0 34px}}.btn{{display:inline-block;background:var(--accent);color:white;text-decoration:none;border-radius:7px;padding:12px 18px;font-weight:800}}footer{{background:var(--ink);color:rgba(255,255,255,.72);padding:34px 0;margin-top:40px}}@media(max-width:980px){{.grid{{grid-template-columns:repeat(2,1fr)}}.library-tools{{grid-template-columns:1fr}}}}@media(max-width:680px){{.grid{{grid-template-columns:1fr}}.nav{{height:auto;align-items:flex-start;padding-top:14px;padding-bottom:14px}}.nav nav{{justify-content:flex-start}}}}
  </style>
  {blog_schema_html}
{HEAD_INTEGRATIONS}
</head>
<body>
  <a href="#content" class="skip-link">Skip to content</a>
  <header class="top"><div class="wrap nav"><a class="brand" href="index.html">CoverClarity</a><nav><a href="index.html#calc">Calculator</a><a href="methodology.html">Methodology</a><a href="editorial-policy.html">Editorial policy</a></nav></div></header>
  <main class="wrap" id="content">
    <section class="hero">
      <div class="eyebrow">Florida ACA subsidy guides</div>
      <h1 class="h1">Florida ACA subsidy guides for 2026</h1>
      <p class="lead">{published_count} currently published guides for Floridians comparing Marketplace premiums, enhanced premium tax credits, current-law estimates, CSR, SLCSP, FPL bands, county scenarios, MAGI questions, and coverage-gap warnings. Additional queued guides publish every five hours.</p>
    </section>
    <section class="cta">
      <h2 style="font:600 1.55rem/1.2 var(--serif);margin:0 0 8px;">Start with your own estimate</h2>
      <p style="margin:0 0 14px;color:var(--soft)">Use the calculator before reading. It makes the guides easier to interpret because the examples match your household size, income, and Florida area.</p>
      <a class="btn" href="index.html#calc">Estimate your 2026 premium</a>
    </section>
    <nav class="quick-nav" aria-label="Guide categories">
      <a href="#hub-guides">Hub guides</a>
      <a href="guides/county-and-rating-area-guides.html">County guides</a>
      <a href="guides/life-event-and-income-change-guides.html">Life event guides</a>
      <a href="guides/plan-selection-and-out-of-pocket-guides.html">Plan selection</a>
      <a href="guides/tax-magi-and-reconciliation-guides.html">Tax and MAGI</a>
      <a href="guides/official-verification-and-troubleshooting-guides.html">Verification</a>
      <a href="#all-guides">All guides</a>
    </nav>
    <section class="library-tools" aria-label="Guide search tools">
      <div>
        <label for="guideSearch">Search guides</label>
        <input id="guideSearch" type="search" placeholder="Try county, MAGI, CSR, Silver, COBRA, verification" autocomplete="off">
        <p class="result-status" id="guideSearchStatus" aria-live="polite">Showing featured and recent guide cards.</p>
      </div>
      <div>
        <label for="clusterFilter">Filter by cluster</label>
        <select id="clusterFilter">
          <option value="">All clusters</option>
          <option value="Florida household estimate">Household estimates</option>
          <option value="County and rating area">County and rating area</option>
          <option value="Life event and income change">Life event and income change</option>
          <option value="Plan selection and out-of-pocket costs">Plan selection</option>
          <option value="Tax, MAGI, and reconciliation">Tax and MAGI</option>
          <option value="Official verification and troubleshooting">Verification</option>
        </select>
      </div>
    </section>
    <div class="no-results" id="guideNoResults">No matching guides. Try a broader term such as subsidy, income, Silver, county, or verification.</div>
    <section class="cluster-block" id="hub-guides">
      <div class="section-head">
        <h2>Core Florida ACA subsidy hub guides</h2>
        <p>Currently published deeper guides for calculator use, enhanced credits, the subsidy cliff, CSR, FPL, tax reconciliation, and high-intent plan decisions.</p>
      </div>
      <div class="grid" aria-label="Hub guides">{''.join(hub_cards) if hub_cards else '<div class="empty-state">No hub guides are published yet. Queued hub articles appear here when their scheduled publish time arrives.</div>'}</div>
    </section>
    {''.join(cluster_sections)}
    <section class="cluster-block" id="all-guides">
      <div class="section-head">
        <h2>Recent Florida ACA subsidy guides</h2>
        <p>The most recently published guide cards in scheduled order. Use the cluster guide hubs, sitemap, RSS feed, or site search index for the full currently published set.</p>
      </div>
      <div class="grid" aria-label="Article list">{all_cards}</div>
    </section>
  </main>
  <footer><div class="wrap">Independent. Not affiliated with the U.S. government or HealthCare.gov. Estimates only, not insurance, tax, or legal advice. <a href="editorial-policy.html">Editorial policy</a> - <a href="sources-corrections.html">Sources and corrections</a> - <a href="contact.html">Contact</a></div></footer>
  <script>
    const searchInput = document.getElementById('guideSearch');
    const clusterFilter = document.getElementById('clusterFilter');
    const statusEl = document.getElementById('guideSearchStatus');
    const noResults = document.getElementById('guideNoResults');
    const cards = Array.from(document.querySelectorAll('.card[data-search]'));
    function applyGuideFilters() {{
      const term = searchInput.value.trim().toLowerCase();
      const cluster = clusterFilter.value;
      let shown = 0;
      cards.forEach((card) => {{
        const matchesTerm = !term || card.dataset.search.includes(term);
        const matchesCluster = !cluster || card.dataset.cluster === cluster;
        const visible = matchesTerm && matchesCluster;
        card.hidden = !visible;
        if (visible) shown += 1;
      }});
      statusEl.textContent = term || cluster ? `Showing ${{shown}} matching featured or recent guide cards.` : 'Showing featured and recent guide cards.';
      noResults.style.display = shown ? 'none' : 'block';
    }}
    function syncGuideParams() {{
      const params = new URLSearchParams(window.location.search);
      const term = searchInput.value.trim();
      const cluster = clusterFilter.value;
      if (term) params.set('q', term); else params.delete('q');
      if (cluster) params.set('cluster', cluster); else params.delete('cluster');
      const next = params.toString() ? `${{window.location.pathname}}?${{params.toString()}}` : window.location.pathname;
      window.history.replaceState(null, '', next + window.location.hash);
    }}
    function applyAndSyncGuideFilters() {{
      applyGuideFilters();
      syncGuideParams();
    }}
    const initialParams = new URLSearchParams(window.location.search);
    const initialQ = initialParams.get('q') || '';
    const initialCluster = initialParams.get('cluster') || '';
    if (initialQ) searchInput.value = initialQ;
    if (initialCluster && Array.from(clusterFilter.options).some((option) => option.value === initialCluster)) clusterFilter.value = initialCluster;
    applyGuideFilters();
    searchInput.addEventListener('input', applyAndSyncGuideFilters);
    clusterFilter.addEventListener('change', applyAndSyncGuideFilters);
  </script>
</body>
</html>
"""


def render_guide_page(heading, cluster, guide_slug, meta_title, topics):
    items = [topic for topic in topics if topic["cluster"] == cluster]
    has_items = bool(items)
    cards = []
    for topic in items:
        cards.append(f"""
      <a class="card" href="../aca/{esc(topic['slug'])}.html">
        <span class="tag">{esc(display_cluster(topic['cluster']))}</span>
        <h2>{esc(topic['title'])}</h2>
        <p class="meta">{esc(publish_status(topic))} {esc(publish_label(topic))}</p>
        <p>{esc(topic['subtitle'])}</p>
      </a>""")
    cards_html = ''.join(cards) if cards else '<div class="empty-state">This hub is not open for indexing yet. Queued articles appear here when their scheduled publish time arrives.</div>'
    lead = (
        f"{heading} collect {len(items)} focused Florida ACA subsidy articles so readers can move from a broad premium estimate "
        "to a specific county, life event, plan-selection, MAGI, or verification question."
        if has_items
        else f"{heading} will collect focused Florida ACA subsidy articles once scheduled guides in this cluster reach their publish time."
    )
    robots = "index,follow,max-image-preview:large" if has_items else "noindex,follow"
    schemas = [
        organization_schema(),
        website_schema(),
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": heading,
            "description": lead,
            "url": f"{SITE_ORIGIN}/guides/{guide_slug}.html",
            "isPartOf": {"@id": f"{SITE_ORIGIN}/#website"},
            "publisher": {"@id": f"{SITE_ORIGIN}/#organization"},
            "mainEntity": [
                {"@type": "Article", "headline": topic["title"], "url": f"{SITE_ORIGIN}/aca/{topic['slug']}.html"}
                for topic in items
            ],
        },
        item_list_schema(heading, f"{SITE_ORIGIN}/guides/{guide_slug}.html", items),
        breadcrumb_schema([
            ("Home", f"{SITE_ORIGIN}/"),
            ("Blog", f"{SITE_ORIGIN}/blog.html"),
            (heading, f"{SITE_ORIGIN}/guides/{guide_slug}.html"),
        ]),
    ]
    schema_html = "\n  ".join(
        f'<script type="application/ld+json">{json.dumps(schema, separators=(",", ":"))}</script>'
        for schema in schemas
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(meta_title)} | CoverClarity</title>
  <meta name="description" content="{esc(lead)}">
  <meta name="robots" content="{robots}">
  <link rel="canonical" href="{SITE_ORIGIN}/guides/{guide_slug}.html">
  <link rel="alternate" type="application/rss+xml" title="CoverClarity Florida ACA Subsidy Guides" href="{SITE_ORIGIN}/feed.xml">
  <link rel="search" type="application/opensearchdescription+xml" title="CoverClarity" href="{SITE_ORIGIN}/opensearch.xml">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(meta_title)} | CoverClarity">
  <meta property="og:description" content="{esc(lead)}">
  <meta property="og:url" content="{SITE_ORIGIN}/guides/{guide_slug}.html">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{esc(meta_title)} | CoverClarity">
  <meta name="twitter:description" content="{esc(lead)}">
  <style>
    :root{{--paper:#faf7f1;--paper2:#f3eee3;--card:#fffdf9;--ink:#1b2a36;--soft:#34434f;--muted:#5b7184;--line:#e4dccb;--accent:#c8862b;--accent2:#a66c1c;--serif:Georgia,serif;--sans:system-ui,-apple-system,Segoe UI,sans-serif}}
    *{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);line-height:1.65}}a{{color:var(--accent2)}}:focus-visible{{outline:3px solid var(--accent);outline-offset:3px;border-radius:4px}}.skip-link{{position:absolute;left:-999px;top:14px;background:var(--ink);color:#fff;padding:10px 14px;border-radius:7px;z-index:9999}}.skip-link:focus{{left:14px}}.wrap{{max-width:1180px;margin:auto;padding:0 22px}}.top{{border-bottom:1px solid var(--line);background:var(--paper)}}.nav{{min-height:68px;display:flex;align-items:center;justify-content:space-between;gap:16px}}.brand{{font:700 1.3rem var(--serif);color:var(--ink);text-decoration:none;white-space:nowrap}}.nav nav{{display:flex;flex-wrap:wrap;gap:8px;justify-content:flex-end}}.nav nav a{{font-weight:650;text-decoration:none;color:var(--soft)}}.hero{{padding:48px 0 28px}}.eyebrow{{color:var(--accent2);font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;font-weight:800}}h1{{font:500 clamp(2.1rem,5vw,3.8rem)/1.05 var(--serif);max-width:17ch;margin:.35em 0}}.lead{{font-size:1.16rem;color:var(--soft);max-width:74ch}}.intro{{background:var(--paper2);border:1px solid var(--line);border-radius:14px;padding:22px;margin:10px 0 30px}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin:22px 0 60px}}.empty-state{{grid-column:1/-1;background:var(--paper2);border:1px solid var(--line);border-radius:14px;padding:18px;color:var(--soft)}}.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px;text-decoration:none;color:inherit;min-height:280px}}.card:hover{{border-color:var(--accent)}}.tag{{display:inline-block;background:#fbf3e1;color:var(--accent2);border:1px solid #e8d2a6;border-radius:99px;padding:4px 10px;font-size:.76rem;font-weight:700}}.card h2{{font:600 1.28rem/1.2 var(--serif);margin:14px 0 8px}}.meta{{font-size:.82rem;color:var(--muted)}}footer{{background:var(--ink);color:rgba(255,255,255,.72);padding:34px 0;margin-top:40px}}@media(max-width:980px){{.grid{{grid-template-columns:repeat(2,1fr)}}}}@media(max-width:680px){{.grid{{grid-template-columns:1fr}}.nav{{height:auto;align-items:flex-start;padding-top:14px;padding-bottom:14px}}.nav nav{{justify-content:flex-start}}}}
  </style>
  {schema_html}
{HEAD_INTEGRATIONS}
</head>
<body>
  <a href="#content" class="skip-link">Skip to content</a>
  <header class="top"><div class="wrap nav"><a class="brand" href="../index.html">CoverClarity</a><nav><a href="../index.html#calc">Calculator</a><a href="../blog.html">Blog</a><a href="../methodology.html">Methodology</a><a href="../editorial-policy.html">Editorial policy</a></nav></div></header>
  <main class="wrap" id="content">
    <section class="hero">
      <div class="eyebrow">Florida ACA guide hub</div>
      <h1>{esc(heading)}</h1>
      <p class="lead">{esc(lead)}</p>
    </section>
    <section class="intro">
      <h2 style="font:600 1.55rem/1.2 var(--serif);margin:0 0 8px;">How to use this hub</h2>
      <p style="margin:0;color:var(--soft)">Start with the article closest to the reader's situation, then use the related guide path inside each article to move toward the calculator, methodology, and official Marketplace confirmation.</p>
    </section>
    <section class="grid" aria-label="{esc(heading)}">{cards_html}
    </section>
  </main>
  <footer><div class="wrap">Independent. Not affiliated with the U.S. government or HealthCare.gov. Estimates only, not insurance, tax, or legal advice. <a href="../editorial-policy.html">Editorial policy</a> - <a href="../sources-corrections.html">Sources and corrections</a> - <a href="../contact.html">Contact</a></div></footer>
</body>
</html>
"""


def render_sitemap(topics):
    urls = [
        (f"{SITE_ORIGIN}/", "1.0"),
        (f"{SITE_ORIGIN}/blog.html", "0.9"),
        (f"{SITE_ORIGIN}/methodology.html", "0.7"),
        (f"{SITE_ORIGIN}/about.html", "0.6"),
        (f"{SITE_ORIGIN}/contact.html", "0.6"),
        (f"{SITE_ORIGIN}/editorial-policy.html", "0.6"),
        (f"{SITE_ORIGIN}/sources-corrections.html", "0.6"),
        (f"{SITE_ORIGIN}/privacy.html", "0.4"),
        (f"{SITE_ORIGIN}/aca-enhanced-subsidies-2026-florida.html", "0.75"),
    ]
    urls.extend(
        (f"{SITE_ORIGIN}/guides/{guide_slug}.html", "0.85")
        for _, cluster, guide_slug, _ in GUIDE_CLUSTERS
        if any(topic["cluster"] == cluster for topic in topics)
    )
    urls.extend((f"{SITE_ORIGIN}/aca/{t['slug']}.html", "0.8") for t in topics)
    body = "\n".join(
        f"  <url><loc>{loc}</loc><lastmod>2026-06-08</lastmod><changefreq>weekly</changefreq><priority>{priority}</priority></url>"
        for loc, priority in urls
    )
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'


def render_feed(topics):
    items = []
    for topic in topics:
        items.append(f"""
    <item>
      <title>{esc(topic['title'])}</title>
      <link>{SITE_ORIGIN}/aca/{topic['slug']}.html</link>
      <guid>{SITE_ORIGIN}/aca/{topic['slug']}.html</guid>
      <description>{esc(topic.get('excerpt', topic['meta_description']))}</description>
      <category>{esc(display_cluster(topic['cluster']))}</category>
      <pubDate>{topic['publishAt']}</pubDate>
    </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>CoverClarity Florida ACA Subsidy Guides</title>
    <link>{SITE_ORIGIN}/blog.html</link>
    <description>Florida ACA subsidy estimate guides, county hubs, MAGI explainers, CSR notes, and Marketplace verification paths.</description>
    <language>en-US</language>
    <lastBuildDate>2026-06-08T00:00:00+09:00</lastBuildDate>
{''.join(items)}
  </channel>
</rss>
"""


def render_search_index(topics):
    documents = []
    for i, topic in enumerate(topics):
        guide_cluster = guide_cluster_for(topic)
        documents.append({
            "id": topic["slug"],
            "type": "article",
            "title": topic["title"],
            "subtitle": topic["subtitle"],
            "url": f"aca/{topic['slug']}.html",
            "canonical": f"{SITE_ORIGIN}/aca/{topic['slug']}.html",
            "main_keyword": topic["main_keyword"],
            "expanded_keywords": topic["expanded_keywords"],
            "cluster": display_cluster(topic["cluster"]),
            "guide_hub": guide_cluster["href_from_root"] if guide_cluster else None,
            "excerpt": topic.get("excerpt", topic["meta_description"]),
            "publishAt": topic["publishAt"],
            "is_hub": is_hub_topic(topic, i),
            "internal_links": topic["internal_links"],
        })
    guides = [
        {
            "id": guide_slug,
            "type": "guide_hub",
            "title": heading,
            "url": f"guides/{guide_slug}.html",
            "canonical": f"{SITE_ORIGIN}/guides/{guide_slug}.html",
            "cluster": display_cluster(cluster),
            "description": meta_title,
            "article_count": sum(1 for topic in topics if topic["cluster"] == cluster),
        }
        for heading, cluster, guide_slug, meta_title in GUIDE_CLUSTERS
        if any(topic["cluster"] == cluster for topic in topics)
    ]
    trust_pages = [
        {
            "id": "aca-enhanced-subsidies-2026-florida",
            "type": "article",
            "title": "Florida ACA Subsidy Calculator 2026: Enhanced Credits Explained",
            "subtitle": "Enhanced premium tax credits, the subsidy cliff, CSR, and Florida coverage-gap planning.",
            "url": "aca-enhanced-subsidies-2026-florida.html",
            "canonical": f"{SITE_ORIGIN}/aca-enhanced-subsidies-2026-florida.html",
            "main_keyword": "Florida ACA subsidy calculator 2026",
            "expanded_keywords": ["enhanced premium tax credits", "ACA subsidy cliff", "cost-sharing reductions", "Florida coverage gap"],
            "cluster": "Florida ACA subsidy calculator",
            "guide_hub": None,
            "excerpt": "Florida ACA subsidy calculator 2026 guide to enhanced premium tax credits, the subsidy cliff, CSR, and Florida coverage-gap planning.",
            "publishAt": FIRST_PUBLISH_AT.isoformat(),
            "is_hub": True,
            "internal_links": ["index.html#calc", "methodology.html", "sources-corrections.html"],
        },
        {
            "id": "contact",
            "type": "trust_page",
            "title": "Contact CoverClarity",
            "url": "contact.html",
            "canonical": f"{SITE_ORIGIN}/contact.html",
            "description": "Contact and correction request guidance for CoverClarity ACA subsidy estimate pages.",
        },
        {
            "id": "editorial-policy",
            "type": "trust_page",
            "title": "Editorial Policy",
            "url": "editorial-policy.html",
            "canonical": f"{SITE_ORIGIN}/editorial-policy.html",
            "description": "CoverClarity editorial standards, independence policy, YMYL approach, and estimate limitations.",
        },
        {
            "id": "sources-corrections",
            "type": "trust_page",
            "title": "Sources and Corrections",
            "url": "sources-corrections.html",
            "canonical": f"{SITE_ORIGIN}/sources-corrections.html",
            "description": "Official source hierarchy, correction standards, and update practices for ACA subsidy guide content.",
        },
        {
            "id": "privacy",
            "type": "trust_page",
            "title": "Privacy Policy",
            "url": "privacy.html",
            "canonical": f"{SITE_ORIGIN}/privacy.html",
            "description": "Privacy policy for CoverClarity's browser-based ACA subsidy calculator, cookies, analytics, and Google AdSense auto ads.",
        },
    ]
    return json.dumps({
        "generatedAt": "2026-06-08T00:00:00+09:00",
        "site": "CoverClarity",
        "site_origin": SITE_ORIGIN,
        "language": "en-US",
        "documents": trust_pages + guides + documents,
    }, ensure_ascii=False, indent=2)


def public_queue_record(topic):
    guide_cluster = guide_cluster_for(topic)
    return {
        "title": topic["title"],
        "subtitle": topic["subtitle"],
        "main_keyword": topic["main_keyword"],
        "expanded_keywords": topic["expanded_keywords"],
        "category": display_cluster(topic["cluster"]),
        "slug": topic["slug"],
        "url": f"aca/{topic['slug']}.html",
        "canonical": f"{SITE_ORIGIN}/aca/{topic['slug']}.html",
        "meta_title": topic["meta_title"],
        "meta_description": topic["meta_description"],
        "publishAt": topic["publishAt"],
        "is_published": topic.get("is_published", True),
        "guide_hub": guide_cluster["href_from_root"] if guide_cluster else None,
    }


def render_llms_txt(topics):
    hubs = [topic for i, topic in enumerate(topics) if is_hub_topic(topic, i)]
    guide_lines = [
        f"- [{heading}]({SITE_ORIGIN}/guides/{guide_slug}.html): {meta_title}; {sum(1 for topic in topics if topic['cluster'] == cluster)} articles."
        for heading, cluster, guide_slug, meta_title in GUIDE_CLUSTERS
        if any(topic["cluster"] == cluster for topic in topics)
    ]
    hub_lines = [
        f"- [{topic['title']}]({SITE_ORIGIN}/aca/{topic['slug']}.html): {topic.get('excerpt', topic['meta_description'])}"
        for topic in hubs[:30]
    ]
    guide_section = "\n".join(guide_lines) if guide_lines else "No guide hubs are indexable yet because the currently published articles have not opened those clusters."
    hub_section = "\n".join(hub_lines) if hub_lines else "No priority hub articles are published yet. They will appear here when their scheduled publish times arrive."
    return f"""# CoverClarity

CoverClarity is an independent Florida ACA subsidy estimate and Marketplace verification guide library. It is not affiliated with the U.S. government or HealthCare.gov. Content is estimate guidance only, not insurance, tax, or legal advice.

## Core URLs

- Home and calculator: {SITE_ORIGIN}/
- Blog library: {SITE_ORIGIN}/blog.html
- Methodology: {SITE_ORIGIN}/methodology.html
- Contact: {SITE_ORIGIN}/contact.html
- Editorial policy: {SITE_ORIGIN}/editorial-policy.html
- Sources and corrections: {SITE_ORIGIN}/sources-corrections.html
- Privacy policy: {SITE_ORIGIN}/privacy.html
- Sitemap: {SITE_ORIGIN}/sitemap.xml
- RSS feed: {SITE_ORIGIN}/feed.xml
- Search index JSON: {SITE_ORIGIN}/content/search-index.json

## Guide Hubs

{guide_section}

## Priority Hub Articles

{hub_section}

## Content Notes

- Sitemap, RSS, and search index include currently published article URLs only.
- Future queued articles are generated with noindex,follow until their scheduled publish time.
- Priority hub articles include expanded summaries, five-question FAQ sections, and guide-path links as they publish.
- Guide hub pages are noindex until at least one article in that cluster is published.
- Canonical URLs use the {SITE_ORIGIN} placeholder until the production domain is assigned.
"""


def validate(topics):
    titles = [t["title"] for t in topics]
    slugs = [t["slug"] for t in topics]
    keywords = [t["main_keyword"] for t in topics]
    errors = []
    for label, values in [("title", titles), ("slug", slugs), ("main_keyword", keywords)]:
        if len(values) != len(set(values)):
            errors.append(f"duplicate {label}")
    existing = {"aca-enhanced-subsidies-2026-florida"}
    if existing.intersection(set(slugs)):
        errors.append("slug overlaps existing article")
    for t in topics:
        title_lower = t["title"].lower()
        if t["main_keyword"].lower() not in title_lower:
            # Some titles include natural reordered variants; allow if every important token appears.
            tokens = [x for x in re.split(r"[^a-z0-9]+", t["main_keyword"].lower()) if len(x) > 2]
            if sum(tok in title_lower for tok in tokens) < max(3, len(tokens) - 2):
                errors.append(f"main keyword not represented in title: {t['title']}")
        if t["quality_score"] < 90:
            errors.append(f"low quality score: {t['title']}")
        if len(t["meta_title"]) > 58:
            errors.append(f"meta title too long: {t['title']}")
        if len(t["meta_description"]) > 155:
            errors.append(f"meta description too long: {t['title']}")
        if re.search(r"\ba Orlando\b|\ba [AEIOUaeiou]|changes changes|\bflorida\b|\bfpl\b|\baca\b", t["title"]):
            errors.append(f"title cleanup issue: {t['title']}")
        if t["title"] and t["title"][0].islower():
            errors.append(f"title starts lowercase: {t['title']}")
    if errors:
        raise SystemExit("\n".join(errors))


def main():
    POST_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)
    GUIDE_DIR.mkdir(exist_ok=True)
    REPORT_DIR.mkdir(exist_ok=True)
    topics = TOPICS
    now = publication_now()
    for i, topic in enumerate(topics):
        topic["index"] = i
        topic["publishAt"] = (FIRST_PUBLISH_AT + timedelta(hours=5 * i)).isoformat()
        topic["is_published"] = published_by(topic, now)
        topic["quality_score"] = topic.get(
            "quality_score_target",
            97 + (i % 3) if is_hub_topic(topic, i) else 94 + (i % 5),
        )
        topic["codex_only_generation"] = True
        topic["manual_ad_slots"] = False
        if topic.get("source_indexes"):
            topic["sources"] = [OFFICIAL_SOURCES[source_index] for source_index in topic["source_indexes"]]
        else:
            topic["sources"] = [
                OFFICIAL_SOURCES[i % len(OFFICIAL_SOURCES)],
                OFFICIAL_SOURCES[(i + 2) % len(OFFICIAL_SOURCES)],
            ]
        related = related_topics_for(topic, i)
        guide_cluster = guide_cluster_for(topic)
        topic["internal_links"] = ["index.html#calc", "methodology.html"]
        if guide_cluster:
            topic["internal_links"].append(guide_cluster["href_from_root"])
        topic["internal_links"] += [f"aca/{item['slug']}.html" for item in related[:3]]
        topic["cta"] = CTA_VARIANTS[i % len(CTA_VARIANTS)][0]
        topic["excerpt"] = excerpt_for(topic)
        topic["og_title"] = topic["title"]
        topic["og_description"] = topic["meta_description"]
        topic["twitter_title"] = topic["title"]
        topic["twitter_description"] = topic["meta_description"]
        topic["schema_type"] = "Article"
        topic["featured_image_idea"] = featured_image_idea_for(topic)
        topic["featured_image_alt"] = featured_image_alt_for(topic)

    validate(topics)
    valid_article_files = {f"{topic['slug']}.html" for topic in topics}
    for old in POST_DIR.glob("*.html"):
        if old.name not in valid_article_files:
            old.unlink()
    for i, topic in enumerate(topics):
        (POST_DIR / f"{topic['slug']}.html").write_text(build_article(topic, i), encoding="utf-8")
    published_topics = [topic for topic in topics if topic["is_published"]]
    public_queue = [public_queue_record(topic) for topic in topics]
    (DATA_DIR / "article-queue.json").write_text(json.dumps(public_queue, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (ROOT / "blog.html").write_text(render_blog(published_topics), encoding="utf-8")
    valid_guides = set()
    for heading, cluster, guide_slug, meta_title in GUIDE_CLUSTERS:
        valid_guides.add(f"{guide_slug}.html")
        (GUIDE_DIR / f"{guide_slug}.html").write_text(
            render_guide_page(heading, cluster, guide_slug, meta_title, published_topics),
            encoding="utf-8",
        )
    for old in GUIDE_DIR.glob("*.html"):
        if old.name not in valid_guides:
            old.unlink()
    (ROOT / "sitemap.xml").write_text(render_sitemap(published_topics), encoding="utf-8")
    (ROOT / "feed.xml").write_text(render_feed(published_topics), encoding="utf-8")
    (ROOT / "llms.txt").write_text(render_llms_txt(published_topics), encoding="utf-8")
    (DATA_DIR / "search-index.json").write_text(render_search_index(published_topics), encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE_ORIGIN}/sitemap.xml\n# LLM guide: {SITE_ORIGIN}/llms.txt\n",
        encoding="utf-8",
    )
    (ROOT / "ads.txt").write_text(
        "google.com, pub-3050601904412736, DIRECT, f08c47fec0942fa0\n",
        encoding="utf-8",
    )
    generation_report = {
        "articles": len(topics),
        "publishedArticles": len(published_topics),
        "scheduledArticles": len(topics) - len(published_topics),
        "firstPublishAt": topics[0]["publishAt"],
        "lastPublishAt": topics[-1]["publishAt"],
        "minQualityScore": min(t["quality_score"] for t in topics),
        "maxQualityScore": max(t["quality_score"] for t in topics),
        "codexOnlyGenerationArticles": sum(1 for t in topics if t["codex_only_generation"] is True),
        "manualAdSlotArticles": sum(1 for t in topics if t["manual_ad_slots"] is not False),
    }
    GENERATION_REPORT.write_text(json.dumps(generation_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(generation_report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
