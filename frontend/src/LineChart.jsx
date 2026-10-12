// Small dependency-free SVG line chart.
export default function LineChart({ title, unit = "", points, color = "var(--accent)" }) {
  const W = 320, H = 130, P = { l: 38, r: 10, t: 10, b: 18 };
  if (!points.length) return null;
  const min = Math.min(...points), max = Math.max(...points);
  const span = max - min || 1;
  const x = (i) => P.l + (i / Math.max(points.length - 1, 1)) * (W - P.l - P.r);
  const y = (v) => P.t + (1 - (v - min) / span) * (H - P.t - P.b);
  const d = points.map((v, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(" ");
  const last = points[points.length - 1];
  return (
    <figure className="chart">
      <figcaption>
        {title} <strong>{last}{unit}</strong>
      </figcaption>
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${title} over time, latest ${last}${unit}`}>
        {[min, (min + max) / 2, max].map((v) => (
          <g key={v}>
            <line x1={P.l} x2={W - P.r} y1={y(v)} y2={y(v)} className="grid" />
            <text x={P.l - 6} y={y(v) + 4} textAnchor="end" className="tick">{Math.round(v)}</text>
          </g>
        ))}
        <path d={d} fill="none" stroke={color} strokeWidth="2" strokeLinejoin="round" />
        <circle cx={x(points.length - 1)} cy={y(last)} r="3.5" fill={color} />
        <text x={P.l} y={H - 4} className="tick">30 days ago</text>
        <text x={W - P.r} y={H - 4} textAnchor="end" className="tick">now</text>
      </svg>
    </figure>
  );
}
