"use client"

import { Badge } from "@/components/ui/badge"

interface ScoreBarsProps {
  exactMatch: number
  fuzzyMatch: number
  toxicity: boolean
}

export function ScoreBars({ exactMatch, fuzzyMatch, toxicity }: ScoreBarsProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return "bg-green-500"
    if (score >= 60) return "bg-yellow-500"
    return "bg-red-500"
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <span className="text-xs font-medium w-16">Exact:</span>
        <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div className={`h-2 rounded-full ${getScoreColor(exactMatch)}`} style={{ width: `${exactMatch}%` }} />
        </div>
        <span className="text-xs w-8">{exactMatch}%</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-xs font-medium w-16">Fuzzy:</span>
        <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div className={`h-2 rounded-full ${getScoreColor(fuzzyMatch)}`} style={{ width: `${fuzzyMatch}%` }} />
        </div>
        <span className="text-xs w-8">{fuzzyMatch}%</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-xs font-medium w-16">Toxic:</span>
        <Badge variant={toxicity ? "destructive" : "secondary"} className="text-xs">
          {toxicity ? "Yes" : "No"}
        </Badge>
      </div>
    </div>
  )
}
