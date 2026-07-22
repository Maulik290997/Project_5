const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const ROOT = path.resolve(__dirname, "..");
const FIG = path.join(ROOT, "figures");
const summary = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "report_summary.json")));

// ---- Palette: Midnight Executive ----
const NAVY = "1E2761";
const ICE = "CADCFC";
const WHITE = "FFFFFF";
const AMBER = "D9A441";
const DARKTEXT = "1B1B2A";
const MUTED = "5A6B8C";

const pres = new pptxgen();
pres.defineLayout({ name: "WIDE", width: 13.333, height: 7.5 });
pres.layout = "WIDE";

const FONT_HEAD = "Cambria";
const FONT_BODY = "Calibri";

function imgPath(name) { return path.join(FIG, name); }

function darkSlide() {
  const s = pres.addSlide();
  s.background = { color: NAVY };
  return s;
}
function lightSlide() {
  const s = pres.addSlide();
  s.background = { color: WHITE };
  return s;
}

function title(s, text, opts = {}) {
  s.addText(text, {
    x: 0.6, y: 0.4, w: 12.1, h: opts.h || 0.9,
    fontFace: FONT_HEAD, fontSize: opts.size || 30, bold: true,
    color: opts.color || NAVY, align: "left", margin: 0,
  });
}
function kicker(s, text, color = AMBER) {
  s.addText(text.toUpperCase(), {
    x: 0.6, y: 0.15, w: 10, h: 0.35, fontFace: FONT_BODY, fontSize: 13,
    bold: true, color, charSpacing: 2, margin: 0,
  });
}
function pageNum(s, n) {
  s.addText(String(n), {
    x: 12.7, y: 7.08, w: 0.5, h: 0.3, fontFace: FONT_BODY, fontSize: 10,
    color: MUTED, align: "right", margin: 0,
  });
}
function footerNote(s, text) {
  s.addText(text, {
    x: 0.6, y: 7.08, w: 10, h: 0.3, fontFace: FONT_BODY, fontSize: 10,
    italic: true, color: MUTED, margin: 0,
  });
}
function bulletsBox(s, items, opts = {}) {
  const paras = items.map((it, i) => ({
    text: it, options: {
      bullet: { code: "25CF", indent: 18 }, breakLine: i < items.length - 1,
      fontSize: opts.size || 15, color: opts.color || DARKTEXT, fontFace: FONT_BODY,
      paraSpaceAfter: 10,
    },
  }));
  s.addText(paras, { x: opts.x, y: opts.y, w: opts.w, h: opts.h, valign: "top", margin: 0 });
}
function statCallout(s, x, y, w, h, num, label, opts = {}) {
  s.addText(num, {
    x, y, w, h: h * 0.62, fontFace: FONT_HEAD, fontSize: opts.numSize || 34, bold: true,
    color: opts.numColor || AMBER, align: "left", margin: 0, valign: "bottom",
  });
  s.addText(label, {
    x, y: y + h * 0.62, w, h: h * 0.38, fontFace: FONT_BODY, fontSize: 12,
    color: opts.labelColor || WHITE, align: "left", margin: 0, valign: "top",
  });
}
function fitImage(name, maxW, maxH) {
  const { execSync } = require("child_process");
  // aspect ratios precomputed (w/h) from PIL inspection
  const ratios = {
    "bivariate_app_vs_total.png": 1.167, "correlation_heatmap.png": 1.333,
    "decile_segmentation.png": 1.8, "engagement_cluster_averages.png": 3.0,
    "engagement_clusters_scatter.png": 1.333, "engagement_elbow.png": 1.4,
    "experience_cluster_averages.png": 3.0, "experience_clusters_scatter.png": 1.333,
    "pca_scree.png": 1.4, "satisfaction_cluster_avg.png": 1.4,
    "satisfaction_clusters.png": 1.333, "satisfaction_distribution.png": 1.6,
    "tcp_retrans_by_handset.png": 1.25, "throughput_by_handset.png": 1.25,
    "top10_handsets.png": 1.8, "top10_satisfied.png": 1.8, "top3_applications.png": 1.4,
    "top3_manufacturers.png": 1.2, "top5_handsets_per_manufacturer.png": 3.2,
    "univariate_analysis.png": 0.6,
  };
  const r = ratios[name];
  let w = maxW, h = w / r;
  if (h > maxH) { h = maxH; w = h * r; }
  return { w, h };
}
function addFig(s, name, x, y, maxW, maxH) {
  const { w, h } = fitImage(name, maxW, maxH);
  s.addImage({ path: imgPath(name), x: x + (maxW - w) / 2, y: y + (maxH - h) / 2, w, h });
}
function card(s, x, y, w, h, color = ICE) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.08, fill: { color }, line: { type: "none" } });
}
function circleNum(s, x, y, d, num, color = AMBER) {
  s.addShape(pres.ShapeType.ellipse, { x, y, w: d, h: d, fill: { color }, line: { type: "none" } });
  s.addText(String(num), {
    x, y, w: d, h: d, align: "center", valign: "middle", fontFace: FONT_HEAD,
    bold: true, fontSize: 20, color: NAVY, margin: 0,
  });
}

let slideNum = 0;
function track(s) { slideNum += 1; pageNum(s, slideNum); return s; }

// ============ SLIDE 1: TITLE ============
{
  const s = darkSlide();
  s.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 7.5, fill: { color: NAVY }, line: { type: "none" } });
  s.addText("TELLCO TELECOM", {
    x: 0.9, y: 2.35, w: 11, h: 0.5, fontFace: FONT_BODY, fontSize: 16, bold: true,
    color: AMBER, charSpacing: 3, margin: 0,
  });
  s.addText("Acquisition Due Diligence", {
    x: 0.85, y: 2.75, w: 11.5, h: 1.3, fontFace: FONT_HEAD, fontSize: 46, bold: true,
    color: WHITE, margin: 0,
  });
  s.addText("A data-driven view of user overview, engagement, network experience, and satisfaction", {
    x: 0.9, y: 4.05, w: 10.8, h: 0.7, fontFace: FONT_BODY, fontSize: 18, italic: true,
    color: ICE, margin: 0,
  });
  s.addText("Prepared for the Investor Due-Diligence Team  |  Nexthikes IT Solutions  |  Republic of Pefkakia", {
    x: 0.9, y: 6.55, w: 11, h: 0.4, fontFace: FONT_BODY, fontSize: 13, color: MUTED === NAVY ? WHITE : "8C9BC9", margin: 0,
  });
  track(s);
}

// ============ SLIDE 2: SITUATIONAL OVERVIEW ============
{
  const s = lightSlide();
  kicker(s, "Business Context");
  title(s, "Why This Analysis Matters");
  s.addText(
    "Our investor specializes in acquiring undervalued assets and driving profitability by refocusing the business on its most valuable customers and products. TellCo's current owners have shared financial data but have never analyzed their own system-generated network data.",
    { x: 0.6, y: 1.5, w: 7.0, h: 2.0, fontFace: FONT_BODY, fontSize: 16, color: DARKTEXT, margin: 0, valign: "top" }
  );
  bulletsBox(s, [
    "One month of xDR (session-level) network data analyzed",
    `${summary.n_users.toLocaleString()} unique subscribers, 150,001 sessions`,
    "Four analysis stages: Overview, Engagement, Experience, Satisfaction",
    "Goal: identify growth levers and a buy/sell recommendation",
  ], { x: 0.6, y: 3.7, w: 7.0, h: 2.6, size: 15 });

  card(s, 8.0, 1.5, 4.7, 5.2, ICE);
  s.addText("Precedent", {
    x: 8.35, y: 1.75, w: 4.0, h: 0.4, fontFace: FONT_HEAD, fontSize: 16, bold: true, color: NAVY, margin: 0,
  });
  s.addText(
    "On a prior engagement, this same investor used rich data analysis to identify that university-student delivery routes were the most profitable segment for a delivery company -- driving a 25% profit increase in 6 months after acquisition. The same rigor is applied here to TellCo.",
    { x: 8.35, y: 2.25, w: 4.0, h: 3.0, fontFace: FONT_BODY, fontSize: 14, color: DARKTEXT, margin: 0, valign: "top" }
  );
  track(s);
}

// ============ SLIDE 3: EXECUTIVE SUMMARY ============
{
  const s = darkSlide();
  kicker(s, "Executive Summary");
  title(s, "Conditional Buy", { color: WHITE, size: 40 });
  s.addText(
    "A large, actively engaged, premium-skewed subscriber base with clear monetization levers -- offset by network telemetry gaps and quality issues a buyer should price in.",
    { x: 0.6, y: 1.35, w: 11.8, h: 0.8, fontFace: FONT_BODY, fontSize: 17, italic: true, color: ICE, margin: 0 }
  );

  const stats = [
    [summary.n_users.toLocaleString(), "Unique subscribers"],
    ["150,001", "xDR sessions analyzed"],
    [`${summary.app_totals_overall_fmt.Gaming}`, "Gaming data volume (top app)"],
    [`${(summary.regression_r2*100).toFixed(0)}%`, "Satisfaction variance explained by usage"],
  ];
  const cardW = 2.85, gap = 0.25, startX = 0.6, y0 = 2.55;
  stats.forEach((st, i) => {
    const x = startX + i * (cardW + gap);
    s.addShape(pres.ShapeType.roundRect, { x, y: y0, w: cardW, h: 1.7, rectRadius: 0.08, fill: { color: "273580" }, line: { type: "none" } });
    statCallout(s, x + 0.2, y0 + 0.15, cardW - 0.4, 1.4, st[0], st[1]);
  });

  bulletsBox(s, [
    "Premium device base (Apple/Samsung/Huawei) signals real spending power",
    "Distinct fixed-wireless broadband segment (Huawei router users) is underexploited",
    "Network quality varies materially by handset -- remediation opportunity",
    "Recommend a price adjustment or escrow for network-infrastructure investment",
  ], { x: 0.6, y: 4.7, w: 11.8, h: 2.2, size: 15, color: WHITE });
  track(s);
}

// ============ SLIDE 4: METHODOLOGY ============
{
  const s = lightSlide();
  kicker(s, "Approach");
  title(s, "Methodology & Data Notes");
  const steps = [
    ["1", "Clean", "Missing values imputed with column mean/mode; extreme outliers capped at 3x IQR"],
    ["2", "Aggregate", "Session-level xDR rows rolled up to per-subscriber (MSISDN) features"],
    ["3", "Model", "K-Means clustering, PCA, and linear regression applied to engagement & experience metrics"],
    ["4", "Score", "Engagement + experience distances combined into a satisfaction score per subscriber"],
  ];
  const w = 2.85, gap = 0.25, x0 = 0.6, y0 = 1.7;
  steps.forEach((st, i) => {
    const x = x0 + i * (w + gap);
    card(s, x, y0, w, 4.6, ICE);
    circleNum(s, x + 0.25, y0 + 0.3, 0.6, st[0]);
    s.addText(st[1], { x: x + 0.25, y: y0 + 1.1, w: w - 0.5, h: 0.5, fontFace: FONT_HEAD, fontSize: 18, bold: true, color: NAVY, margin: 0 });
    s.addText(st[2], { x: x + 0.25, y: y0 + 1.65, w: w - 0.5, h: 2.7, fontFace: FONT_BODY, fontSize: 13, color: DARKTEXT, margin: 0, valign: "top" });
  });
  footerNote(s, "Modeling used a dependency-free numpy toolkit (scikit-learn-API-compatible); see code repository README.");
  track(s);
}

// ============ SLIDE 5: HANDSET & MANUFACTURER LANDSCAPE ============
{
  const s = lightSlide();
  kicker(s, "Task 1 - User Overview");
  title(s, "Handset & Manufacturer Landscape");
  addFig(s, "top10_handsets.png", 0.6, 1.55, 7.0, 5.3);
  card(s, 7.9, 1.55, 4.85, 5.3, ICE);
  s.addText("Top 3 Manufacturers", { x: 8.2, y: 1.8, w: 4.2, h: 0.4, fontFace: FONT_HEAD, fontSize: 16, bold: true, color: NAVY, margin: 0 });
  Object.entries(summary.top_3_manufacturers).forEach(([k, v], i) => {
    statCallout(s, 8.2, 2.35 + i * 1.4, 4.2, 1.2, v.toLocaleString(), k, { numColor: NAVY, labelColor: DARKTEXT, numSize: 26 });
  });
  track(s);
}

// ============ SLIDE 6: TOP HANDSETS PER MANUFACTURER ============
{
  const s = lightSlide();
  kicker(s, "Task 1 - User Overview");
  title(s, "Top 5 Handsets per Top-3 Manufacturer");
  addFig(s, "top5_handsets_per_manufacturer.png", 0.6, 1.6, 12.1, 4.3);
  s.addText(
    "The Huawei B528S-23A -- a fixed-wireless/home-broadband router, not a phone -- is TellCo's single most common device, pointing to a meaningful home-broadband customer segment alongside mobile handsets.",
    { x: 0.6, y: 6.1, w: 12.1, h: 0.9, fontFace: FONT_BODY, fontSize: 15, italic: true, color: DARKTEXT, margin: 0 }
  );
  track(s);
}

// ============ SLIDE 7: CORRELATION & PCA ============
{
  const s = lightSlide();
  kicker(s, "Task 1 - User Overview");
  title(s, "Application Usage: Correlation & PCA");
  addFig(s, "correlation_heatmap.png", 0.6, 1.6, 5.7, 5.2);
  addFig(s, "pca_scree.png", 6.6, 1.6, 5.5, 4.0);
  bulletsBox(s, [
    "Application categories are essentially uncorrelated -- usage of one app tells you little about another",
    "PCA variance is spread evenly (~14% per component) -- no single 'heavy user' axis",
    "Total data volume is driven almost entirely by Gaming (r=0.998)",
  ], { x: 6.6, y: 5.65, w: 5.9, h: 1.6, size: 13 });
  track(s);
}

// ============ SLIDE 8: DECILE SEGMENTATION ============
{
  const s = lightSlide();
  kicker(s, "Task 1 - User Overview");
  title(s, "Data Volume by Session-Duration Decile");
  addFig(s, "decile_segmentation.png", 0.6, 1.6, 7.3, 5.2);
  card(s, 8.1, 1.6, 4.65, 5.2, ICE);
  s.addText("Top decile alone accounts for", { x: 8.4, y: 2.0, w: 4.0, h: 0.4, fontFace: FONT_BODY, fontSize: 14, color: DARKTEXT, margin: 0 });
  statCallout(s, 8.4, 2.35, 4.0, 1.5, summary.decile_totals_fmt["9"], "of total network data volume", { numColor: NAVY, labelColor: DARKTEXT, numSize: 36 });
  s.addText(
    "Long-session users are disproportionately valuable data consumers -- more than double the 6th decile's volume. These subscribers are prime candidates for premium/unlimited plan upsell.",
    { x: 8.4, y: 4.1, w: 4.0, h: 2.5, fontFace: FONT_BODY, fontSize: 13, color: DARKTEXT, margin: 0, valign: "top" }
  );
  track(s);
}

// ============ SLIDE 9: ENGAGEMENT METRICS ============
{
  const s = lightSlide();
  kicker(s, "Task 2 - User Engagement");
  title(s, "Engagement Metrics & Top Customers");
  s.addText(
    "Engagement was measured per subscriber via three metrics: session frequency, total session duration, and total session traffic (DL+UL bytes).",
    { x: 0.6, y: 1.55, w: 11.9, h: 0.7, fontFace: FONT_BODY, fontSize: 15, color: DARKTEXT, margin: 0 }
  );
  addFig(s, "engagement_cluster_averages.png", 0.6, 2.9, 5.7, 2.6);
  s.addText(
    "Cluster 2 (the single outlier) dwarfs the scale of clusters 0-1, visually flattening them -- see Slide 10 for the full 3-cluster breakdown.",
    { x: 0.6, y: 5.7, w: 5.7, h: 1.0, fontFace: FONT_BODY, fontSize: 13, italic: true, color: MUTED, margin: 0, valign: "top" }
  );
  card(s, 6.6, 2.5, 5.9, 4.3, ICE);
  s.addText("What drives engagement", { x: 6.9, y: 2.75, w: 5.3, h: 0.4, fontFace: FONT_HEAD, fontSize: 16, bold: true, color: NAVY, margin: 0 });
  bulletsBox(s, [
    "One subscriber logged 1,066 sessions in the month vs. a median of ~1 -- an extreme statistical outlier (likely M2M/aggregator line)",
    "Excluding that outlier, the next-heaviest users show 12-18 sessions -- a natural 'power user' tier",
    "Gaming and unclassified 'Other' traffic dominate total bytes network-wide",
  ], { x: 6.9, y: 3.25, w: 5.3, h: 3.4, size: 14, color: DARKTEXT });
  track(s);
}

// ============ SLIDE 10: ENGAGEMENT CLUSTERS ============
{
  const s = lightSlide();
  kicker(s, "Task 2 - User Engagement");
  title(s, "Engagement Segmentation (K-Means, k=3)");
  addFig(s, "engagement_elbow.png", 0.6, 1.6, 5.7, 4.6);
  addFig(s, "engagement_clusters_scatter.png", 6.6, 1.6, 5.9, 4.6);
  s.addText(
    "The elbow method supports k=3: additional clusters yield diminishing returns. One cluster is a single extreme outlier that heavily skews centroid placement -- flagged as a data-quality limitation.",
    { x: 0.6, y: 6.3, w: 11.9, h: 0.8, fontFace: FONT_BODY, fontSize: 14, italic: true, color: DARKTEXT, margin: 0 }
  );
  track(s);
}

// ============ SLIDE 11: TOP APPLICATIONS ============
{
  const s = lightSlide();
  kicker(s, "Task 2 - User Engagement");
  title(s, "Most-Used Applications, Network-Wide");
  addFig(s, "top3_applications.png", 0.6, 1.6, 6.5, 5.2);
  card(s, 7.5, 1.6, 5.25, 5.2, ICE);
  const apps = [["Gaming", summary.app_totals_overall_fmt.Gaming], ["Other", summary.app_totals_overall_fmt.Other], ["YouTube", summary.app_totals_overall_fmt.Youtube]];
  apps.forEach((a, i) => {
    statCallout(s, 7.8, 1.9 + i * 1.6, 4.7, 1.4, a[1], a[0] + " total volume", { numColor: NAVY, labelColor: DARKTEXT, numSize: 28 });
  });
  track(s);
}

// ============ SLIDE 12: THROUGHPUT BY HANDSET ============
{
  const s = lightSlide();
  kicker(s, "Task 3 - User Experience");
  title(s, "Average Throughput by Handset Type");
  addFig(s, "throughput_by_handset.png", 0.6, 1.55, 12.1, 5.3);
  footerNote(s, "Top 15 handsets by session volume. Spread within a single model suggests real network/coverage variance, not just device capability.");
  track(s);
}

// ============ SLIDE 13: TCP RETRANSMISSION & EXPERIENCE CLUSTERS ============
{
  const s = lightSlide();
  kicker(s, "Task 3 - User Experience");
  title(s, "Network Quality: Retransmission & Experience Clusters");
  addFig(s, "tcp_retrans_by_handset.png", 0.6, 1.6, 6.3, 5.2);
  addFig(s, "experience_clusters_scatter.png", 7.1, 1.6, 5.6, 4.4);
  s.addText(
    "Three clean experience clusters emerge: good (low RTT/retrans, high throughput), moderate, and poor. The poor-experience cluster anchors the Task 4 satisfaction scoring.",
    { x: 7.1, y: 6.1, w: 5.6, h: 1.1, fontFace: FONT_BODY, fontSize: 13, italic: true, color: DARKTEXT, margin: 0 }
  );
  track(s);
}

// ============ SLIDE 14: SATISFACTION METHODOLOGY ============
{
  const s = darkSlide();
  kicker(s, "Task 4 - Satisfaction");
  title(s, "Scoring Customer Satisfaction", { color: WHITE });
  const steps = [
    ["Engagement score", "Distance from each user to the LEAST-engaged cluster centroid"],
    ["Experience score", "Distance from each user to the WORST-experience cluster centroid"],
    ["Satisfaction score", "Average of engagement score and experience score"],
  ];
  const w = 3.85, gap = 0.3, x0 = 0.6, y0 = 2.0;
  steps.forEach((st, i) => {
    const x = x0 + i * (w + gap);
    s.addShape(pres.ShapeType.roundRect, { x, y: y0, w, h: 3.6, rectRadius: 0.08, fill: { color: "273580" }, line: { type: "none" } });
    circleNum(s, x + 0.3, y0 + 0.3, 0.55, i + 1);
    s.addText(st[0], { x: x + 0.3, y: y0 + 1.1, w: w - 0.6, h: 0.6, fontFace: FONT_HEAD, fontSize: 18, bold: true, color: WHITE, margin: 0 });
    s.addText(st[1], { x: x + 0.3, y: y0 + 1.75, w: w - 0.6, h: 1.7, fontFace: FONT_BODY, fontSize: 14, color: ICE, margin: 0, valign: "top" });
  });
  footerNote(s, "Higher score = farther from the 'bad' reference cluster = more engaged / better experience / more satisfied.");
  track(s);
}

// ============ SLIDE 15: TOP SATISFIED + REGRESSION ============
{
  const s = lightSlide();
  kicker(s, "Task 4 - Satisfaction");
  title(s, "Top Satisfied Customers & What Drives Satisfaction");
  addFig(s, "top10_satisfied.png", 0.6, 1.6, 6.3, 5.2);
  card(s, 7.1, 1.6, 5.6, 5.2, ICE);
  s.addText(`Regression R² = ${summary.regression_r2}`, { x: 7.4, y: 1.85, w: 5.0, h: 0.5, fontFace: FONT_HEAD, fontSize: 18, bold: true, color: NAVY, margin: 0 });
  const coefs = Object.entries(summary.regression_coefficients).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));
  const rows = [[{ text: "Feature", options: { bold: true, fill: { color: NAVY }, color: WHITE, fontSize: 12 } }, { text: "Coefficient", options: { bold: true, fill: { color: NAVY }, color: WHITE, fontSize: 12 } }]];
  coefs.forEach(([k, v]) => rows.push([{ text: k, options: { fontSize: 12, color: DARKTEXT } }, { text: String(v), options: { fontSize: 12, color: DARKTEXT } }]));
  s.addTable(rows, {
    x: 7.4, y: 2.5, w: 5.0, colW: [3.4, 1.6],
    border: { type: "solid", color: "FFFFFF", pt: 1 },
    autoPage: false,
  });
  s.addText("Session frequency and duration are the strongest positive drivers of satisfaction.", { x: 7.4, y: 6.0, w: 5.0, h: 0.7, fontFace: FONT_BODY, fontSize: 12, italic: true, color: DARKTEXT, margin: 0 });
  track(s);
}

// ============ SLIDE 16: SATISFACTION CLUSTERS ============
{
  const s = lightSlide();
  kicker(s, "Task 4 - Satisfaction");
  title(s, "Satisfaction Clusters (k=2)");
  addFig(s, "satisfaction_clusters.png", 0.6, 1.6, 7.3, 5.2);
  card(s, 8.1, 1.6, 4.65, 5.2, ICE);
  const csea = summary.cluster_satisfaction_experience_avg;
  Object.entries(csea).forEach(([k, v], i) => {
    s.addText(`Cluster ${k}`, { x: 8.4, y: 1.9 + i * 2.5, w: 4.0, h: 0.4, fontFace: FONT_HEAD, fontSize: 15, bold: true, color: NAVY, margin: 0 });
    s.addText(`Avg satisfaction: ${v.satisfaction_score}\nAvg experience: ${v.experience_score}\nAvg engagement: ${v.engagement_score}`,
      { x: 8.4, y: 2.3 + i * 2.5, w: 4.0, h: 1.3, fontFace: FONT_BODY, fontSize: 13, color: DARKTEXT, margin: 0, valign: "top" });
  });
  track(s);
}

// ============ SLIDE 17: MLOPS ============
{
  const s = lightSlide();
  kicker(s, "Deployment");
  title(s, "MLOps: Model Deployment & Tracking");
  const items = [
    ["Versioned runs", "Each training run logs code version, start/end time, and parameters"],
    ["Tracked metrics", "Train/test R² and RMSE recorded per run in model_tracking_log.csv"],
    ["Artifacts saved", "Coefficients and full run records archived to reports/model_runs/"],
    ["Database export", "Final scored table (engagement, experience, satisfaction) exported for SQL access"],
  ];
  const w = 2.85, gap = 0.25, x0 = 0.6, y0 = 1.8;
  items.forEach((it, i) => {
    const x = x0 + i * (w + gap);
    card(s, x, y0, w, 4.6, ICE);
    circleNum(s, x + 0.25, y0 + 0.3, 0.55, i + 1);
    s.addText(it[0], { x: x + 0.25, y: y0 + 1.05, w: w - 0.5, h: 0.6, fontFace: FONT_HEAD, fontSize: 16, bold: true, color: NAVY, margin: 0 });
    s.addText(it[1], { x: x + 0.25, y: y0 + 1.65, w: w - 0.5, h: 2.7, fontFace: FONT_BODY, fontSize: 13, color: DARKTEXT, margin: 0, valign: "top" });
  });
  track(s);
}

// ============ SLIDE 18: LIMITATIONS ============
{
  const s = darkSlide();
  kicker(s, "Caveats");
  title(s, "Analysis Limitations", { color: WHITE });
  bulletsBox(s, [
    "Single-month snapshot -- trend, seasonality, and churn cannot be assessed",
    "55-87% missingness in key network-quality columns (TCP retransmission, HTTP bytes), imputed per brief",
    "One extreme outlier subscriber dominates engagement/satisfaction clustering and rankings",
    "No revenue or pricing data provided -- engagement/experience used as value proxies, not profitability",
    "Custom numpy modeling toolkit used (no scikit-learn/scipy in this environment) -- unit-tested but not cross-validated against scikit-learn",
    "Database export used SQLite as a stand-in for MySQL (no local MySQL server available)",
  ], { x: 0.6, y: 1.7, w: 11.9, h: 5.2, size: 16, color: WHITE });
  track(s);
}

// ============ SLIDE 19: RECOMMENDATION ============
{
  const s = darkSlide();
  kicker(s, "Recommendation");
  title(s, "Buy, With Conditions", { color: WHITE });
  bulletsBox(s, [
    "Positive: large, engaged subscriber base with a premium device mix and an underexploited fixed-wireless broadband segment",
    "Risk: immature network telemetry and measurable per-handset quality variance should be priced into the deal",
    "Recommended next step: negotiate a network-infrastructure remediation allowance into the purchase price",
    "Recommended next step: commission a multi-month follow-up analysis to confirm trends before final close",
  ], { x: 0.6, y: 1.7, w: 11.9, h: 4.0, size: 17, color: WHITE });
  card(s, 0.6, 5.85, 11.9, 1.1, "273580");
  s.addText("Bottom line: the data supports proceeding with the acquisition, conditioned on a network-quality remediation plan.", {
    x: 0.9, y: 5.85, w: 11.3, h: 1.1, fontFace: FONT_HEAD, fontSize: 16, bold: true, color: AMBER, valign: "middle", margin: 0,
  });
  track(s);
}

// ============ SLIDE 20: REFERENCES ============
{
  const s = lightSlide();
  kicker(s, "Appendix");
  title(s, "References");
  bulletsBox(s, [
    "TellCo xDR session-level export (source dataset), Nexthikes IT Solutions",
    "Field Descriptions.xlsx -- field dictionary accompanying the source dataset",
    "Project code repository: tellco-analysis/ (src/tellco package, scripts/, tests/, dashboard/app.py)",
    "Full written report: TellCo_Investor_Report.docx",
    "Interactive dashboard: dashboard/app.py (Streamlit)",
  ], { x: 0.6, y: 1.7, w: 11.9, h: 3.5, size: 16 });
  track(s);
}

pres.writeFile({ fileName: path.join(ROOT, "reports", "TellCo_Investor_Deck.pptx") }).then(fileName => {
  console.log("WROTE", fileName);
});
