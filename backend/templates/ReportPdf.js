// // backend/templates/ReportPdf.js
// const React = require("react");
// const { Document, Page, Text, View, StyleSheet, Link } = require("@react-pdf/renderer");

// const styles = StyleSheet.create({
//   page: { padding: 28, fontSize: 11, color: "#222" },

//   title: { fontSize: 18, color: "#003366", marginBottom: 8 },
//   meta: { fontSize: 9, color: "#666", marginBottom: 14, lineHeight: 1.4 },

//   h2: { fontSize: 13, color: "#003366", marginTop: 14, marginBottom: 6 },
//   h3: { fontSize: 11, color: "#003366", marginTop: 10, marginBottom: 4 },

//   li: { marginBottom: 4, lineHeight: 1.35 },

//   muted: { fontSize: 9, color: "#666", marginBottom: 2 },
//   warning: { color: "#a94442", fontWeight: 700 },

//   block: { marginBottom: 8 },
// });

// function asArray(x) {
//   return Array.isArray(x) ? x : [];
// }
// function safeText(x) {
//   if (x === null || x === undefined) return "";
//   return String(x);
// }
// function join(arr, sep = ", ") {
//   return asArray(arr).map(safeText).filter(Boolean).join(sep);
// }

// const e = React.createElement;

// module.exports = function ReportPdf({ report }) {
//   const title = report?.title || "CrewAI Report";
//   const sections = report?.sections || {};

//   const exec = asArray(sections.executive_summary);

//   const ct = sections.clinical_trials || {};
//   const ctSummary = ct.summary || {};
//   const phaseDist = ctSummary.phase_distribution || {};
//   const highlights = asArray(ct.highlights);
//   const topTrials = asArray(ct.top_trials);

//   const gl = sections.guidelines_and_literature || {};
//   const guidelines = asArray(gl.guideline_points);
//   const pubs = asArray(gl.publication_points);
//   const news = asArray(gl.news_signals);

//   const repOpts = asArray(sections.repurposing_options);
//   const risks = asArray(sections.risks_and_gaps);
//   const refs = asArray(sections.references);
//   const warnings = asArray(report?.warnings);

//   const metaBlock = e(
//     View,
//     { style: styles.meta, wrap: true },
//     e(Text, { wrap: true }, `Report ID: ${safeText(report?.report_id)}`),
//     e(Text, { wrap: true }, `Generated At: ${safeText(report?.generated_at)}`),
//     e(Text, { wrap: true }, `Format: ${safeText(report?.format || "pdf")}`)
//   );

//   const execList =
//     exec.length > 0
//       ? exec.map((p, i) =>
//           e(Text, { key: `exec-${i}`, style: styles.li, wrap: true }, `• ${safeText(p)}`)
//         )
//       : [e(Text, { key: "exec-empty", style: styles.muted, wrap: true }, "No executive summary available.")];

//   const phaseList =
//     Object.keys(phaseDist).length > 0
//       ? Object.entries(phaseDist).map(([k, v]) =>
//           e(Text, { key: `phase-${k}`, style: styles.li, wrap: true }, `• ${safeText(k)}: ${safeText(v)}`)
//         )
//       : [e(Text, { key: "phase-empty", style: styles.muted, wrap: true }, "No phase distribution available.")];

//   const highlightList =
//     highlights.length > 0
//       ? highlights.map((h, i) =>
//           e(Text, { key: `hi-${i}`, style: styles.li, wrap: true }, `• ${safeText(h)}`)
//         )
//       : [e(Text, { key: "hi-empty", style: styles.muted, wrap: true }, "No highlights available.")];

//   // ✅ SAFE Top Trials (list blocks, no table)
//   const topTrialsBlocks =
//     topTrials.length > 0
//       ? topTrials.map((t, idx) =>
//           e(
//             View,
//             { key: `trial-${idx}`, style: styles.block, wrap: false },
//             e(
//               Text,
//               { style: styles.li, wrap: true },
//               `• ${safeText(t.trial_id)} — ${safeText(t.title)}`
//             ),
//             e(
//               Text,
//               { style: styles.muted, wrap: true },
//               `Phase: ${safeText(t.phase)} | Status: ${safeText(t.status)} | Sponsor: ${safeText(t.sponsor)}`
//             ),
//             e(
//               Text,
//               { style: styles.muted, wrap: true },
//               `Locations: ${join(t.locations)} | Start: ${safeText(t.start_date)}`
//             )
//           )
//         )
//       : [e(Text, { key: "trial-empty", style: styles.muted, wrap: true }, "No trial records available.")];

//   const guidelineBlocks =
//     guidelines.length > 0
//       ? guidelines.map((g, i) =>
//           e(
//             View,
//             { key: `g-${i}`, style: styles.block, wrap: false },
//             e(
//               Text,
//               { style: styles.li, wrap: true },
//               `• ${safeText(g.source)}: ${safeText(g.recommendation)}`
//             ),
//             e(
//               Text,
//               { style: styles.muted, wrap: true },
//               `Publisher: ${safeText(g.publisher)}${g.date ? ` | Date: ${safeText(g.date)}` : ""}`
//             ),
//             g.url
//               ? e(
//                   Link,
//                   { src: g.url },
//                   e(Text, { style: styles.muted, wrap: true }, safeText(g.url))
//                 )
//               : null
//           )
//         )
//       : [e(Text, { key: "g-empty", style: styles.muted, wrap: true }, "No guideline points available.")];

//   const pubBlocks =
//     pubs.length > 0
//       ? pubs.map((p, i) =>
//           e(
//             View,
//             { key: `p-${i}`, style: styles.block, wrap: false },
//             e(
//               Text,
//               { style: styles.li, wrap: true },
//               `• PMID ${safeText(p.pmid)} (${safeText(p.year)}): ${safeText(p.title)}`
//             ),
//             e(Text, { style: styles.muted, wrap: true }, `Journal: ${safeText(p.journal)}`),
//             e(Text, { style: styles.muted, wrap: true }, `Finding: ${safeText(p.key_finding)}`)
//           )
//         )
//       : [e(Text, { key: "p-empty", style: styles.muted, wrap: true }, "No publications available.")];

//   const newsBlocks =
//     news.length > 0
//       ? news.map((n, i) =>
//           e(
//             View,
//             { key: `n-${i}`, style: styles.block, wrap: false },
//             e(Text, { style: styles.li, wrap: true }, `• ${safeText(n.headline)}`),
//             e(
//               Text,
//               { style: styles.muted, wrap: true },
//               `${safeText(n.publisher)}${n.date ? ` | ${safeText(n.date)}` : ""}`
//             ),
//             e(Text, { style: styles.muted, wrap: true }, safeText(n.takeaway)),
//             n.url
//               ? e(
//                   Link,
//                   { src: n.url },
//                   e(Text, { style: styles.muted, wrap: true }, safeText(n.url))
//                 )
//               : null
//           )
//         )
//       : [e(Text, { key: "n-empty", style: styles.muted, wrap: true }, "No news signals available.")];

//   const repBlocks =
//     repOpts.length > 0
//       ? repOpts.map((o, i) =>
//           e(
//             View,
//             { key: `r-${i}`, style: styles.block, wrap: false },
//             e(Text, { style: styles.li, wrap: true }, `• ${safeText(o.option)}`),
//             e(Text, { style: styles.muted, wrap: true }, `Rationale: ${safeText(o.rationale)}`),
//             e(Text, { style: styles.muted, wrap: true }, `Evidence: ${join(o.evidence)}`)
//           )
//         )
//       : [e(Text, { key: "r-empty", style: styles.muted, wrap: true }, "No repurposing options available.")];

//   const riskList =
//     risks.length > 0
//       ? risks.map((r, i) =>
//           e(Text, { key: `risk-${i}`, style: styles.li, wrap: true }, `• ${safeText(r)}`)
//         )
//       : [e(Text, { key: "risk-empty", style: styles.muted, wrap: true }, "No risks/gaps available.")];

//   const refBlocks =
//     refs.length > 0
//       ? refs.map((r, i) =>
//           e(
//             View,
//             { key: `ref-${i}`, style: styles.block, wrap: false },
//             e(Text, { style: styles.li, wrap: true }, `• ${safeText(r.type)}: ${safeText(r.label)}`),
//             r.url
//               ? e(
//                   Link,
//                   { src: r.url },
//                   e(Text, { style: styles.muted, wrap: true }, safeText(r.url))
//                 )
//               : e(Text, { style: styles.muted, wrap: true }, "(No URL)")
//           )
//         )
//       : [e(Text, { key: "ref-empty", style: styles.muted, wrap: true }, "No references available.")];

//   const warningSection =
//     warnings.length > 0
//       ? [
//           e(Text, { key: "w-h", style: styles.h2, wrap: true }, "Warnings"),
//           ...warnings.map((w, i) =>
//             e(Text, { key: `w-${i}`, style: [styles.li, styles.warning], wrap: true }, `• ${safeText(w)}`)
//           ),
//         ]
//       : [];

//   return e(
//     Document,
//     null,
//     e(
//       Page,
//       { size: "A4", style: styles.page, wrap: true },
//       e(Text, { style: styles.title, wrap: true }, title),
//       metaBlock,

//       e(Text, { style: styles.h2, wrap: true }, "Executive Summary"),
//       ...execList,

//       e(Text, { style: styles.h2, wrap: true }, "Clinical Trials"),
//       e(Text, { style: styles.h3, wrap: true }, "Summary"),
//       e(Text, { style: styles.li, wrap: true }, `• Active trials: ${safeText(ctSummary.active)}`),
//       e(Text, { style: styles.li, wrap: true }, `• Completed trials: ${safeText(ctSummary.completed)}`),

//       e(Text, { style: styles.h3, wrap: true }, "Phase distribution"),
//       ...phaseList,

//       e(Text, { style: styles.h3, wrap: true }, "Highlights"),
//       ...highlightList,

//       e(Text, { style: styles.h3, wrap: true }, "Top Trials"),
//       ...topTrialsBlocks,

//       e(Text, { style: styles.h2, wrap: true }, "Guidelines and Literature"),
//       e(Text, { style: styles.h3, wrap: true }, "Guidelines"),
//       ...guidelineBlocks,

//       e(Text, { style: styles.h3, wrap: true }, "Publications"),
//       ...pubBlocks,

//       e(Text, { style: styles.h3, wrap: true }, "News Signals"),
//       ...newsBlocks,

//       e(Text, { style: styles.h2, wrap: true }, "Repurposing Options"),
//       ...repBlocks,

//       e(Text, { style: styles.h2, wrap: true }, "Risks and Gaps"),
//       ...riskList,

//       e(Text, { style: styles.h2, wrap: true }, "References"),
//       ...refBlocks,

//       ...warningSection
//     )
//   );
// };

// backend/templates/ReportPdf.js
const React = require("react");
const { Document, Page, Text, View, StyleSheet, Link } = require("@react-pdf/renderer");

const styles = StyleSheet.create({
  page: { padding: 28, fontSize: 11, color: "#222" },

  title: { fontSize: 18, color: "#003366", marginBottom: 8 },
  meta: { fontSize: 9, color: "#666", marginBottom: 14, lineHeight: 1.4 },

  h2: { fontSize: 13, color: "#003366", marginTop: 14, marginBottom: 6 },
  h3: { fontSize: 11, color: "#003366", marginTop: 10, marginBottom: 4 },

  li: { marginBottom: 4, lineHeight: 1.35 },

  muted: { fontSize: 9, color: "#666", marginBottom: 2 },
  warning: { color: "#a94442", fontWeight: 700 },

  block: { marginBottom: 8 },

  // ✅ Table styles (Top Trials)
  table: { marginTop: 6, borderWidth: 1, borderColor: "#ccc" },
  row: { flexDirection: "row" },

  th: {
    padding: 6,
    fontSize: 9,
    backgroundColor: "#f2f2f2",
    borderRightWidth: 1,
    borderRightColor: "#ccc",
    fontWeight: 700,
  },
  td: {
    padding: 6,
    fontSize: 9,
    borderRightWidth: 1,
    borderRightColor: "#ccc",
  },

  cellId: { width: "16%" },
  cellTitle: { width: "44%" },
  cellPhase: { width: "12%" },
  cellStatus: { width: "12%" },
  cellStart: { width: "16%", borderRightWidth: 0 },
});

function asArray(x) {
  return Array.isArray(x) ? x : [];
}
function safeText(x) {
  if (x === null || x === undefined) return "";
  return String(x);
}
function join(arr, sep = ", ") {
  return asArray(arr).map(safeText).filter(Boolean).join(sep);
}

const e = React.createElement;

module.exports = function ReportPdf({ report }) {
  const title = report?.title || "CrewAI Report";
  const sections = report?.sections || {};

  const exec = asArray(sections.executive_summary);

  const ct = sections.clinical_trials || {};
  const ctSummary = ct.summary || {};
  const phaseDist = ctSummary.phase_distribution || {};
  const highlights = asArray(ct.highlights);
  const topTrials = asArray(ct.top_trials);

  const gl = sections.guidelines_and_literature || {};
  const guidelines = asArray(gl.guideline_points);
  const pubs = asArray(gl.publication_points);
  const news = asArray(gl.news_signals);

  const repOpts = asArray(sections.repurposing_options);
  const risks = asArray(sections.risks_and_gaps);
  const refs = asArray(sections.references);
  const warnings = asArray(report?.warnings);

  const metaBlock = e(
    View,
    { style: styles.meta, wrap: true },
    e(Text, { wrap: true }, `Report ID: ${safeText(report?.report_id)}`),
    e(Text, { wrap: true }, `Generated At: ${safeText(report?.generated_at)}`),
    e(Text, { wrap: true }, `Format: ${safeText(report?.format || "pdf")}`)
  );

  const execList =
    exec.length > 0
      ? exec.map((p, i) =>
          e(Text, { key: `exec-${i}`, style: styles.li, wrap: true }, `• ${safeText(p)}`)
        )
      : [e(Text, { key: "exec-empty", style: styles.muted, wrap: true }, "No executive summary available.")];

  const phaseList =
    Object.keys(phaseDist).length > 0
      ? Object.entries(phaseDist).map(([k, v]) =>
          e(Text, { key: `phase-${k}`, style: styles.li, wrap: true }, `• ${safeText(k)}: ${safeText(v)}`)
        )
      : [e(Text, { key: "phase-empty", style: styles.muted, wrap: true }, "No phase distribution available.")];

  const highlightList =
    highlights.length > 0
      ? highlights.map((h, i) =>
          e(Text, { key: `hi-${i}`, style: styles.li, wrap: true }, `• ${safeText(h)}`)
        )
      : [e(Text, { key: "hi-empty", style: styles.muted, wrap: true }, "No highlights available.")];

  // ✅ Top Trials as a table (safe + wraps title text)
  const topTrialsBlocks =
    topTrials.length > 0
      ? [
          e(
            View,
            { key: "tt-table", style: styles.table, wrap: false },
            // Header row
            e(
              View,
              { style: styles.row },
              e(Text, { style: [styles.th, styles.cellId] }, "Trial ID"),
              e(Text, { style: [styles.th, styles.cellTitle] }, "Title"),
              e(Text, { style: [styles.th, styles.cellPhase] }, "Phase"),
              e(Text, { style: [styles.th, styles.cellStatus] }, "Status"),
              e(Text, { style: [styles.th, styles.cellStart] }, "Start Date")
            ),
            // Data rows
            ...topTrials.map((t, idx) =>
              e(
                View,
                { key: `tt-row-${idx}`, style: styles.row, wrap: false },
                e(Text, { style: [styles.td, styles.cellId] }, safeText(t.trial_id)),
                e(Text, { style: [styles.td, styles.cellTitle], wrap: true }, safeText(t.title)),
                e(Text, { style: [styles.td, styles.cellPhase] }, safeText(t.phase)),
                e(Text, { style: [styles.td, styles.cellStatus] }, safeText(t.status)),
                e(Text, { style: [styles.td, styles.cellStart] }, safeText(t.start_date))
              )
            )
          ),
        ]
      : [e(Text, { key: "trial-empty", style: styles.muted, wrap: true }, "No trial records available.")];

  const guidelineBlocks =
    guidelines.length > 0
      ? guidelines.map((g, i) =>
          e(
            View,
            { key: `g-${i}`, style: styles.block, wrap: false },
            e(Text, { style: styles.li, wrap: true }, `• ${safeText(g.source)}: ${safeText(g.recommendation)}`),
            e(
              Text,
              { style: styles.muted, wrap: true },
              `Publisher: ${safeText(g.publisher)}${g.date ? ` | Date: ${safeText(g.date)}` : ""}`
            ),
            g.url
              ? e(Link, { src: g.url }, e(Text, { style: styles.muted, wrap: true }, safeText(g.url)))
              : null
          )
        )
      : [e(Text, { key: "g-empty", style: styles.muted, wrap: true }, "No guideline points available.")];

  const pubBlocks =
    pubs.length > 0
      ? pubs.map((p, i) =>
          e(
            View,
            { key: `p-${i}`, style: styles.block, wrap: false },
            e(
              Text,
              { style: styles.li, wrap: true },
              `• PMID ${safeText(p.pmid)} (${safeText(p.year)}): ${safeText(p.title)}`
            ),
            e(Text, { style: styles.muted, wrap: true }, `Journal: ${safeText(p.journal)}`),
            e(Text, { style: styles.muted, wrap: true }, `Finding: ${safeText(p.key_finding)}`)
          )
        )
      : [e(Text, { key: "p-empty", style: styles.muted, wrap: true }, "No publications available.")];

  const newsBlocks =
    news.length > 0
      ? news.map((n, i) =>
          e(
            View,
            { key: `n-${i}`, style: styles.block, wrap: false },
            e(Text, { style: styles.li, wrap: true }, `• ${safeText(n.headline)}`),
            e(
              Text,
              { style: styles.muted, wrap: true },
              `${safeText(n.publisher)}${n.date ? ` | ${safeText(n.date)}` : ""}`
            ),
            e(Text, { style: styles.muted, wrap: true }, safeText(n.takeaway)),
            n.url
              ? e(Link, { src: n.url }, e(Text, { style: styles.muted, wrap: true }, safeText(n.url)))
              : null
          )
        )
      : [e(Text, { key: "n-empty", style: styles.muted, wrap: true }, "No news signals available.")];

  const repBlocks =
    repOpts.length > 0
      ? repOpts.map((o, i) =>
          e(
            View,
            { key: `r-${i}`, style: styles.block, wrap: false },
            e(Text, { style: styles.li, wrap: true }, `• ${safeText(o.option)}`),
            e(Text, { style: styles.muted, wrap: true }, `Rationale: ${safeText(o.rationale)}`),
            e(Text, { style: styles.muted, wrap: true }, `Evidence: ${join(o.evidence)}`)
          )
        )
      : [e(Text, { key: "r-empty", style: styles.muted, wrap: true }, "No repurposing options available.")];

  const riskList =
    risks.length > 0
      ? risks.map((r, i) => e(Text, { key: `risk-${i}`, style: styles.li, wrap: true }, `• ${safeText(r)}`))
      : [e(Text, { key: "risk-empty", style: styles.muted, wrap: true }, "No risks/gaps available.")];

  const refBlocks =
    refs.length > 0
      ? refs.map((r, i) =>
          e(
            View,
            { key: `ref-${i}`, style: styles.block, wrap: false },
            e(Text, { style: styles.li, wrap: true }, `• ${safeText(r.type)}: ${safeText(r.label)}`),
            r.url
              ? e(Link, { src: r.url }, e(Text, { style: styles.muted, wrap: true }, safeText(r.url)))
              : e(Text, { style: styles.muted, wrap: true }, "(No URL)")
          )
        )
      : [e(Text, { key: "ref-empty", style: styles.muted, wrap: true }, "No references available.")];

  const warningSection =
    warnings.length > 0
      ? [
          e(Text, { key: "w-h", style: styles.h2, wrap: true }, "Warnings"),
          ...warnings.map((w, i) =>
            e(Text, { key: `w-${i}`, style: [styles.li, styles.warning], wrap: true }, `• ${safeText(w)}`)
          ),
        ]
      : [];

  return e(
    Document,
    null,
    e(
      Page,
      { size: "A4", style: styles.page, wrap: true },
      e(Text, { style: styles.title, wrap: true }, title),
      metaBlock,

      e(Text, { style: styles.h2, wrap: true }, "Executive Summary"),
      ...execList,

      e(Text, { style: styles.h2, wrap: true }, "Clinical Trials"),
      e(Text, { style: styles.h3, wrap: true }, "Summary"),
      e(Text, { style: styles.li, wrap: true }, `• Active trials: ${safeText(ctSummary.active)}`),
      e(Text, { style: styles.li, wrap: true }, `• Completed trials: ${safeText(ctSummary.completed)}`),

      e(Text, { style: styles.h3, wrap: true }, "Phase distribution"),
      ...phaseList,

      e(Text, { style: styles.h3, wrap: true }, "Highlights"),
      ...highlightList,

      e(Text, { style: styles.h3, wrap: true }, "Top Trials"),
      ...topTrialsBlocks,

      e(Text, { style: styles.h2, wrap: true }, "Guidelines and Literature"),
      e(Text, { style: styles.h3, wrap: true }, "Guidelines"),
      ...guidelineBlocks,

      e(Text, { style: styles.h3, wrap: true }, "Publications"),
      ...pubBlocks,

      e(Text, { style: styles.h3, wrap: true }, "News Signals"),
      ...newsBlocks,

      e(Text, { style: styles.h2, wrap: true }, "Repurposing Options"),
      ...repBlocks,

      e(Text, { style: styles.h2, wrap: true }, "Risks and Gaps"),
      ...riskList,

      e(Text, { style: styles.h2, wrap: true }, "References"),
      ...refBlocks,

      ...warningSection
    )
  );
};
