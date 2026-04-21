import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
  CartesianGrid,
} from "recharts";
import type { Paper } from "../types";
import { Breadcrumb } from "../components/Breadcrumb";
import {
  countBy, countMulti,
  getDSSFocusGroup, getIndustryGroup,
  normalizeDataSource,
} from "../utils/groupings";


// Consistent color palette
// Matches generate_figures_mikkel.py PALETTE
const PALETTE = [
  "#2C3E50", "#E74C3C", "#3498DB", "#208346", "#F39C12",
  "#9B59B6", "#1ABC9C", "#E67E22", "#34495E", "#E91E63",
];

// Matches generate_figures_mikkel.py level_colors mapping
const LEVEL_COLORS: Record<string, string> = {
  L0: PALETTE[0], // #2C3E50 dark blue-gray
  L1: PALETTE[3], // #208346 green
  L2: PALETTE[4], // #F39C12 yellow (with diagonal hatches)
  L3: PALETTE[1], // #E74C3C red
};

const PIE_COLORS = [
  PALETTE[6], PALETTE[0], PALETTE[1], PALETTE[2],
  PALETTE[3], PALETTE[4], PALETTE[5], PALETTE[7],
  PALETTE[8], PALETTE[9], "#95a5a6",
];

interface ChartSectionProps {
  id: string;
  title: string;
  figNum: string;
  children: React.ReactNode;
}

function ChartSection({ id, title, figNum, children }: ChartSectionProps) {
  return (
    <section className="chart-section" id={id}>
      <h2 className="chart-title">
        <span className="chart-fig-num">{figNum}</span> {title}
      </h2>
      {children}
    </section>
  );
}

// Custom tooltip for bar/pie charts
function CountTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ value: number }>; label?: string }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <strong>{label}</strong>: {payload[0].value} papers
    </div>
  );
}

export function Dashboard({ papers }: { papers: Paper[] }) {
  const navigate = useNavigate();

  // ---- DATA COMPUTATIONS ----

  // Stacked timeline: year × level
  const LEVELS = ["L0", "L1", "L2", "L3"] as const;

  const timelineData = useMemo(() => {
    const years = [...new Set(papers.map((p) => p.year))].sort();
    return years.map((year) => {
      const yearPapers = papers.filter((p) => p.year === year);
      const row: Record<string, number | string> = { year: String(year) };
      let total = 0;
      for (const lvl of LEVELS) {
        const count = yearPapers.filter((p) => {
          const ml = p.manufacturingLevel;
          if (lvl === "L3") return ml === "L3" || ml === "L3/L4" || ml === "L4";
          return ml === lvl;
        }).length;
        row[lvl] = count;
        total += count;
      }
      row.total = total;
      return row;
    });
  }, [papers]);

  const countryData = useMemo(() => {
    return countBy(papers, (p) => p.country).filter((d) => d.count >= 2);
  }, [papers]);

  const techData = useMemo(
    () => countMulti(papers, "technologies").filter((d) => d.count >= 2),
    [papers]
  );

  const dssFocusData = useMemo(
    () => countBy(papers, (p) => getDSSFocusGroup(p.dssFocus)),
    [papers]
  );

  const evalData = useMemo(
    () => countBy(papers, (p) => p.evaluationSetting),
    [papers]
  );

  const dataSourceData = useMemo(
    () => countBy(papers, (p) => normalizeDataSource(p.dataSource)),
    [papers]
  );

  const snowballData = useMemo(() => {
    const yes = papers.filter((p) => p.snowball).length;
    return [
      { name: "Database search", count: papers.length - yes },
      { name: "Snowball", count: yes },
    ];
  }, [papers]);

  const industryData = useMemo(
    () => countBy(papers, (p) => getIndustryGroup(p.industry)),
    [papers]
  );

  // Word cloud data
  const wordCloudData = useMemo(() => {
    const techCounts = countMulti(papers, "technologies");
    const methodCounts = countMulti(papers, "methods");
    return [...techCounts, ...methodCounts].sort((a, b) => b.count - a.count);
  }, [papers]);

  // ---- RENDER ----

  return (
    <div className="page">
      <Breadcrumb crumbs={[{ label: "Levels", to: "/" }, { label: "Dashboard" }]} />
      <h1>Survey Dashboard</h1>
      <p className="subtitle">{papers.length} papers — interactive overview</p>

      <nav className="chart-nav">
        {[
          ["#timeline", "Timeline + Levels"],
          ["#countries", "Countries"],
          ["#technologies", "Technologies"],
          ["#wordcloud", "Word Cloud"],
          ["#dss-focus", "DSS Focus"],
          ["#evaluation", "Evaluation"],
          ["#datasource", "Data Source"],
          ["#snowball", "Snowball"],
          ["#industry", "Industry"],
        ].map(([href, label]) => (
          <a key={href} href={href} className="chart-nav-link">{label}</a>
        ))}
      </nav>

      {/* Fig 01+02: Publication Timeline stacked by Manufacturing Level */}
      <ChartSection id="timeline" title="Publications per Year (by Manufacturing Level)" figNum="01/02">
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={timelineData} onClick={(e) => {
            if (e?.activeLabel) navigate(`/search?years=${e.activeLabel}`);
          }}>
            <defs>
              <pattern
                id="hatch-L2"
                patternUnits="userSpaceOnUse"
                width={6}
                height={6}
                patternTransform="rotate(45)"
              >
                <rect width={6} height={6} fill={LEVEL_COLORS.L2} />
                <line x1={0} y1={0} x2={0} y2={6} stroke="#2C3E50" strokeWidth={1.2} />
              </pattern>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="year" />
            <YAxis />
            <Tooltip
              content={({ active, payload, label }) => {
                if (!active || !payload?.length) return null;
                const total = payload.reduce((s, p) => s + (Number(p.value) || 0), 0);
                return (
                  <div className="chart-tooltip">
                    <strong>{label}</strong> — {total} papers
                    {payload.map((p) => (
                      <div key={String(p.dataKey)} style={{ color: p.color }}>
                        {String(p.dataKey)}: {String(p.value)}
                      </div>
                    ))}
                  </div>
                );
              }}
            />
            <Legend />
            {LEVELS.map((lvl) => (
              <Bar
                key={lvl}
                dataKey={lvl}
                stackId="level"
                fill={lvl === "L2" ? "url(#hatch-L2)" : LEVEL_COLORS[lvl]}
                cursor="pointer"
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </ChartSection>

      {/* Fig 03: Country Distribution */}
      <ChartSection id="countries" title="Country Distribution" figNum="03">
        <ResponsiveContainer width="100%" height={Math.max(300, countryData.length * 28)}>
          <BarChart data={countryData} layout="vertical" onClick={(e) => {
            if (e?.activeLabel) navigate(`/search?countries=${encodeURIComponent(e.activeLabel)}`);
          }}>
            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
            <XAxis type="number" />
            <YAxis dataKey="name" type="category" width={100} tick={{ fontSize: 12 }} />
            <Tooltip content={<CountTooltip />} />
            <Bar dataKey="count" fill={PALETTE[0]} radius={[0, 4, 4, 0]} cursor="pointer" />
          </BarChart>
        </ResponsiveContainer>
      </ChartSection>

      {/* Fig 04: Technology Landscape */}
      <ChartSection id="technologies" title="Technology Landscape" figNum="04">
        <ResponsiveContainer width="100%" height={Math.max(300, techData.length * 28)}>
          <BarChart data={techData} layout="vertical" onClick={(e) => {
            if (e?.activeLabel) navigate(`/search?technologies=${encodeURIComponent(e.activeLabel)}`);
          }}>
            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
            <XAxis type="number" />
            <YAxis dataKey="name" type="category" width={110} tick={{ fontSize: 12 }} />
            <Tooltip content={<CountTooltip />} />
            <Bar dataKey="count" fill={PALETTE[2]} radius={[0, 4, 4, 0]} cursor="pointer" />
          </BarChart>
        </ResponsiveContainer>
      </ChartSection>

      {/* Fig 04c: Word Cloud */}
      <ChartSection id="wordcloud" title="Methods & Technologies Word Cloud" figNum="04c">
        <WordCloud data={wordCloudData} onWordClick={(word) => navigate(`/search?q=${encodeURIComponent(word)}`)} />
      </ChartSection>

      {/* Fig 05: DSS Focus */}
      <ChartSection id="dss-focus" title="DSS Focus Areas" figNum="05">
        <ResponsiveContainer width="100%" height={350}>
          <PieChart>
            <Pie
              data={dssFocusData}
              dataKey="count"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={130}
              label={({ name, percent }) =>
                `${name} (${((percent ?? 0) * 100).toFixed(1)}%)`
              }
              labelLine
              cursor="pointer"
              onClick={(entry) => {
                if (entry?.name) navigate(`/search?dssFocus=${encodeURIComponent(entry.name)}`);
              }}
            >
              {dssFocusData.map((_, i) => (
                <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => `${value} papers`} />
          </PieChart>
        </ResponsiveContainer>
      </ChartSection>

      {/* Fig 07: Evaluation Setting */}
      <ChartSection id="evaluation" title="Evaluation Setting" figNum="07">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={evalData} onClick={(e) => {
            if (e?.activeLabel) navigate(`/search?eval=${encodeURIComponent(e.activeLabel)}`);
          }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis />
            <Tooltip content={<CountTooltip />} />
            <Bar dataKey="count" fill={PALETTE[3]} radius={[4, 4, 0, 0]} cursor="pointer" />
          </BarChart>
        </ResponsiveContainer>
      </ChartSection>

      {/* Fig 08: Data Source */}
      <ChartSection id="datasource" title="Data Source" figNum="08">
        <ResponsiveContainer width="100%" height={Math.max(250, dataSourceData.length * 40)}>
          <BarChart data={dataSourceData} layout="vertical" onClick={(e) => {
            if (e?.activeLabel) navigate(`/search?dataSource=${encodeURIComponent(e.activeLabel)}`);
          }}>
            <CartesianGrid strokeDasharray="3 3" horizontal={false} />
            <XAxis type="number" />
            <YAxis dataKey="name" type="category" width={140} tick={{ fontSize: 12 }} />
            <Tooltip content={<CountTooltip />} />
            <Bar dataKey="count" fill={PALETTE[4]} radius={[0, 4, 4, 0]} cursor="pointer" />
          </BarChart>
        </ResponsiveContainer>
      </ChartSection>

      {/* Fig 09: Snowball Source */}
      <ChartSection id="snowball" title="Paper Source (Snowball vs Database)" figNum="09">
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={snowballData}
              dataKey="count"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={110}
              label={({ name, percent }) =>
                `${name} ${((percent ?? 0) * 100).toFixed(0)}%`
              }
              cursor="pointer"
              onClick={(entry) => {
                if (entry?.name) {
                  const val = entry.name === "Snowball" ? "yes" : "no";
                  navigate(`/search?snowball=${val}`);
                }
              }}
            >
              <Cell fill={PALETTE[0]} />
              <Cell fill={PALETTE[1]} />
            </Pie>
            <Tooltip formatter={(value) => `${value} papers`} />
          </PieChart>
        </ResponsiveContainer>
      </ChartSection>

      {/* Fig 10: Industry Distribution */}
      <ChartSection id="industry" title="Industry Distribution" figNum="10">
        <ResponsiveContainer width="100%" height={350}>
          <PieChart>
            <Pie
              data={industryData}
              dataKey="count"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={130}
              label={({ name, percent }) =>
                `${name} (${((percent ?? 0) * 100).toFixed(1)}%)`
              }
              labelLine
              cursor="pointer"
              onClick={(entry) => {
                if (entry?.name) navigate(`/search?industry=${encodeURIComponent(entry.name)}`);
              }}
            >
              {industryData.map((_, i) => (
                <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => `${value} papers`} />
          </PieChart>
        </ResponsiveContainer>
      </ChartSection>

    </div>
  );
}

// ---- CUSTOM COMPONENTS ----

function WordCloud({ data, onWordClick }: { data: { name: string; count: number }[]; onWordClick: (word: string) => void }) {
  const maxCount = Math.max(...data.map((d) => d.count));
  const colors = PALETTE;

  return (
    <div className="word-cloud">
      {data.map((d, i) => {
        const size = 0.7 + (d.count / maxCount) * 2.3;
        return (
          <span
            key={d.name}
            className="word-cloud-word"
            style={{
              fontSize: `${size}rem`,
              color: colors[i % colors.length],
              opacity: 0.7 + (d.count / maxCount) * 0.3,
              cursor: "pointer",
            }}
            title={`${d.name}: ${d.count} papers`}
            onClick={() => onWordClick(d.name)}
          >
            {d.name}
          </span>
        );
      })}
    </div>
  );
}

