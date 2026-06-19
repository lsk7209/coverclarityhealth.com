import Script from "next/script";
import "./globals.css";
import { absoluteUrl, getAdsenseClient, getSiteUrl, siteConfig } from "@/lib/site";

export const metadata = {
  metadataBase: new URL(getSiteUrl()),
  title: {
    default: "Cover Clarity Health",
    template: "%s | Cover Clarity Health",
  },
  description: siteConfig.description,
  alternates: {
    canonical: "/",
    types: {
      "application/rss+xml": "/feed.xml",
    },
  },
  openGraph: {
    title: "Cover Clarity Health",
    description: siteConfig.description,
    url: "/",
    siteName: siteConfig.name,
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Cover Clarity Health",
    description: siteConfig.description,
  },
};

export default function RootLayout({ children }) {
  const gaMeasurementId = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID;
  const adsenseClient = getAdsenseClient();
  const enableAdsense = process.env.NEXT_PUBLIC_ENABLE_ADSENSE !== "false";
  const organizationLd = {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: siteConfig.name,
    url: getSiteUrl(),
    description: siteConfig.description,
  };
  const websiteLd = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: siteConfig.name,
    url: getSiteUrl(),
    description: siteConfig.description,
    inLanguage: "en-US",
    potentialAction: {
      "@type": "SearchAction",
      target: `${absoluteUrl("/search")}?q={search_term_string}`,
      "query-input": "required name=search_term_string",
    },
  };

  return (
    <html lang="en">
      <body>
        <div className="site-shell">
          {children}
          <footer className="footer">
            <div className="footer-inner">
              <span>Cover Clarity Health</span>
              <span>Educational information only. Not a broker or insurer.</span>
            </div>
          </footer>
        </div>
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationLd) }} />
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(websiteLd) }} />
        {gaMeasurementId ? (
          <>
            <Script src={`https://www.googletagmanager.com/gtag/js?id=${gaMeasurementId}`} strategy="afterInteractive" />
            <Script id="ga4-pageview" strategy="afterInteractive">
              {`
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());
                gtag('config', '${gaMeasurementId}', { send_page_view: true });
              `}
            </Script>
          </>
        ) : null}
        {enableAdsense ? (
          <Script
            id="adsense-loader"
            async
            src={`https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${adsenseClient}`}
            crossOrigin="anonymous"
            strategy="afterInteractive"
          />
        ) : null}
      </body>
    </html>
  );
}
