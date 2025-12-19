const $ = (id) => document.getElementById(id);

let chart;

// ---------------------
// UI helpers
// ---------------------
function setStatus(msg) {
  const el = $("status");
  if (el) el.textContent = msg || "";
}

function setBadge(text) {
  const b = $("recBadge");
  if (!b) return;

  const rec = (text || "—").toUpperCase();
  b.textContent = rec;

  // subtle border hint (Apple-ish, not loud)
  if (rec === "BUY") b.style.borderColor = "rgba(0,128,0,.35)";
  else if (rec === "SELL") b.style.borderColor = "rgba(180,0,0,.35)";
  else if (rec === "HOLD") b.style.borderColor = "rgba(120,120,0,.35)";
  else b.style.borderColor = "rgba(0,0,0,.10)";
}

function fmtNum(v) {
  if (v === null || v === undefined) return "—";
  const n = Number(v);
  if (Number.isFinite(n)) return n.toLocaleString(undefined, { maximumFractionDigits: 2 });
  return String(v);
}

function fmtPct(v) {
  if (v === null || v === undefined) return "—";
  const n = Number(v);
  if (!Number.isFinite(n)) return String(v);
  return (n * 100).toFixed(2) + "%";
}

// ---------------------
// Chart
// ---------------------
function ensureChart() {
  const ctx = $("chart");
  if (!ctx) return null;
  if (chart) return chart;

  chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["RSI", "MACD", "Signal", "Volatility", "Sharpe", "Cur Drawdown"],
      datasets: [{
        label: "Snapshot",
        data: [0, 0, 0, 0, 0, 0],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: { enabled: true }
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  });

  return chart;
}

// ---------------------
// RSI gauge
// ---------------------
function rsiLabel(rsi) {
  if (!Number.isFinite(rsi)) return "—";
  if (rsi < 30) return "Oversold";
  if (rsi > 70) return "Overbought";
  return "Neutral";
}

function setRsiGauge(rsi) {
  const ring = $("rsiRing");
  const big = $("rsiBig");
  const tag = $("rsiTag");

  if (!ring || !big || !tag) return;

  if (!Number.isFinite(rsi)) {
    big.textContent = "—";
    tag.textContent = "—";
    ring.style.strokeDashoffset = 289;
    return;
  }

  const p = Math.max(0, Math.min(1, rsi / 100));
  const circumference = 289;
  ring.style.strokeDashoffset = String(circumference * (1 - p));
  big.textContent = rsi.toFixed(2);
  tag.textContent = rsiLabel(rsi);
}

// ---------------------
// UI-side recommendation engine
// (does NOT touch backend)
// ---------------------
function deriveRecommendation(tech, risk) {
  const rsi = Number(tech?.rsi_14);
  const trendRaw = tech?.trend ?? "";
  const trend = String(trendRaw).toLowerCase();

  const sharpe = Number(risk?.sharpe_ratio);
  const drawdown = Number(risk?.current_drawdown);
  const vol = Number(risk?.volatility);

  // Defaults
  let recommendation = "HOLD";
  let riskLevel = "Moderate";

  // Rules (conservative + explainable)
  // BUY: bullish + not overbought + decent sharpe
  if (trend === "bullish" && Number.isFinite(rsi) && rsi < 70 && Number.isFinite(sharpe) && sharpe >= 0.5) {
    recommendation = "BUY";
  }

  // SELL: bearish + meaningful drawdown risk
  if (trend === "bearish" && Number.isFinite(drawdown) && drawdown < -0.15) {
    recommendation = "SELL";
  }

  // Risk level
  if ((Number.isFinite(vol) && vol >= 0.35) || (Number.isFinite(drawdown) && drawdown < -0.30)) {
    riskLevel = "High";
  } else if ((Number.isFinite(vol) && vol < 0.20) && (Number.isFinite(sharpe) && sharpe >= 0.7)) {
    riskLevel = "Low";
  }

  const reasoningParts = [];
  reasoningParts.push(`Trend is ${trendRaw || "—"} with RSI at ${Number.isFinite(rsi) ? rsi.toFixed(2) : "—"}.`);
  reasoningParts.push(`Volatility is ${Number.isFinite(vol) ? vol.toFixed(2) : "—"} and Sharpe is ${Number.isFinite(sharpe) ? sharpe.toFixed(2) : "—"}.`);
  if (Number.isFinite(drawdown)) {
    reasoningParts.push(`Current drawdown is ${(drawdown * 100).toFixed(2)}%.`);
  }

  const drivers = [
    `Trend signal: ${trendRaw || "—"}`,
    `RSI (14): ${Number.isFinite(rsi) ? rsi.toFixed(2) : "—"}`,
    `Sharpe ratio: ${Number.isFinite(sharpe) ? sharpe.toFixed(2) : "—"}`,
    `Volatility: ${Number.isFinite(vol) ? vol.toFixed(2) : "—"}`,
    `Drawdown: ${Number.isFinite(drawdown) ? (drawdown * 100).toFixed(2) + "%" : "—"}`
  ];

  return { recommendation, riskLevel, reasoning: reasoningParts.join(" "), drivers };
}

// Prefer backend values if they exist, else use derived UI values
function pickRecommendationPackage(data, tech, riskm) {
  const backendHasAny =
    data?.recommendation || data?.risk_level || data?.reasoning || (Array.isArray(data?.key_drivers) && data.key_drivers.length);

  if (backendHasAny) {
    return {
      recommendation: (data.recommendation ?? "HOLD").toUpperCase(),
      riskLevel: data.risk_level ?? "Moderate",
      reasoning: data.reasoning ?? "—",
      drivers: Array.isArray(data.key_drivers) && data.key_drivers.length ? data.key_drivers : []
    };
  }

  return deriveRecommendation(tech, riskm);
}

// ---------------------
// Main action
// ---------------------
async function analyze() {
  const tickerInput = $("ticker");
  const runBtn = $("run");

  const ticker = (tickerInput?.value || "").trim().toUpperCase();
  if (!ticker) {
    setStatus("Enter a ticker symbol (e.g., AAPL).");
    return;
  }

  setStatus("Running analysis… this may take a few seconds.");
  if (runBtn) {
    runBtn.disabled = true;
    runBtn.dataset.prevText = runBtn.textContent;
    runBtn.textContent = "Analyzing…";
  }

  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker })
    });

    const data = await res.json();

    if (!res.ok) {
      setStatus(`Error ${res.status}: ${data?.detail ?? "Unknown error"}`);
      return;
    }

    // Always pull these from backend payload (correct keys!)
    const tech = data.technical_indicators || {};
    const riskm = data.risk_metrics || {};

    // Top-level
    if ($("tickerChip")) $("tickerChip").textContent = data.ticker ?? ticker;
    if ($("analysisDate")) $("analysisDate").textContent = data.analysis_date ?? "—";

    // Recommendation section (backend if available, else derived)
    const pkg = pickRecommendationPackage(data, tech, riskm);

    setBadge(pkg.recommendation);
    if ($("riskLevel")) $("riskLevel").textContent = pkg.riskLevel ?? "—";
    if ($("reasoning")) $("reasoning").textContent = pkg.reasoning ?? "—";

    const driversEl = $("drivers");
    if (driversEl) {
      const list = Array.isArray(pkg.drivers) ? pkg.drivers : [];
      driversEl.innerHTML = list.map(d => `<li>${d}</li>`).join("") || "<li>—</li>";
    }

    // Pills
    if ($("trendPill")) $("trendPill").textContent = `Trend: ${tech.trend ?? "—"}`;
    if ($("riskPill")) $("riskPill").textContent = `Risk: ${pkg.riskLevel ?? "—"}`;
    if ($("recPill")) $("recPill").textContent = `Rec: ${pkg.recommendation ?? "—"}`;

    // Metrics tiles
    if ($("price")) $("price").textContent = fmtNum(tech.current_price);
    if ($("rsi")) $("rsi").textContent = fmtNum(tech.rsi_14);
    if ($("trend")) $("trend").textContent = tech.trend ?? "—";
    if ($("vol")) $("vol").textContent = fmtNum(riskm.volatility);
    if ($("sharpe")) $("sharpe").textContent = fmtNum(riskm.sharpe_ratio);
    if ($("cdd")) $("cdd").textContent = fmtPct(riskm.current_drawdown);

    // RSI Gauge
    const rsi = Number(tech.rsi_14);
    setRsiGauge(Number.isFinite(rsi) ? rsi : NaN);

    // Snapshot chart
    const snap = [
      Number(tech.rsi_14 ?? 0),
      Number(tech.macd_line ?? 0),
      Number(tech.signal_line ?? 0),
      Number(riskm.volatility ?? 0) * 100,
      Number(riskm.sharpe_ratio ?? 0) * 10,
      Math.abs(Number(riskm.current_drawdown ?? 0)) * 100
    ];

    const c = ensureChart();
    if (c) {
      c.data.datasets[0].data = snap.map(v => (Number.isFinite(v) ? v : 0));
      c.update();
    }

    // Raw JSON
    if ($("rawJson")) $("rawJson").textContent = JSON.stringify(data, null, 2);

    setStatus("Done.");
  } catch (e) {
    console.error(e);
    setStatus("Request failed. Check the server console for errors.");
  } finally {
    if (runBtn) {
      runBtn.disabled = false;
      runBtn.textContent = runBtn.dataset.prevText || "Analyze";
    }
  }
}

// ---------------------
// Events
// ---------------------
$("run")?.addEventListener("click", analyze);

$("ticker")?.addEventListener("keydown", (e) => {
  if (e.key === "Enter") analyze();
});

$("copyJson")?.addEventListener("click", async () => {
  const raw = $("rawJson");
  const txt = raw ? raw.textContent : "";
  try {
    await navigator.clipboard.writeText(txt);
    setStatus("Copied JSON to clipboard.");
    setTimeout(() => setStatus(""), 1200);
  } catch {
    setStatus("Copy failed (browser permissions).");
  }
});
