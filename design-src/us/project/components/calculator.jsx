/* ============================================================
   CoverClarity — calculator form + result orchestrator
   React (Babel). Exports Calculator, ResultBlock to window.
   ============================================================ */
const m$ = (n, d) => window.ACA.money(n, d);

/* ---------- difference figure ---------- */
const DiffFigure = ({ res, run }) => {
  const diff = useCountUp(Math.max(0, res.diffMonthly), run);
  const yearly = Math.max(0, res.diffMonthly) * 12;
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 14, flexWrap: "wrap",
      background: "var(--ink)", color: "#fff", borderRadius: "var(--r)", padding: "18px 24px", textAlign: "center" }}>
      <span style={{ fontSize: "1rem", color: "rgba(255,255,255,.78)" }}>Without the enhanced credits, you'd pay</span>
      <span className="tnum" style={{ fontFamily: "var(--serif)", fontWeight: 600, fontSize: "2.1rem", color: "var(--accent)", lineHeight: 1 }}>{m$(diff)}</span>
      <span style={{ fontSize: "1rem", color: "rgba(255,255,255,.78)" }}>more per month <span style={{ color: "rgba(255,255,255,.5)" }}>· about {m$(yearly)}/yr</span></span>
    </div>
  );
};

/* ---------- CSR note ---------- */
const CSRNote = () => (
  <div style={{ display: "flex", gap: 11, alignItems: "flex-start", background: "var(--favorable-tint)", border: "1px solid var(--favorable-line)", borderRadius: "var(--r)", padding: "13px 16px" }}>
    <span style={{ color: "var(--favorable-deep)", flex: "none", marginTop: 1 }}><Icon name="spark" size={17} /></span>
    <div style={{ fontSize: ".92rem", lineHeight: 1.5 }}>
      <b style={{ color: "var(--favorable-deep)" }}>You likely qualify for extra savings (CSR).</b> Because your income is under 250% of the federal poverty level, choosing a <b>Silver</b> plan adds cost-sharing reductions — lower deductibles and copays — at no extra premium. <a href="article.html">How CSR works →</a>
    </div>
  </div>
);

/* ---------- Florida Medicaid coverage-gap state ---------- */
const CoverageGapBlock = () => (
  <div style={{ background: "var(--card)", border: "1px solid var(--line-2)", borderRadius: "var(--r-lg)", padding: "26px 28px" }}>
    <div className="chip chip-quiet" style={{ marginBottom: 14 }}><Icon name="map" size={14} /> Florida coverage gap</div>
    <h3 className="h3" style={{ marginBottom: 10 }}>Your income may fall into Florida's coverage gap</h3>
    <p style={{ margin: "0 0 14px", color: "var(--ink-soft)", maxWidth: 620 }}>
      Florida did not expand Medicaid, so people earning <b>below about 100% of the federal poverty level</b> often earn too little to get a Marketplace tax credit, but too much for Florida Medicaid. We won't show a misleading subsidy number here.
    </p>
    <div className="panel" style={{ padding: "16px 18px", marginBottom: 16 }}>
      <div style={{ fontWeight: 600, marginBottom: 6 }}>What you can do</div>
      <ul style={{ margin: 0, paddingLeft: 20, color: "var(--ink-soft)", lineHeight: 1.7, fontSize: ".95rem" }}>
        <li>Double-check your <b>estimated 2026 income</b> — even a small increase can qualify you for large savings.</li>
        <li>See if you qualify for <b>Florida Medicaid or KidCare</b> (children often still qualify).</li>
        <li>Find free local help from a <b>Navigator</b> or certified assister.</li>
      </ul>
    </div>
    <div className="row-wrap">
      <a className="btn btn-primary" href="https://www.healthcare.gov/medicaid-chip/" target="_blank" rel="noopener">Check Medicaid & KidCare <Icon name="arrow" size={16} /></a>
      <a className="btn btn-ghost" href="article.html">Read: the coverage gap explained</a>
    </div>
  </div>
);

/* ---------- Result block orchestrator ---------- */
const ResultBlock = ({ res, run, regime, layout = "cards", showAd = true }) => {
  const Cmp = { cards: ComparisonCards, bars: ComparisonBars, ledger: ComparisonLedger }[layout] || ComparisonCards;
  const over400 = !res.regimes.original.eligible;
  return (
    <div className="stack" style={{ "--gap": "18px" }}>
      <PolicyBanner regime={regime} />

      {res.coverageGap ? <CoverageGapBlock /> : (
        <React.Fragment>
          <div className="spread" style={{ flexWrap: "wrap", gap: 10 }}>
            <div>
              <div className="eyebrow">Your estimated monthly premium</div>
              <div className="caption tnum" style={{ marginTop: 2 }}>
                {res.metro.label} · household of {res.householdSize} · {m$(res.income)}/yr · {Math.round(res.fplPct)}% FPL
              </div>
            </div>
            <EstimateChip />
          </div>

          <Cmp res={res} run={run} />
          <DiffFigure res={res} run={run} />

          {/* transparent breakdown */}
          <div className="panel" style={{ padding: "16px 18px" }}>
            <div className="spread" style={{ marginBottom: 8 }}>
              <div style={{ fontWeight: 600, fontSize: ".95rem" }}>How we got there</div>
              <a href="methodology.html" style={{ fontSize: ".85rem" }}>Methodology →</a>
            </div>
            <div className="tnum" style={{ display: "grid", gridTemplateColumns: "1fr auto", rowGap: 7, columnGap: 16, fontSize: ".92rem", color: "var(--ink-soft)" }}>
              <span>Benchmark Silver plan (SLCSP)</span><span style={{ textAlign: "right", fontWeight: 600 }}>{m$(res.benchmarkMonthly)}/mo</span>
              <span>Estimated credit — enhanced rules</span><span style={{ textAlign: "right", fontWeight: 600, color: "var(--favorable-deep)" }}>−{m$(res.regimes.enhanced.creditMonthly)}/mo</span>
              <span>Estimated credit — current law</span><span style={{ textAlign: "right", fontWeight: 600, color: "var(--increase-deep)" }}>{over400 ? "none" : "−" + m$(res.regimes.original.creditMonthly) + "/mo"}</span>
            </div>
          </div>

          {res.csrEligible && <CSRNote />}
          {over400 && (
            <div style={{ display: "flex", gap: 11, alignItems: "flex-start", background: "var(--increase-tint)", border: "1px solid var(--increase-line)", borderRadius: "var(--r)", padding: "13px 16px" }}>
              <span style={{ color: "var(--increase-deep)", flex: "none", marginTop: 1 }}><Icon name="info" size={17} /></span>
              <div style={{ fontSize: ".92rem", lineHeight: 1.5 }}>
                <b style={{ color: "var(--increase-deep)" }}>Above 400% of the poverty level.</b> Under current law there's a "subsidy cliff" — no premium tax credit at all. The enhanced rules removed that cliff, which is why the two columns differ so much.
              </div>
            </div>
          )}

          {res.input && <ResultShare inp={res.input} res={res} />}

          <div className="spread" style={{ flexWrap: "wrap", gap: 12, paddingTop: 4 }}>
            <DateStamp />
            <div className="nonaffil"><Icon name="lock" size={15} /> Your numbers stay in your browser — nothing is saved or sent.</div>
          </div>
        </React.Fragment>
      )}

      {showAd && (
        <div className="adslot" style={{ marginTop: 6 }}>
          <span className="adnote">Responsive ad · 728×90 / 300×250 — clearly separated from results</span>
        </div>
      )}
    </div>
  );
};

/* ---------- deep-link query helpers ---------- */
function buildQuery(inp) {
  const p = new URLSearchParams();
  p.set("metro", inp.metro); p.set("size", inp.size);
  p.set("ages", inp.ages.join("-")); p.set("income", inp.income);
  if (inp.tobacco) p.set("tobacco", "1");
  return p.toString();
}
function parseQuery() {
  const p = new URLSearchParams(location.search);
  if (!p.has("metro") && !p.has("income")) return null;
  const out = {};
  if (p.has("metro") && window.ACA.METROS[p.get("metro")]) out.metro = p.get("metro");
  if (p.has("size")) out.size = Math.max(1, Math.min(8, parseInt(p.get("size"), 10) || 1));
  if (p.has("ages")) out.ages = p.get("ages").split("-").map(a => parseInt(a, 10) || 0).filter((_, i) => i < (out.size || 8));
  if (p.has("income")) out.income = parseInt(p.get("income"), 10) || 0;
  out.tobacco = p.get("tobacco") === "1";
  if (out.ages && out.size && out.ages.length !== out.size) out.size = out.ages.length;
  return out;
}

/* ---------- share / deep-link strip on results ---------- */
function ResultShare({ inp, res }) {
  const [copied, setCopied] = React.useState("");
  const flash = (w) => { setCopied(w); setTimeout(() => setCopied(""), 1800); };
  const copyLink = () => {
    const url = location.origin + location.pathname + "?" + buildQuery(inp);
    (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject()).then(() => flash("link")).catch(() => { history.replaceState(null, "", location.pathname + "?" + buildQuery(inp)); flash("link"); });
  };
  const copySummary = () => {
    const o = res.regimes.original;
    const txt = `${res.metro.label}, household of ${res.householdSize}, about $${Number(res.income).toLocaleString("en-US")}/yr: roughly $${Math.round(res.regimes.enhanced.netMonthly)}/mo with the enhanced ACA premium credits vs ${o.eligible ? "$" + Math.round(o.netMonthly) + "/mo" : "full price"} under current law (about $${Math.round(Math.max(0, res.diffMonthly))}/mo more). Estimate via CoverClarity — not a quote; confirm at HealthCare.gov.`;
    (navigator.clipboard ? navigator.clipboard.writeText(txt) : Promise.reject()).then(() => flash("summary")).catch(() => flash("summary"));
  };
  return (
    <div className="panel" style={{ padding: "14px 16px", display: "flex", alignItems: "center", justifyContent: "space-between", gap: 14, flexWrap: "wrap" }}>
      <div className="row" style={{ gap: 9 }}>
        <span style={{ color: "var(--accent-deep)", flex: "none" }}><Icon name="spark" size={17} /></span>
        <div style={{ lineHeight: 1.3 }}>
          <div style={{ fontWeight: 600, fontSize: ".95rem" }}>Share this estimate</div>
          <div className="caption">A private link that re-opens these exact numbers — no personal data in it.</div>
        </div>
      </div>
      <div className="row-wrap" style={{ gap: 8 }}>
        <button className="btn btn-ghost" style={{ padding: "9px 14px", fontSize: ".9rem" }} onClick={copyLink}>
          <Icon name="lock" size={15} /> {copied === "link" ? "Link copied!" : "Copy link"}
        </button>
        <button className="btn btn-ghost" style={{ padding: "9px 14px", fontSize: ".9rem" }} onClick={copySummary}>
          <Icon name="quote" size={15} /> {copied === "summary" ? "Copied!" : "Copy summary"}
        </button>
      </div>
    </div>
  );
}

/* ---------- The calculator form ---------- */
const DEFAULT_INPUT = { metro: "tampa", zip: "33602", size: 4, ages: [40, 38, 10, 8], income: 64300, tobacco: false };

function Calculator({ initial, regime = "expired", layout = "cards", startOpen = false, showAd = true, embedded = false }) {
  const [inp, setInp] = React.useState(() => {
    const base = { ...DEFAULT_INPUT, ...(initial || {}) };
    if (!embedded) { const q = parseQuery(); if (q) return { ...base, ...q }; }
    return base;
  });
  const [showResults, setShowResults] = React.useState(startOpen);
  const [animKey, setAnimKey] = React.useState(0);
  const [moreOpen, setMoreOpen] = React.useState(false);
  const cardRef = React.useRef(null);

  // reserve room for the mobile sticky CTA (only the primary, non-embedded calculator)
  React.useEffect(() => {
    if (embedded) return;
    document.body.classList.add("has-mobile-cta");
    return () => document.body.classList.remove("has-mobile-cta");
  }, [embedded]);

  function scrollToCard() {
    if (!cardRef.current) return;
    const y = cardRef.current.getBoundingClientRect().top + window.scrollY - 80;
    window.scrollTo({ top: y, behavior: "smooth" });
  }

  // keep ages array length synced to household size
  function setSize(n) {
    n = Math.max(1, Math.min(8, n));
    setInp(s => {
      const ages = s.ages.slice(0, n);
      while (ages.length < n) ages.push(ages.length === 0 ? 40 : 30 - (ages.length - 1) * 2);
      return { ...s, size: n, ages };
    });
  }
  function setAge(i, v) {
    setInp(s => { const ages = s.ages.slice(); ages[i] = Math.max(0, Math.min(99, parseInt(v || 0, 10))); return { ...s, ages }; });
  }
  function calc() {
    setShowResults(true); setAnimKey(k => k + 1);
    if (!embedded) { try { history.replaceState(null, "", location.pathname + "?" + buildQuery(inp)); } catch (e) {} }
  }

  const res = window.ACA.estimate(inp);
  res.householdSize = inp.size; res.income = inp.income; res.input = inp;

  const moneyFmt = (n) => Number(n).toLocaleString("en-US");

  return (
    <React.Fragment>
    <div className="card" ref={cardRef} style={{ padding: embedded ? "22px" : "26px 28px", scrollMarginTop: 90 }}>
      <div className="spread" style={{ marginBottom: 16, flexWrap: "wrap", gap: 8 }}>
        <div className="row" style={{ gap: 10 }}>
          <span style={{ width: 30, height: 30, borderRadius: 8, background: "var(--accent-tint)", color: "var(--accent-deep)", display: "grid", placeItems: "center", flex: "none" }}><Icon name="calc" size={18} /></span>
          <span style={{ fontFamily: "var(--serif)", fontWeight: 600, fontSize: "1.18rem" }}>Estimate your 2026 premium</span>
        </div>
        <span className="chip chip-quiet"><Icon name="lock" size={13} /> Nothing saved or sent</span>
      </div>

      {/* inputs */}
      <div style={{ display: "grid", gridTemplateColumns: embedded ? "1fr" : "1fr 1fr", gap: 16 }} className="calc-grid">
        <div className="field">
          <label className="field-label" htmlFor="cc-metro">Where in Florida do you live?</label>
          <select id="cc-metro" className="select" value={inp.metro} onChange={e => setInp(s => ({ ...s, metro: e.target.value }))}>
            {Object.entries(window.ACA.METROS).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
          </select>
          <div className="field-hint">Resolves to your {res.metro.area}.</div>
        </div>

        <div className="field">
          <label className="field-label" htmlFor="cc-income">Estimated 2026 household income</label>
          <div className="input-prefix">
            <span className="pfx">$</span>
            <input id="cc-income" className="input tnum" inputMode="numeric" value={moneyFmt(inp.income)}
              onChange={e => setInp(s => ({ ...s, income: parseInt(e.target.value.replace(/[^0-9]/g, "") || 0, 10) }))} />
          </div>
          <div className="field-hint tnum">About {Math.round(res.fplPct)}% of the federal poverty level for a household of {inp.size}.</div>
        </div>

        <div className="field">
          <label className="field-label">How many people need coverage?</label>
          <div className="stepper" role="group" aria-label="Household size">
            <button type="button" aria-label="Fewer" onClick={() => setSize(inp.size - 1)}>−</button>
            <span className="val tnum">{inp.size}</span>
            <button type="button" aria-label="More" onClick={() => setSize(inp.size + 1)}>+</button>
          </div>
        </div>

        <div className="field">
          <label className="field-label">Age of each person</label>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {inp.ages.map((a, i) => (
              <input key={i} className="input tnum" aria-label={"Person " + (i + 1) + " age"} inputMode="numeric"
                style={{ width: 64, textAlign: "center", padding: "10px 6px" }} value={a} onChange={e => setAge(i, e.target.value)} />
            ))}
          </div>
        </div>
      </div>

      {/* progressive disclosure: more options */}
      <button type="button" onClick={() => setMoreOpen(o => !o)} style={{ marginTop: 14, background: "none", border: "none", color: "var(--accent-deep)", fontFamily: "var(--sans)", fontWeight: 600, fontSize: ".9rem", cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 6, padding: 0 }}>
        {moreOpen ? "Hide" : "More options"} <span style={{ transform: moreOpen ? "rotate(180deg)" : "none", transition: ".2s" }}>▾</span>
      </button>
      {moreOpen && (
        <div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 14, flexWrap: "wrap" }}>
          <span className="field-label" style={{ margin: 0 }}>Does anyone use tobacco?</span>
          <div className="seg">
            <button type="button" aria-pressed={!inp.tobacco} onClick={() => setInp(s => ({ ...s, tobacco: false }))}>No</button>
            <button type="button" aria-pressed={inp.tobacco} onClick={() => setInp(s => ({ ...s, tobacco: true }))}>Yes</button>
          </div>
          <span className="field-hint" style={{ margin: 0 }}>May raise the premium insurers can charge.</span>
        </div>
      )}

      <button className="btn btn-primary btn-lg btn-block" style={{ marginTop: 20 }} onClick={calc}>
        {showResults ? "Update estimate" : "See my estimate"} <Icon name="arrow" size={18} />
      </button>

      {showResults && (
        <div key={animKey} style={{ marginTop: 24, paddingTop: 22, borderTop: "1px solid var(--line)" }}>
          <ResultBlock res={res} run={true} regime={regime} layout={layout} showAd={showAd} />
        </div>
      )}
    </div>

    {!embedded && (
      <div className="calc-sticky" aria-hidden={false}>
        {showResults && !res.coverageGap ? (
          <React.Fragment>
            <div style={{ lineHeight: 1.2 }}>
              <div style={{ fontSize: ".74rem", color: "var(--quiet)" }}>Without enhanced credits</div>
              <div className="tnum" style={{ fontWeight: 700, color: "var(--increase-deep)", fontSize: "1.12rem" }}>+{m$(Math.max(0, res.diffMonthly))}/mo more</div>
            </div>
            <button className="btn btn-primary" onClick={scrollToCard}><Icon name="edit" size={16} /> Adjust</button>
          </React.Fragment>
        ) : (
          <React.Fragment>
            <div style={{ fontWeight: 600 }}>See your 2026 estimate</div>
            <button className="btn btn-primary" onClick={() => { calc(); setTimeout(scrollToCard, 60); }}>Calculate <Icon name="arrow" size={16} /></button>
          </React.Fragment>
        )}
      </div>
    )}
    </React.Fragment>
  );
}

Object.assign(window, { Calculator, ResultBlock, DiffFigure, CSRNote, CoverageGapBlock });
