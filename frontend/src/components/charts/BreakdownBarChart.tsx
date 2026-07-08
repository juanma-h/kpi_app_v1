import { Bar, BarChart, CartesianGrid, Cell, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { EmptyState } from "@/components/ui/States";

export interface BreakdownDatum {
  label: string;
  value: number;
  tone?: string;
}

const DEFAULT_COLOR = "var(--color-series-1)";

function ChartTooltip({
  active,
  payload,
  valueFormatter,
}: {
  active?: boolean;
  payload?: { payload: BreakdownDatum }[];
  valueFormatter: (v: number) => string;
}) {
  if (!active || !payload || payload.length === 0) return null;
  const datum = payload[0].payload;
  return (
    <div className="glass-panel rounded-lg bg-(--color-surface-2) px-3 py-2 text-xs shadow-xl">
      <p className="font-medium text-ink">{datum.label}</p>
      <p className="text-ink-secondary">{valueFormatter(datum.value)}</p>
    </div>
  );
}

export function BreakdownBarChart({
  data,
  valueFormatter = (v: number) => `${v}`,
  color = DEFAULT_COLOR,
  height,
}: {
  data: BreakdownDatum[];
  valueFormatter?: (value: number) => string;
  color?: string;
  height?: number;
}) {
  if (data.length === 0) {
    return <EmptyState title="Sin datos para este período" />;
  }

  const chartHeight = height ?? Math.max(160, data.length * 42);

  return (
    <ResponsiveContainer width="100%" height={chartHeight}>
      <BarChart data={data} layout="vertical" margin={{ top: 4, right: 36, bottom: 4, left: 4 }} barCategoryGap={10}>
        <CartesianGrid horizontal={false} stroke="var(--color-border)" />
        <XAxis type="number" hide />
        <YAxis
          type="category"
          dataKey="label"
          width={132}
          tickLine={false}
          axisLine={false}
          tick={{ fill: "var(--color-ink-secondary)", fontSize: 12 }}
        />
        <Tooltip cursor={{ fill: "rgba(255,255,255,0.04)" }} content={<ChartTooltip valueFormatter={valueFormatter} />} />
        <Bar dataKey="value" radius={[4, 4, 4, 4]} maxBarSize={22}>
          {data.map((entry, index) => (
            <Cell key={index} fill={entry.tone ?? color} />
          ))}
          <LabelList
            dataKey="value"
            position="right"
            formatter={(v: unknown) => valueFormatter(Number(v))}
            fill="var(--color-ink-secondary)"
            fontSize={12}
          />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
