import "./BarChart.css";

// Histogramme groupé : entrants (sky) vs sortants (lime) par semaine du mois.
export default function BarChart({ data }) {
  const W = 620;
  const H = 240;
  const padL = 28;
  const padB = 34;
  const padT = 18;
  const chartH = H - padB - padT;
  const baseline = padT + chartH;
  const max = Math.max(1, ...data.flatMap((d) => [d.entrants, d.sortants]));
  const groupW = (W - padL) / data.length;
  const barW = Math.min(26, groupW / 3.2);
  const y = (v) => padT + chartH * (1 - v / max);

  return (
    <div className="bar-chart">
      <div className="bar-legende">
        <span><i style={{ background: "var(--brand-sky)" }} /> Entrants</span>
        <span><i style={{ background: "var(--brand-lime)" }} /> Sortants</span>
      </div>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        preserveAspectRatio="xMidYMid meet"
        role="img"
        aria-label="Répartition des courriers entrants et sortants par semaine"
      >
        <line x1={padL} y1={baseline} x2={W} y2={baseline} stroke="var(--border)" />
        {data.map((d, i) => {
          const centre = padL + groupW * i + groupW / 2;
          return (
            <g key={d.semaine}>
              {[
                { v: d.entrants, x: centre - barW - 2, fill: "var(--brand-sky)" },
                { v: d.sortants, x: centre + 2, fill: "var(--brand-lime)" },
              ].map((b, j) => (
                <g key={j}>
                  <rect x={b.x} y={y(b.v)} width={barW} height={baseline - y(b.v)} fill={b.fill} rx="2" />
                  {b.v > 0 && (
                    <text x={b.x + barW / 2} y={y(b.v) - 5} textAnchor="middle" className="bar-valeur">
                      {b.v}
                    </text>
                  )}
                </g>
              ))}
              <text x={centre} y={baseline + 20} textAnchor="middle" className="bar-label">
                S{d.semaine}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
