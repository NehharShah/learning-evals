"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { FileText, Target, AlertTriangle, TrendingUp } from "lucide-react"

interface SummaryCardsProps {
  totalPrompts: number
  averageExactMatch: number
  averageFuzzyMatch: number
  flaggedPrompts: number
}

export function SummaryCards({
  totalPrompts,
  averageExactMatch,
  averageFuzzyMatch,
  flaggedPrompts,
}: SummaryCardsProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600 dark:text-green-400"
    if (score >= 60) return "text-yellow-600 dark:text-yellow-400"
    return "text-red-600 dark:text-red-400"
  }

  const getScoreBadgeVariant = (score: number) => {
    if (score >= 80) return "default"
    if (score >= 60) return "secondary"
    return "destructive"
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Prompts</CardTitle>
          <FileText className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{totalPrompts.toLocaleString()}</div>
          <p className="text-xs text-muted-foreground">Evaluated across all models</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Avg Exact Match</CardTitle>
          <Target className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className={`text-2xl font-bold ${getScoreColor(averageExactMatch)}`}>
            {averageExactMatch.toFixed(1)}%
          </div>
          <Badge variant={getScoreBadgeVariant(averageExactMatch)} className="text-xs">
            {averageExactMatch >= 80 ? "Excellent" : averageExactMatch >= 60 ? "Good" : "Needs Improvement"}
          </Badge>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Avg Fuzzy Match</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className={`text-2xl font-bold ${getScoreColor(averageFuzzyMatch)}`}>
            {averageFuzzyMatch.toFixed(1)}%
          </div>
          <Badge variant={getScoreBadgeVariant(averageFuzzyMatch)} className="text-xs">
            {averageFuzzyMatch >= 80 ? "Excellent" : averageFuzzyMatch >= 60 ? "Good" : "Needs Improvement"}
          </Badge>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Flagged Prompts</CardTitle>
          <AlertTriangle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-red-600 dark:text-red-400">{flaggedPrompts}</div>
          <p className="text-xs text-muted-foreground">Security & safety alerts</p>
        </CardContent>
      </Card>
    </div>
  )
}
