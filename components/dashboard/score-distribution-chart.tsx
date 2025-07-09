"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, PieChart, Pie, Cell } from "recharts"

interface ScoreDistributionChartProps {
  data: Array<{
    range: string
    exactMatch: number
    fuzzyMatch: number
  }>
  type?: "bar" | "pie"
}

const COLORS = ["#ef4444", "#f97316", "#eab308", "#22c55e"]

export function ScoreDistributionChart({ data, type = "bar" }: ScoreDistributionChartProps) {
  const pieData = data.map((item, index) => ({
    name: item.range,
    value: item.exactMatch,
    color: COLORS[index % COLORS.length],
  }))

  if (type === "pie") {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Score Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={{
              value: {
                label: "Count",
                color: "hsl(var(--chart-1))",
              },
            }}
            className="h-[300px]"
          >
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <ChartTooltip content={<ChartTooltipContent />} />
              </PieChart>
            </ResponsiveContainer>
          </ChartContainer>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Score Distribution</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer
          config={{
            exactMatch: {
              label: "Exact Match",
              color: "hsl(var(--chart-1))",
            },
            fuzzyMatch: {
              label: "Fuzzy Match",
              color: "hsl(var(--chart-2))",
            },
          }}
          className="h-[300px]"
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <XAxis dataKey="range" />
              <YAxis />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Bar dataKey="exactMatch" fill="var(--color-exactMatch)" />
              <Bar dataKey="fuzzyMatch" fill="var(--color-fuzzyMatch)" />
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
