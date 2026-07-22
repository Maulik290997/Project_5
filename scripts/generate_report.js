const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, ImageRun,
  Table, TableRow, TableCell, WidthType, ShadingType, AlignmentType,
  BorderStyle, PageBreak, PageOrientation,
} = require("docx");

const ROOT = path.resolve(__dirname, "..");
const FIG = path.join(ROOT, "figures");
const summary = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "report_summary.json")));

function img(name, width = 560) {
  const filePath = path.join(FIG, name);
  const buf = fs.readFileSync(filePath);
  return new ImageRun({ data: buf, type: "png", transformation: { width, height: Math.round(width * 0.68) } });
}

function h(text, level = HeadingLevel.HEADING_1) {
  return new Paragraph({ text, heading: level, spacing: { before: 240, after: 120 } });
}
function p(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 120 } });
}
function bullet(text) {
  return new Paragraph({ text, bullet: { level: 0 }, spacing: { after: 80 } });
}
function figure(name, caption, width = 520) {
  return [
    new Paragraph({ children: [img(name, width)], alignment: AlignmentType.CENTER, spacing: { before: 120, after: 80 } }),
    new Paragraph({
      children: [new TextRun({ text: caption, italics: true, size: 18 })],
      alignment: AlignmentType.CENTER, spacing: { after: 200 },
    }),
  ];
}

function cell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.width || 2000, type: WidthType.DXA },
    shading: opts.header ? { type: ShadingType.CLEAR, fill: "1F4E5F" } : undefined,
    children: [new Paragraph({
      children: [new TextRun({ text: String(text), bold: !!opts.header, color: opts.header ? "FFFFFF" : "000000", size: 20 })],
    })],
  });
}

function simpleTable(headers, rows, widths) {
  const w = widths || headers.map(() => Math.floor(9000 / headers.length));
  return new Table({
    columnWidths: w,
    width: { size: 9000, type: WidthType.DXA },
    rows: [
      new TableRow({ children: headers.map((hd, i) => cell(hd, { header: true, width: w[i] })) }),
      ...rows.map(r => new TableRow({ children: r.map((c, i) => cell(c, { width: w[i] })) })),
    ],
  });
}

const children = [];

// ---------------- TITLE PAGE ----------------
children.push(
  new Paragraph({ text: "", spacing: { before: 2000 } }),
  new Paragraph({
    children: [new TextRun({ text: "TellCo Telecom Acquisition Due Diligence", bold: true, size: 56 })],
    alignment: AlignmentType.CENTER, spacing: { after: 200 },
  }),
  new Paragraph({
    children: [new TextRun({ text: "User Analytics: Overview, Engagement, Experience & Satisfaction", size: 30, color: "44546A" })],
    alignment: AlignmentType.CENTER, spacing: { after: 600 },
  }),
  new Paragraph({
    children: [new TextRun({ text: "Prepared for the Investor Due-Diligence Team", size: 24 })],
    alignment: AlignmentType.CENTER, spacing: { after: 120 },
  }),
  new Paragraph({
    children: [new TextRun({ text: "Nexthikes IT Solutions - TellCo, Republic of Pefkakia", size: 22, italics: true })],
    alignment: AlignmentType.CENTER, spacing: { after: 800 },
  }),
  new Paragraph({ children: [new PageBreak()] }),
);

// ---------------- EXECUTIVE SUMMARY ----------------
children.push(h("Executive Summary"));
children.push(p(
  `This report analyzes one month of xDR (session-level) network data from TellCo, covering ${summary.n_users.toLocaleString()} unique subscribers and 150,001 data sessions, to support an investment decision on acquiring the company. The analysis proceeds through four stages: a User Overview of the device base, User Engagement (session frequency, duration, and traffic), Network Experience (throughput, latency, retransmission by handset), and a derived Customer Satisfaction score combining engagement and experience.`
));
children.push(p(
  "Recommendation: Conditional Buy. TellCo has a large, actively engaged, and reasonably affluent subscriber base with clear, monetizable usage segments (heavy gaming/video users, a premium-device segment, and a fixed-wireless broadband cohort). However, the underlying network telemetry has substantial gaps and quality issues that a buyer should price into the deal or address post-acquisition. Full detail and caveats are below.",
  { bold: true }
));
children.push(p("Key findings:"));
children.push(bullet(`Apple, Samsung, and Huawei account for the top 3 handset manufacturers (${summary.top_3_manufacturers.Apple.toLocaleString()}, ${summary.top_3_manufacturers.Samsung.toLocaleString()}, and ${summary.top_3_manufacturers.Huawei.toLocaleString()} sessions respectively) -- a premium-skewed device base with real spending power.`));
children.push(bullet(`Gaming and unclassified "Other" traffic dominate total network bytes (${summary.app_totals_overall_fmt.Gaming} and ${summary.app_totals_overall_fmt.Other} respectively, vs. ${summary.app_totals_overall_fmt.Youtube} for YouTube) -- total data usage is almost entirely explained by gaming volume (r=${summary.bivariate_corr.Gaming}).`));
children.push(bullet("Engagement clustering (k=3) cleanly separates a small, extremely heavy-usage segment from the general subscriber base -- a natural target for premium/unlimited plans."));
children.push(bullet("Network experience (RTT, TCP retransmission, throughput) varies materially by handset type, pointing to device- or area-specific network quality issues worth remediating before/after acquisition."));
children.push(bullet(`A regression model explains ${(summary.regression_r2*100).toFixed(1)}% of the variance in the derived satisfaction score from engagement and experience features alone, confirming these are meaningful, actionable levers.`));

// ---------------- METHODOLOGY ----------------
children.push(h("Methodology & Data Notes"));
children.push(p("The raw export contains 55 columns and 150,001 xDR session rows. Missing values were imputed with the column mean (numeric) or mode (categorical) as specified in the brief; a small number of extreme outliers were capped at 3x the interquartile range. All modeling (PCA, K-Means, linear regression) was implemented with a lightweight numpy-based toolkit built for this project (API-compatible with scikit-learn) since this analysis environment had no external package access; see the accompanying code repository README for details and swap-in instructions for a standard scikit-learn environment."));

// ---------------- TASK 1 ----------------
children.push(h("Task 1: User Overview Analysis"));
children.push(p(`The dataset covers ${summary.n_users.toLocaleString()} unique subscribers (MSISDN) across 150,001 xDR sessions.`));
children.push(h("Top Handsets & Manufacturers", HeadingLevel.HEADING_2));
children.push(...figure("top10_handsets.png", "Figure 1.1 - Top 10 handsets by xDR session count."));
children.push(...figure("top3_manufacturers.png", "Figure 1.2 - Top 3 handset manufacturers by session count."));
children.push(...figure("top5_handsets_per_manufacturer.png", "Figure 1.3 - Top 5 handsets within each of the top 3 manufacturers."));
children.push(p("The single most common device is the Huawei B528S-23A -- a fixed-wireless/home-broadband router (CPE), not a handset. Its ~20,000 sessions indicate a meaningful home-broadband customer segment operating alongside the mobile handset base, worth analyzing and marketing to separately from mobile subscribers."));

children.push(h("Univariate & Bivariate Analysis", HeadingLevel.HEADING_2));
children.push(...figure("univariate_analysis.png", "Figure 1.4 - Distributions and boxplots of session duration, DL/UL volume, RTT, and throughput.", 480));
children.push(p("Session duration, RTT, and throughput are all right-skewed with heavy tails (confirmed by positive skewness/kurtosis in the underlying statistics), meaning a small number of very long or very slow sessions pull the mean well above the median -- medians are the more representative 'typical experience' figures."));
children.push(...figure("correlation_heatmap.png", "Figure 1.5 - Correlation matrix of per-application data volumes.", 420));
children.push(p("Application usage categories are essentially uncorrelated with each other (all pairwise correlations near 0) -- a user's Social Media usage tells you nothing about their Gaming or Netflix usage. This is echoed by the PCA below."));

children.push(h("Decile Segmentation & PCA", HeadingLevel.HEADING_2));
children.push(...figure("decile_segmentation.png", "Figure 1.6 - Total data volume for the top 5 session-duration deciles.", 420));
children.push(p(`Total data volume rises sharply with session-duration decile: the top decile alone accounts for ${summary.decile_totals_fmt["9"]} of data, more than double the 6th decile (${summary.decile_totals_fmt["6"]}) -- confirming that long-session users are disproportionately valuable data consumers.`));
children.push(...figure("pca_scree.png", `Figure 1.7 - PCA scree plot; each of the first 4 components explains ~${summary.pca_var_ratio[0]}% of variance.`, 420));
children.push(p("PCA interpretation (4 points max, per brief):"));
children.push(bullet("Explained variance is spread almost evenly across components (~14% each) rather than concentrated in one or two -- there is no single dominant 'heavy user' axis."));
children.push(bullet("This confirms the correlation-matrix finding: the 7 application categories are close to statistically independent dimensions of behavior."));
children.push(bullet("Practically, a single composite 'usage score' would lose most of the signal; segmentation and targeting should stay app-specific (e.g., gaming bundles, video bundles) rather than one universal tier."));
children.push(bullet("Dimensionality reduction offers limited compression benefit here -- nearly all 7 original dimensions are needed to retain the behavioral signal."));

// ---------------- TASK 2 ----------------
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h("Task 2: User Engagement Analysis"));
children.push(p("Engagement was measured via three metrics aggregated per subscriber: session frequency, total session duration, and total session traffic (DL+UL bytes)."));
children.push(...figure("engagement_elbow.png", "Figure 2.1 - Elbow method for choosing k. Inertia drops sharply through k=3 and levels off after.", 420));
children.push(p("The elbow method supports k=3 as a reasonable, assignment-specified choice: additional clusters beyond 3 yield diminishing reductions in within-cluster variance."));
children.push(...figure("engagement_clusters_scatter.png", "Figure 2.2 - Engagement clusters (k=3): duration vs. traffic.", 420));
children.push(p("One cluster consists of a single extreme outlier subscriber with 1,066 sessions in the period (vs. a median of ~1 for all other users) -- almost certainly a machine-to-machine (M2M) SIM, data-reseller line, or logging artifact rather than a typical retail customer. This single point heavily skews cluster centroids; see Limitations."));
children.push(...figure("top3_applications.png", "Figure 2.3 - Top 3 most-used applications network-wide.", 400));
children.push(p(`Gaming (${summary.app_totals_overall_fmt.Gaming}) and unclassified "Other" traffic (${summary.app_totals_overall_fmt.Other}) dominate total network bytes, dwarfing YouTube (${summary.app_totals_overall_fmt.Youtube}), Netflix (${summary.app_totals_overall_fmt.Netflix}), Google (${summary.app_totals_overall_fmt.Google}), Email (${summary.app_totals_overall_fmt.Email}), and Social Media (${summary.app_totals_overall_fmt["Social Media"]}).`));

// ---------------- TASK 3 ----------------
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h("Task 3: User Experience Analysis"));
children.push(p("Experience was measured via average TCP retransmission volume, average round-trip time (RTT), average throughput, and handset type, aggregated per subscriber."));
children.push(...figure("throughput_by_handset.png", "Figure 3.1 - Average throughput distribution by handset type (top 15 handsets by session volume).", 460));
children.push(p("Throughput varies substantially by handset, even among high-volume devices -- some of this reflects device radio capability (e.g., older vs. newer LTE chipsets), but the spread within a single handset model also suggests real network/coverage variance."));
children.push(...figure("tcp_retrans_by_handset.png", "Figure 3.2 - Average TCP retransmission volume by handset type (top 15 by session volume).", 460));
children.push(...figure("experience_clusters_scatter.png", "Figure 3.3 - Experience clusters (k=3): RTT vs. throughput.", 420));
children.push(p("The three experience clusters separate cleanly into a good-experience group (low RTT, high throughput, minimal retransmission), a moderate group, and a poor-experience group (elevated RTT and/or retransmission, low throughput) -- this poor-experience cluster is the one used as the 'worst experience' reference point for Task 4's satisfaction scoring."));

// ---------------- TASK 4 ----------------
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h("Task 4: Satisfaction Analysis"));
children.push(p("Engagement score = Euclidean distance (in normalized engagement-metric space) from each user to the least-engaged cluster centroid. Experience score = Euclidean distance (in normalized experience-metric space) from each user to the worst-experience cluster centroid. Satisfaction score = average of the two."));
children.push(...figure("satisfaction_distribution.png", "Figure 4.1 - Distribution of satisfaction scores (99.9th percentile trimmed for readability).", 420));
children.push(...figure("top10_satisfied.png", "Figure 4.2 - Top 10 most satisfied customers by satisfaction score.", 460));
children.push(p("As in Task 2, the single most 'satisfied' customer by this score is the extreme M2M-like outlier -- its satisfaction score of ~262 is roughly 20x the next-highest customer. Excluding it, the top-satisfied customers are drawn from genuinely high-engagement, good-experience subscribers, which is the intended signal."));

children.push(h("Regression Model", HeadingLevel.HEADING_2));
children.push(p(`A linear regression predicting satisfaction score from the 6 underlying engagement and experience features achieves R² = ${summary.regression_r2} (in-sample; a held-out 80/20 split in the accompanying model-tracking log shows R² ≈ 0.85, confirming the relationship generalizes and is not solely driven by the one outlier).`));
children.push(simpleTable(
  ["Feature", "Standardized coefficient"],
  Object.entries(summary.regression_coefficients).map(([k, v]) => [k, v]),
  [6000, 3000]
));
children.push(p("Session frequency and total duration are the strongest positive drivers of satisfaction, followed by throughput -- reinforcing that keeping subscribers actively engaged with a fast network is the clearest lever on satisfaction.", { italics: true, size: 20 }));

children.push(h("Satisfaction Clusters (k=2)", HeadingLevel.HEADING_2));
children.push(...figure("satisfaction_clusters.png", "Figure 4.3 - Satisfaction clusters (k=2): engagement vs. experience score (log scale on x-axis due to the outlier).", 460));
const csea = summary.cluster_satisfaction_experience_avg;
children.push(simpleTable(
  ["Cluster", "Avg satisfaction", "Avg experience", "Avg engagement"],
  Object.entries(csea).map(([k, v]) => [k, v.satisfaction_score, v.experience_score, v.engagement_score]),
  [2000, 2500, 2500, 2500]
));
children.push(p("Cluster 0 (106,856 subscribers) represents the general population; Cluster 1 is the single outlier described above. In a production deployment this outlier should be filtered or handled as its own segment before re-running k=2 to get a meaningful second population cluster."));

children.push(h("MLOps: Model Deployment & Tracking", HeadingLevel.HEADING_2));
children.push(p("Each model-training run is logged (code version, start/end time, parameters, train/test R² and RMSE, and a coefficients artifact) to reports/model_tracking_log.csv and reports/model_runs/, providing an auditable history of model versions as required for MLOps governance. The final scored table (user ID, engagement score, experience score, satisfaction score, cluster) is exported to a local database (data/tellco_satisfaction.db) queryable via standard SQL; see the code repository for the exact schema and export script."));

// ---------------- LIMITATIONS ----------------
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(h("Limitations"));
children.push(bullet("Single-month snapshot: the data covers roughly one month, so trend, seasonality, and churn cannot be assessed -- all findings describe a point-in-time cross-section, not growth trajectory."));
children.push(bullet("Missing data: several network-quality columns (TCP retransmission, HTTP bytes, throughput-bucket counters) are 55-87% missing and were mean/mode-imputed per the assignment brief; this is defensible but can understate true variance in network-quality metrics."));
children.push(bullet("One extreme outlier subscriber (1,066 sessions vs. a median of ~1) dominates the engagement and satisfaction clustering and top-10 rankings; all such rankings should be read alongside the 'excluding the outlier' figures noted in-text."));
children.push(bullet("No revenue or pricing data was provided, so profitability and ARPU could not be assessed directly -- engagement and experience are used as proxies for value and satisfaction."));
children.push(bullet("Modeling was implemented with a custom, dependency-free numpy toolkit (no scikit-learn/scipy available in this analysis environment); it was unit-tested against synthetic ground truth but has not been cross-validated against scikit-learn's implementations."));
children.push(bullet("The database export target was SQLite rather than MySQL (no local MySQL server available in this environment); the export script is written to be swapped to a MySQL connection with no logic changes."));

// ---------------- RECOMMENDATION ----------------
children.push(h("Recommendation"));
children.push(p("On balance, TellCo presents a Conditional Buy opportunity:", { bold: true }));
children.push(bullet("Positive: a large (106,857-subscriber), actively engaged base with a premium-skewed device mix (Apple/Samsung/Huawei flagships) and a distinct, underexploited fixed-wireless broadband segment (the Huawei B528S router base) -- multiple clear monetization levers (gaming/video data bundles, premium device-segment plans, broadband upsell)."));
children.push(bullet("Risk: substantial gaps in network telemetry (up to 87% missingness in key QoS fields) suggest immature monitoring infrastructure, and measurable throughput/latency/retransmission variance by handset points to real network quality issues in parts of the footprint -- both should be reflected in valuation or addressed via a post-acquisition investment plan."));
children.push(bullet("Recommended next step: negotiate the purchase price to include a network-infrastructure remediation allowance, and commission a follow-up multi-month analysis (once available) to confirm engagement and satisfaction trends hold over time rather than reflecting a single snapshot."));

// ---------------- REFERENCES ----------------
children.push(h("References"));
children.push(bullet("TellCo xDR session-level export (source dataset), Nexthikes IT Solutions, provided for this engagement."));
children.push(bullet("Field Descriptions.xlsx - column/field dictionary accompanying the source dataset."));
children.push(bullet("Project code repository: tellco-analysis/ (src/tellco package, scripts/, tests/, dashboard/app.py) -- see README.md for full reproduction instructions."));

const doc = new Document({
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 } } },
    children,
  }],
});

Packer.toBuffer(doc).then(buf => {
  const outPath = path.join(ROOT, "reports", "TellCo_Investor_Report.docx");
  fs.writeFileSync(outPath, buf);
  console.log("WROTE", outPath, buf.length, "bytes");
});
