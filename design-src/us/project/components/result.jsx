/* ============================================================
   CoverClarity — result rendering: policy banner, count-up,
   comparison layouts, coverage-gap & threshold states.
   React (Babel). Exports to window.
   ============================================================ */
const money = (n, d) => window.ACA.money(n, d);

/* ---------- count-up number ---------- */
function useCountUp(target, run, ms = 650) {
  const [val, setVal] = React.useState(run ? 0 : target);
  const raf = React.useRef();
  React.useEffect(() => {
    if (!run) { setVal(target); return; }
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) { setVal(target); return; }
    let start, done = false;
    const tick = (t) => {
      if (!start) start = t;
      const p = Math.min(1, (t - start) / ms);
      const e = 1 - Math.pow(1 - p, 3);
      setVal(target * e);
      if (p < 1) raf.current = requestAnimationFrame(tick);
      else { setVal(target); done = true; }
    };
    raf.current = requestAnimationFrame(tick);
    // guarantee the final value lands even if rAF is throttled (hidden tab / capture)
    const fb = setTimeout(() => { if (!done) setVal(target); }, ms + 140);
    return () => { cancelAnimationFrame(raf.current); clearTimeout(fb); };
  }, [target, run]);
  return val;
}

/* ---------- Policy-status banner (swappable regime messaging) ---------- */
const REGIMES = {
  expired: {
    tone: "neutral",
    label: "Current law as of Jun 5, 2026",
    text: <>The enhanced premium tax credits <b>expired December 31, 2025</b>. Current-law estimates use the pre-2021 rules. We update this when Congress acts.</>,
  },
  extended: {
    tone: "good",
    label: "Current law as of Jun 5, 2026",
    text: <>Congress <b>extended the enhanced premium tax credits</b>. Both columns below reflect the enhanced rules. We update this if the law changes.</>,
  },
  compromise: {
    tone: "warn",
    label: "Current law as of Jun 5, 2026",
    text: <>A <b>partial compromise</b> is in effect — enhanced credits continue at reduced levels. Estimates blend both regimes. We update this as rules are finalized.</>,
  },
};
const PolicyBanner = ({ regime = "expired" }) => {
  const r = REGIMES[regime] || REGIMES.expired;
  const bg = { neutral: "var(--paper-2)", good: "var(--favorable-tint)", warn: "var(--accent-wash)" }[r.tone];
  const bd = { neutral: "var(--line-2)", good: "var(--favorable-line)", warn: "#E8D2A6" }[r.tone];
  const ic = { neutral: "var(--quiet)", good: "var(--favorable-deep)", warn: "var(--accent-deep)" }[r.tone];
  return (
    <div role="status" style={{ background: bg, border: "1px solid " + bd, borderRadius: "var(--r)",
      padding: "13px 16px", display: "flex", gap: 12, alignItems: "flex-start" }}>
      <span style={{ color: ic, flex: "none", marginTop: 1 }}><Icon name="info" size={18} /></span>
      <div>
        <div className="eyebrow" style={{ color: ic, marginBottom: 3 }}>{r.label}</div>
        <div style={{ fontSize: ".93rem", lineHeight: 1.5, color: "var(--ink-soft)" }}>{r.text}</div>
      </div>
    </div>
  );
};

/* ---------- small column header used across layouts ---------- */
const ColTag = ({ kind, children }) => {
  const fav = kind === "fav";
  return (
    <div style={{ display: "inline-flex", alignItems: "center", gap: 7 }}>
      <span aria-hidden="true" style={{ width: 11, height: 11, borderRadius: 3,
        background: fav ? "var(--favorable)" : "var(--increase)",
        backgroundImage: fav ? "none" : "repeating-linear-gradient(45deg, rgba(255,255,255,.45) 0 2px, transparent 2px 4px)" }} />
      <span style={{ fontWeight: 600, fontSize: ".9rem", color: fav ? "var(--favorable-deep)" : "var(--increase-deep)" }}>{children}</span>
    </div>
  );
};

/* ---------- big monetary figure ---------- */
const BigMoney = ({ value, run, color, sub }) => {
  const v = useCountUp(value, run);
  return (
    <div>
      <div className="tnum" style={{ fontFamily: "var(--serif)", fontWeight: 600, lineHeight: 1,
        fontSize: "clamp(2.6rem, 5vw, 3.4rem)", color, letterSpacing: "-.02em" }}>
        {money(v)}<span style={{ fontSize: ".4em", fontWeight: 500, color: "var(--quiet)", fontFamily: "var(--sans)" }}>/mo</span>
      </div>
      {sub && <div className="caption" style={{ marginTop: 4 }}>{sub}</div>}
    </div>
  );
};

/* ---------- COMPARISON — cards layout (default) ---------- */
const ComparisonCards = ({ res, run }) => {
  const e = res.regimes.enhanced, o = res.regimes.original;
  return (
    <div className="cmp-cards" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
      <div style={{ background: "var(--favorable-tint)", border: "1px solid var(--favorable-line)", borderRadius: "var(--r)", padding: "20px 22px" }}>
        <ColTag kind="fav">With enhanced credits</ColTag>
        <div className="caption" style={{ margin: "3px 0 14px" }}>The expired/enhanced rules — favorable</div>
        <BigMoney value={e.netMonthly} run={run} color="var(--favorable-deep)" sub="You'd pay each month" />
      </div>
      <div style={{ background: "var(--increase-tint)", border: "1px solid var(--increase-line)", borderRadius: "var(--r)", padding: "20px 22px" }}>
        <ColTag kind="inc">Without enhanced credits</ColTag>
        <div className="caption" style={{ margin: "3px 0 14px" }}>Current law — pre-2021 rules</div>
        {o.eligible
          ? <BigMoney value={o.netMonthly} run={run} color="var(--increase-deep)" sub="You'd pay each month" />
          : <div><div style={{ fontFamily: "var(--serif)", fontWeight: 600, fontSize: "1.7rem", color: "var(--increase-deep)", lineHeight: 1.1 }}>No tax credit</div><div className="caption" style={{ marginTop: 6 }}>Over 400% FPL — full price under current law</div></div>}
      </div>
    </div>
  );
};

/* ---------- COMPARISON — bars layout ---------- */
const ComparisonBars = ({ res, run }) => {
  const e = res.regimes.enhanced, o = res.regimes.original;
  const max = Math.max(e.netMonthly, o.netMonthly, res.benchmarkMonthly) * 1.05;
  const we = useCountUp((e.netMonthly / max) * 100, run);
  const wo = useCountUp(((o.eligible ? o.netMonthly : res.benchmarkMonthly) / max) * 100, run);
  const Bar = ({ w, color, striped, label, sub, val }) => (
    <div style={{ marginBottom: 18 }}>
      <div className="spread" style={{ marginBottom: 6 }}><ColTag kind={color === "fav" ? "fav" : "inc"}>{label}</ColTag>
        <span className="tnum" style={{ fontWeight: 700, fontFamily: "var(--serif)", fontSize: "1.5rem", color: color === "fav" ? "var(--favorable-deep)" : "var(--increase-deep)" }}>{money(val)}<span style={{ fontSize: ".55rem", color: "var(--quiet)", fontFamily: "var(--sans)" }}>/mo</span></span></div>
      <div style={{ height: 26, background: "var(--paper-2)", borderRadius: 6, overflow: "hidden", border: "1px solid var(--line)" }}>
        <div style={{ width: w + "%", height: "100%", borderRadius: 6,
          background: color === "fav" ? "var(--favorable)" : "var(--increase)",
          backgroundImage: striped ? "repeating-linear-gradient(45deg, rgba(255,255,255,.32) 0 6px, transparent 6px 12px)" : "none",
          transition: "width .1s linear" }} />
      </div>
      <div className="caption" style={{ marginTop: 4 }}>{sub}</div>
    </div>
  );
  return (
    <div>
      <Bar w={we} color="fav" label="With enhanced credits" val={e.netMonthly} sub="Favorable — expired/enhanced rules" />
      <Bar w={wo} color="inc" striped label="Without enhanced credits" val={o.eligible ? o.netMonthly : res.benchmarkMonthly} sub={o.eligible ? "Current law — pre-2021 rules" : "No credit over 400% FPL — full benchmark price"} />
    </div>
  );
};

/* ---------- COMPARISON — ledger layout ---------- */
const ComparisonLedger = ({ res, run }) => {
  const e = res.regimes.enhanced, o = res.regimes.original;
  const rows = [
    ["Benchmark Silver plan (SLCSP)", money(res.benchmarkMonthly) + "/mo", money(res.benchmarkMonthly) + "/mo"],
    ["Estimated tax credit", "−" + money(e.creditMonthly) + "/mo", o.eligible ? "−" + money(o.creditMonthly) + "/mo" : "—"],
  ];
  return (
    <div style={{ border: "1px solid var(--line)", borderRadius: "var(--r)", overflow: "hidden" }}>
      <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr 1fr" }}>
        <div style={{ padding: "12px 16px", background: "var(--paper-2)", fontWeight: 600, fontSize: ".85rem", color: "var(--quiet)" }}>Per month</div>
        <div style={{ padding: "12px 16px", background: "var(--favorable-tint)" }}><ColTag kind="fav">With enhanced</ColTag></div>
        <div style={{ padding: "12px 16px", background: "var(--increase-tint)" }}><ColTag kind="inc">Current law</ColTag></div>
        {rows.map((r, i) => (
          <React.Fragment key={i}>
            <div style={{ padding: "12px 16px", borderTop: "1px solid var(--line)", fontSize: ".92rem" }}>{r[0]}</div>
            <div className="tnum" style={{ padding: "12px 16px", borderTop: "1px solid var(--line)", textAlign: "right", fontWeight: 500 }}>{r[1]}</div>
            <div className="tnum" style={{ padding: "12px 16px", borderTop: "1px solid var(--line)", textAlign: "right", fontWeight: 500 }}>{r[2]}</div>
          </React.Fragment>
        ))}
        <div style={{ padding: "14px 16px", borderTop: "2px solid var(--line-2)", fontWeight: 700, background: "var(--card)" }}>You'd pay</div>
        <div className="tnum" style={{ padding: "14px 16px", borderTop: "2px solid var(--line-2)", textAlign: "right", fontWeight: 700, fontSize: "1.25rem", color: "var(--favorable-deep)", background: "var(--card)" }}>{money(e.netMonthly)}</div>
        <div className="tnum" style={{ padding: "14px 16px", borderTop: "2px solid var(--line-2)", textAlign: "right", fontWeight: 700, fontSize: "1.25rem", color: "var(--increase-deep)", background: "var(--card)" }}>{o.eligible ? money(o.netMonthly) : "Full price"}</div>
      </div>
    </div>
  );
};

Object.assign(window, { useCountUp, PolicyBanner, ColTag, BigMoney, ComparisonCards, ComparisonBars, ComparisonLedger, REGIMES });
