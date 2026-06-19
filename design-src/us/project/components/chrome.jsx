/* ============================================================
   CoverClarity — shared chrome, trust components, icons
   React (Babel). Exports components to window.
   ============================================================ */

/* ---------- Icon set (inline SVG, 1.6 stroke, currentColor) ---------- */
const Icon = ({ name, size = 20, style }) => {
  const p = { width: size, height: size, viewBox: "0 0 24 24", fill: "none",
    stroke: "currentColor", strokeWidth: 1.6, strokeLinecap: "round", strokeLinejoin: "round", style };
  const paths = {
    shield: <><path d="M12 3l7 3v5c0 4.5-3 7.7-7 9-4-1.3-7-4.5-7-9V6l7-3z"/></>,
    info:   <><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 7.5h.01"/></>,
    calc:   <><rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 11h2M12 11h.01M16 11h.01M8 15h2M12 15h.01M16 15v3M8 18h4"/></>,
    doc:    <><path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M10 13h6M10 17h6"/></>,
    book:   <><path d="M5 4h9a3 3 0 013 3v13H8a3 3 0 01-3-3V4z"/><path d="M5 4a3 3 0 00-3 3v10"/></>,
    users:  <><circle cx="9" cy="8" r="3.2"/><path d="M3.5 20a5.5 5.5 0 0111 0"/><path d="M16 5.2A3.2 3.2 0 0117 11M21 20a5.5 5.5 0 00-4-5.3"/></>,
    check:  <><path d="M20 6L9 17l-5-5"/></>,
    arrow:  <><path d="M5 12h14M13 6l6 6-6 6"/></>,
    map:    <><path d="M12 21s7-5.5 7-11a7 7 0 10-14 0c0 5.5 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/></>,
    lock:   <><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 018 0v3"/></>,
    clock:  <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
    scale:  <><path d="M12 3v18M7 21h10M5 7h14M5 7l-2.5 6a3 3 0 005 0L5 7zM19 7l-2.5 6a3 3 0 005 0L19 7zM12 5l-5 2M12 5l5 2"/></>,
    spark:  <><path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3z"/></>,
    edit:   <><path d="M4 20h4l10-10-4-4L4 16v4z"/><path d="M13.5 6.5l4 4"/></>,
    quote:  <><path d="M9 7H5v6h4l-1 4M19 7h-4v6h4l-1 4"/></>,
  };
  return <svg {...p} aria-hidden="true">{paths[name] || paths.info}</svg>;
};

/* ---------- Global non-affiliation banner (top of header) ---------- */
const NonAffilBar = () => (
  <div style={{ background: "var(--ink)", color: "rgba(255,255,255,.82)" }}>
    <div className="wrap" style={{ display: "flex", alignItems: "center", gap: 9,
      padding: "7px 28px", fontSize: ".79rem", justifyContent: "center", textAlign: "center" }}>
      <span style={{ display: "inline-flex", color: "var(--accent)" }}><Icon name="info" size={14} /></span>
      <span><b style={{ color: "#fff", fontWeight: 600 }}>Independent.</b> Not affiliated with the U.S. government or HealthCare.gov.</span>
    </div>
  </div>
);

/* ---------- Wordmark ---------- */
const Wordmark = ({ size = 1 }) => (
  <a href="index.html" style={{ display: "inline-flex", alignItems: "center", gap: 10, textDecoration: "none", color: "var(--ink)" }}>
    <span style={{ width: 34 * size, height: 34 * size, borderRadius: 9, background: "var(--ink)",
      color: "var(--accent)", display: "grid", placeItems: "center", flex: "none" }}>
      <Icon name="scale" size={20 * size} />
    </span>
    <span style={{ fontFamily: "var(--serif)", fontWeight: 600, fontSize: 1.34 * size + "rem", letterSpacing: "-.01em", lineHeight: 1 }}>
      Cover<span style={{ color: "var(--accent-deep)" }}>Clarity</span>
    </span>
  </a>
);

/* ---------- Header ---------- */
const Header = ({ active }) => {
  const nav = [
    { href: "index.html", label: "Calculator" },
    { href: "metro.html", label: "Florida metros" },
    { href: "blog.html", label: "News & guides" },
    { href: "methodology.html", label: "Methodology" },
    { href: "about.html", label: "About" },
  ];
  return (
    <header>
      <NonAffilBar />
      <div style={{ borderBottom: "1px solid var(--line)", background: "var(--paper)", position: "sticky", top: 0, zIndex: 50 }}>
        <div className="wrap-wide spread" style={{ height: 70 }}>
          <Wordmark />
          <nav style={{ display: "flex", gap: 4, alignItems: "center" }} className="mainnav">
            {nav.map(n => (
              <a key={n.href} href={n.href} style={{
                fontSize: ".95rem", fontWeight: active === n.label ? 600 : 500,
                color: active === n.label ? "var(--ink)" : "var(--ink-soft)",
                textDecoration: "none", padding: "8px 13px", borderRadius: 7,
                background: active === n.label ? "var(--paper-2)" : "transparent" }}>
                {n.label}
              </a>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
};

/* ---------- Source citation row ---------- */
const SourceRow = ({ compact }) => (
  <div className="sourcerow" style={compact ? { fontSize: ".8rem" } : null}>
    <span className="src-label">Data sources</span>
    <a href="methodology.html">Illustrative rate model</a>
    <a href="methodology.html">IRS Rev. Proc.</a>
    <a href="methodology.html">HHS Poverty Guidelines</a>
  </div>
);

/* ---------- Date stamp ---------- */
const DateStamp = ({ updated = "Jun 5, 2026", planYear = "2026", regimeAsOf = "Jun 1, 2026" }) => (
  <div className="datestamp tnum">
    <span><b>Last updated</b> {updated}</span>
    <span><b>Plan year</b> {planYear}</span>
    <span><b>Regime as of</b> {regimeAsOf}</span>
  </div>
);

/* ---------- Reviewer credential chip ---------- */
const ReviewerChip = () => (
  <a className="reviewer-chip" href="about.html#reviewer">
    <span className="avatar">DM</span>
    <span>
      <span className="rc-name">Reviewed by Diane Marsh</span>
      <span className="rc-role" style={{ display: "block" }}>Licensed Health Insurance Counselor (FL)</span>
    </span>
  </a>
);

/* ---------- Estimate-not-a-quote chip ---------- */
const EstimateChip = () => (
  <a className="chip chip-accent" href="methodology.html" style={{ textDecoration: "none" }}>
    <Icon name="info" size={14} /> Estimate, not a quote — confirm at HealthCare.gov
  </a>
);

/* ---------- Footer ---------- */
const Footer = () => (
  <footer style={{ background: "var(--ink)", color: "rgba(255,255,255,.72)", marginTop: 72 }}>
    <div className="wrap-wide" style={{ padding: "52px 28px 30px" }}>
      <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr 1fr", gap: 40 }} className="footgrid">
        <div>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
            <span style={{ width: 30, height: 30, borderRadius: 8, background: "rgba(255,255,255,.08)", color: "var(--accent)", display: "grid", placeItems: "center" }}><Icon name="scale" size={18} /></span>
            <span style={{ fontFamily: "var(--serif)", fontWeight: 600, fontSize: "1.22rem", color: "#fff" }}>CoverClarity</span>
          </div>
          <p style={{ fontSize: ".88rem", lineHeight: 1.6, maxWidth: 340, margin: 0 }}>
            Independent, plain-language estimates of Florida ACA Marketplace premiums and subsidies. We inform; you enroll at HealthCare.gov.
          </p>
        </div>
        <div>
          <h4 style={{ fontFamily: "var(--sans)", fontSize: ".8rem", letterSpacing: ".1em", textTransform: "uppercase", color: "rgba(255,255,255,.5)", margin: "0 0 12px" }}>Explore</h4>
          {[["index.html", "Subsidy calculator"], ["metro.html", "Florida metros"], ["blog.html", "News & guides"], ["methodology.html", "Methodology"], ["about.html", "About & standards"]].map(([h, l]) => (
            <a key={h} href={h} style={{ display: "block", color: "rgba(255,255,255,.8)", textDecoration: "none", fontSize: ".9rem", padding: "5px 0" }}>{l}</a>
          ))}
        </div>
        <div>
          <h4 style={{ fontFamily: "var(--sans)", fontSize: ".8rem", letterSpacing: ".1em", textTransform: "uppercase", color: "rgba(255,255,255,.5)", margin: "0 0 12px" }}>Official enrollment</h4>
          <a href="https://www.healthcare.gov" target="_blank" rel="noopener" style={{ display: "inline-flex", alignItems: "center", gap: 7, color: "var(--accent)", textDecoration: "none", fontSize: ".9rem", fontWeight: 600 }}>HealthCare.gov <Icon name="arrow" size={15} /></a>
          <p style={{ fontSize: ".82rem", marginTop: 12, lineHeight: 1.55 }}>Enroll in or change coverage only through the official Marketplace.</p>
        </div>
      </div>

      <hr style={{ border: "none", borderTop: "1px solid rgba(255,255,255,.12)", margin: "30px 0 20px" }} />

      <div style={{ fontSize: ".8rem", lineHeight: 1.6, color: "rgba(255,255,255,.6)", maxWidth: 820 }}>
        <b style={{ color: "rgba(255,255,255,.82)" }}>Disclaimer.</b> CoverClarity provides estimates only. This is not insurance, tax, or legal advice and is not a quote or an offer of coverage. Confirm all coverage details and pricing at HealthCare.gov. Figures shown are illustrative for design demonstration.
      </div>
      <div style={{ marginTop: 18, display: "flex", flexWrap: "wrap", gap: "6px 18px", fontSize: ".8rem", color: "rgba(255,255,255,.55)" }}>
        <span>© 2026 CoverClarity</span>
        <a href="about.html#corrections" style={{ color: "rgba(255,255,255,.7)" }}>Corrections policy</a>
        <a href="methodology.html" style={{ color: "rgba(255,255,255,.7)" }}>Methodology</a>
        <span>Independent — not affiliated with the U.S. government or HealthCare.gov.</span>
      </div>
    </div>
  </footer>
);

Object.assign(window, { Icon, NonAffilBar, Wordmark, Header, SourceRow, DateStamp, ReviewerChip, EstimateChip, Footer });
