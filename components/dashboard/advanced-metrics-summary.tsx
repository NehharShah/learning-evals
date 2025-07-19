"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { BarChart3, TrendingUp, Brain, Target } from "lucide-react"

interface AdvancedMetricsSummary {
  averageBleuScore: number
  averageRougeF1: {
    "rouge-1": number
    "rouge-2": number
    "rouge-l": number
  }
  averageSemanticSimilarity: {
    tfidf: number
    jaccard: number
    sequence: number
  }
}

interface AdvancedMetricsSummaryProps {
  summary: AdvancedMetricsSummary
  className?: string
}

export function AdvancedMetricsSummary({ summary, className = "" }: AdvancedMetricsSummaryProps) {
  const formatScore = (score: number) => {
    return (score * 100).toFixed(1)
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return "text-green-600"
    if (score >= 0.6) return "text-yellow-600"
    return "text-red-600"
  }

  const getScoreBadgeVariant = (score: number) => {
    if (score >= 0.8) return "default" as const
    if (score >= 0.6) return "secondary" as const
    return "destructive" as const
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-blue-600" />
          Advanced Metrics Summary
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* BLEU Score Summary */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Target className="h-4 w-4 text-blue-600" />
            <span className="font-medium">Average BLEU Score</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Badge variant={getScoreBadgeVariant(summary.averageBleuScore)}>
                {formatScore(summary.averageBleuScore)}%
              </Badge>
              <span className={`text-sm font-medium ${getScoreColor(summary.averageBleuScore)}`}>
                {summary.averageBleuScore.toFixed(3)}
              </span>
            </div>
          </div>
          <Progress value={summary.averageBleuScore * 100} className="h-2" />
        </div>

        {/* ROUGE Scores Summary */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-orange-600" />
            <span className="font-medium">Average ROUGE F1 Scores</span>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center space-y-2">
              <div className="text-sm font-medium">ROUGE-1</div>
              <Badge variant={getScoreBadgeVariant(summary.averageRougeF1["rouge-1"])}>
                {formatScore(summary.averageRougeF1["rouge-1"])}%
              </Badge>
              <Progress value={summary.averageRougeF1["rouge-1"] * 100} className="h-2" />
            </div>
            <div className="text-center space-y-2">
              <div className="text-sm font-medium">ROUGE-2</div>
              <Badge variant={getScoreBadgeVariant(summary.averageRougeF1["rouge-2"])}>
                {formatScore(summary.averageRougeF1["rouge-2"])}%
              </Badge>
              <Progress value={summary.averageRougeF1["rouge-2"] * 100} className="h-2" />
            </div>
            <div className="text-center space-y-2">
              <div className="text-sm font-medium">ROUGE-L</div>
              <Badge variant={getScoreBadgeVariant(summary.averageRougeF1["rouge-l"])}>
                {formatScore(summary.averageRougeF1["rouge-l"])}%
              </Badge>
              <Progress value={summary.averageRougeF1["rouge-l"] * 100} className="h-2" />
            </div>
          </div>
        </div>

        {/* Semantic Similarity Summary */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Brain className="h-4 w-4 text-purple-600" />
            <span className="font-medium">Average Semantic Similarity</span>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">TF-IDF Cosine</span>
              <div className="flex items-center gap-2">
                <Progress value={summary.averageSemanticSimilarity.tfidf * 100} className="w-20 h-2" />
                <Badge variant={getScoreBadgeVariant(summary.averageSemanticSimilarity.tfidf)}>
                  {formatScore(summary.averageSemanticSimilarity.tfidf)}%
                </Badge>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Jaccard</span>
              <div className="flex items-center gap-2">
                <Progress value={summary.averageSemanticSimilarity.jaccard * 100} className="w-20 h-2" />
                <Badge variant={getScoreBadgeVariant(summary.averageSemanticSimilarity.jaccard)}>
                  {formatScore(summary.averageSemanticSimilarity.jaccard)}%
                </Badge>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Sequence</span>
              <div className="flex items-center gap-2">
                <Progress value={summary.averageSemanticSimilarity.sequence * 100} className="w-20 h-2" />
                <Badge variant={getScoreBadgeVariant(summary.averageSemanticSimilarity.sequence)}>
                  {formatScore(summary.averageSemanticSimilarity.sequence)}%
                </Badge>
              </div>
            </div>
          </div>
        </div>

        {/* Metrics Legend */}
        <div className="pt-4 border-t">
          <div className="text-xs text-muted-foreground space-y-1">
            <p><strong>BLEU:</strong> Bilingual Evaluation Understudy - measures n-gram overlap</p>
            <p><strong>ROUGE:</strong> Recall-Oriented Understudy for Gisting Evaluation</p>
            <p><strong>Semantic Similarity:</strong> Different methods for measuring meaning similarity</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
} 