/* ============================================================
   CoverClarity — ACA dual-regime subsidy estimator engine
   Pure functions. No DOM, no storage. window.ACA namespace.

   ILLUSTRATIVE ESTIMATES for design demonstration. Premium
   base rates are plausible Florida 2026 placeholders, not
   filed rates. Real tool would load CMS Exchange PUF data.
   ============================================================ */
(function () {
  // --- 2025 HHS Federal Poverty Guidelines (used for 2026 coverage), 48 states ---
  const FPL_BASE = 15650;     // 1 person
  const FPL_ADD  = 5500;      // each additional person
  function fpl(size) { return FPL_BASE + (Math.max(1, size) - 1) * FPL_ADD; }

  // --- Federal default age curve (2018+). age -> rating factor (age 21 = 1.0) ---
  const AGE_CURVE = {
    0:.765,1:.765,2:.765,3:.765,4:.765,5:.765,6:.765,7:.765,8:.765,9:.765,10:.765,
    11:.765,12:.765,13:.765,14:.765,15:.833,16:.859,17:.885,18:.913,19:.941,20:.970,
    21:1.000,22:1.000,23:1.000,24:1.000,25:1.004,26:1.024,27:1.048,28:1.087,29:1.119,
    30:1.135,31:1.159,32:1.183,33:1.198,34:1.214,35:1.222,36:1.230,37:1.238,38:1.246,
    39:1.262,40:1.278,41:1.302,42:1.325,43:1.357,44:1.397,45:1.444,46:1.500,47:1.563,
    48:1.635,49:1.706,50:1.786,51:1.865,52:1.952,53:2.040,54:2.135,55:2.230,56:2.333,
    57:2.437,58:2.548,59:2.603,60:2.714,61:2.810,62:2.873,63:2.952,64:3.000
  };
  function ageFactor(a) { return AGE_CURVE[Math.min(64, Math.max(0, a|0))]; }

  // --- Florida metro rating areas: age-21 benchmark Silver monthly base (illustrative) ---
  const METROS = {
    miami:        { label: "Miami–Fort Lauderdale", base: 485, area: "FL Rating Area 51" },
    tampa:        { label: "Tampa–St. Petersburg", base: 442, area: "FL Rating Area 41" },
    orlando:      { label: "Orlando–Kissimmee",     base: 458, area: "FL Rating Area 38" },
    jacksonville: { label: "Jacksonville",          base: 470, area: "FL Rating Area 21" },
    tallahassee:  { label: "Tallahassee",           base: 505, area: "FL Rating Area 11" }
  };

  const TOBACCO_SURCHARGE = 1.15; // illustrative

  // --- Benchmark (SLCSP) annual premium for a household ---
  // ACA: only the 3 oldest dependents under 21 are charged.
  function benchmarkAnnual(metroKey, ages, tobacco) {
    const base = (METROS[metroKey] || METROS.tampa).base;
    const adults = ages.filter(a => a >= 21).sort((x, y) => y - x);
    const kids   = ages.filter(a => a < 21).sort((x, y) => y - x).slice(0, 3);
    const charged = adults.concat(kids);
    let monthly = 0;
    charged.forEach(a => {
      let p = base * ageFactor(a);
      if (tobacco && a >= 21) p *= TOBACCO_SURCHARGE;
      monthly += p;
    });
    return monthly * 12;
  }

  // --- Applicable percentage schedules (share of income toward benchmark) ---
  function lerp(x, x0, x1, y0, y1) { return y0 + (y1 - y0) * (x - x0) / (x1 - x0); }

  // Enhanced (ARPA/IRA) — in effect through 2025, expired 12/31/2025
  function applicableEnhanced(pct) { // pct = income as % of FPL (e.g. 200)
    if (pct <= 150) return 0;
    if (pct <= 200) return lerp(pct, 150, 200, 0, 2) / 100;
    if (pct <= 250) return lerp(pct, 200, 250, 2, 4) / 100;
    if (pct <= 300) return lerp(pct, 250, 300, 4, 6) / 100;
    if (pct <= 400) return lerp(pct, 300, 400, 6, 8.5) / 100;
    return 8.5 / 100; // no cliff
  }

  // Original (pre-2021) — reverts to this under current law; 400% cliff. (~2021 table, illustrative)
  function applicableOriginal(pct) {
    if (pct < 133) return 2.07 / 100;
    if (pct <= 150) return lerp(pct, 133, 150, 3.10, 4.14) / 100;
    if (pct <= 200) return lerp(pct, 150, 200, 4.14, 6.52) / 100;
    if (pct <= 250) return lerp(pct, 200, 250, 6.52, 8.33) / 100;
    if (pct <= 300) return lerp(pct, 250, 300, 8.33, 9.83) / 100;
    if (pct <= 400) return 9.83 / 100;
    return null; // cliff: no subsidy over 400%
  }

  // --- Main estimate ---
  // input: { metro, ages:[], income, size, tobacco }
  function estimate(input) {
    const size = input.size || input.ages.length || 1;
    const povLine = fpl(size);
    const pct = (input.income / povLine) * 100;
    const benchmark = benchmarkAnnual(input.metro, input.ages, input.tobacco);

    const result = {
      fpl: povLine,
      fplPct: pct,
      benchmarkAnnual: benchmark,
      benchmarkMonthly: benchmark / 12,
      metro: METROS[input.metro] || METROS.tampa,
      csrEligible: pct >= 100 && pct < 250,           // cost-sharing reduction on Silver
      coverageGap: pct < 100,                          // FL non-expansion gap
      regimes: {}
    };

    // helper to build a regime result
    function regime(appPct) {
      if (appPct === null) { // over cliff, original regime
        return { eligible: false, contributionAnnual: null, aptcAnnual: 0,
                 netMonthly: benchmark / 12, creditMonthly: 0 };
      }
      const contribution = appPct * input.income;
      const aptc = Math.max(0, benchmark - contribution);
      const net = Math.max(0, benchmark - aptc);
      return {
        eligible: true,
        appPct: appPct,
        contributionAnnual: contribution,
        aptcAnnual: aptc,
        aptcMonthly: aptc / 12,
        netAnnual: net,
        netMonthly: net / 12,
        creditMonthly: aptc / 12
      };
    }

    result.regimes.enhanced = regime(applicableEnhanced(pct));
    result.regimes.original = regime(applicableOriginal(pct));

    // monthly difference (what you'd pay MORE without enhanced credits)
    result.diffMonthly = result.regimes.original.netMonthly - result.regimes.enhanced.netMonthly;
    return result;
  }

  function money(n, dec) {
    if (n === null || n === undefined || isNaN(n)) return "—";
    return "$" + Number(n).toLocaleString("en-US", { minimumFractionDigits: dec || 0, maximumFractionDigits: dec || 0 });
  }

  window.ACA = { fpl, ageFactor, benchmarkAnnual, estimate, money, METROS,
                 applicableEnhanced, applicableOriginal };
})();
