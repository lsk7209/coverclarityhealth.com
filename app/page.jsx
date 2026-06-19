import Link from "next/link";

const comparisons = [
  ["Premium", "Monthly bill before subsidy", 72],
  ["Deductible", "Care paid before plan sharing", 54],
  ["Network", "Doctors and hospitals included", 82],
  ["Maximum", "Worst-case annual exposure", 64],
];

const guides = [
  {
    title: "Total yearly cost",
    text: "Compare premiums, deductible exposure, copays, prescriptions, and expected care instead of ranking plans by premium alone.",
  },
  {
    title: "Enrollment timing",
    text: "Track open enrollment, special enrollment triggers, employer deadlines, and documentation windows before a plan choice becomes urgent.",
  },
  {
    title: "Care access",
    text: "Check network rules, referral requirements, urgent care access, telehealth options, and pharmacy coverage before switching.",
  },
];

export default function HomePage() {
  return (
    <main>
      <header className="topbar">
        <div className="topbar-inner">
          <Link className="brand" href="/">Cover Clarity Health</Link>
          <nav className="nav" aria-label="Primary">
            <Link href="/about">About</Link>
            <Link href="/privacy">Privacy</Link>
            <Link href="/feed.xml">RSS</Link>
          </nav>
        </div>
      </header>

      <section className="hero">
        <div className="section">
          <div>
            <p className="eyebrow">Health coverage decisions, made readable</p>
            <h1>Cover Clarity Health</h1>
            <p className="lead">
              A practical guide hub for comparing health plan costs, coverage rules, enrollment timing,
              and care access without losing the tradeoffs that matter.
            </p>
            <div className="actions">
              <a className="button" href="#compare">Compare factors</a>
              <a className="button secondary" href="#checklist">Review checklist</a>
            </div>
          </div>

          <div className="coverage-visual" aria-label="Coverage factor comparison">
            {comparisons.map(([label, detail, value]) => (
              <div className="visual-row" key={label}>
                <strong>{label}</strong>
                <div>
                  <div className="bar"><span style={{ width: `${value}%` }} /></div>
                  <small>{detail}</small>
                </div>
                <span className="metric">{value}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="section" id="compare">
        <h2>Coverage checks before a plan switch</h2>
        <p className="section-copy">
          The first version of this site focuses on durable plan-comparison basics while deeper guides
          are prepared for publication.
        </p>
        <div className="grid">
          {guides.map((guide) => (
            <article className="card" key={guide.title}>
              <h3>{guide.title}</h3>
              <p>{guide.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section" id="checklist">
        <h2>Decision checklist</h2>
        <ul className="checklist">
          <li>Confirm preferred doctors, hospitals, and pharmacies are in network.</li>
          <li>Estimate annual care usage before comparing out-of-pocket maximums.</li>
          <li>Check whether prescription tiers changed for recurring medication.</li>
          <li>Keep enrollment documents and qualifying-event dates in one place.</li>
        </ul>
      </section>
    </main>
  );
}
