export const metadata = {
  title: "About",
  description: "About Cover Clarity Health and its coverage comparison scope.",
  alternates: { canonical: "/about" },
};

export default function AboutPage() {
  return (
    <main className="section">
      <h1>About Cover Clarity Health</h1>
      <p className="lead">
        Cover Clarity Health publishes educational health coverage explainers for readers comparing
        plan costs, care access, enrollment timing, and policy terms.
      </p>
      <p>
        The site is not an insurer, broker, or medical provider. Readers should verify plan documents,
        marketplace notices, and provider-network details before making coverage decisions.
      </p>
    </main>
  );
}
