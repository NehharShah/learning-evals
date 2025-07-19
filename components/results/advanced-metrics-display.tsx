"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { 
  BarChart3, 
  TrendingUp, 
  Brain, 
  ChevronDown, 
  ChevronUp,
  Info
} from "lucide-react"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

interface AdvancedMetrics {
  bleuScore: number
  rougeScores: {
    "rouge-1": { precision: number; recall: number; f1: number }
    "rouge-2": { precision: number; recall: number; f1: number }
    "rouge-l": { precision: number; recall: number; f1: number }
  }
  semanticSimilarity: {
    tfidf: number
    jaccard: number
    sequence: number
  }
}

interface AdvancedMetricsDisplayProps {
  metrics: AdvancedMetrics
  className?: string
}

export function AdvancedMetricsDisplay({ metrics, className = "" }: AdvancedMetricsDisplayProps) {
  const [isExpanded, setIsExpanded] = useState(false)

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
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-blue-600" />
            <CardTitle className="text-lg">Advanced Metrics</CardTitle>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger>
                  <Info className="h-4 w-4 text-muted-foreground" />
                </TooltipTrigger>
                <TooltipContent>
                  <p className="max-w-xs">
                    Advanced NLP metrics for evaluating text similarity and quality
                  </p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="h-8 w-8 p-0"
          >
            {isExpanded ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* BLEU Score */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="font-medium">BLEU Score</span>
              <Badge variant={getScoreBadgeVariant(metrics.bleuScore)}>
                {formatScore(metrics.bleuScore)}%
              </Badge>
            </div>
            <span className={`text-sm font-medium ${getScoreColor(metrics.bleuScore)}`}>
              {metrics.bleuScore.toFixed(3)}
            </span>
          </div>
          <Progress value={metrics.bleuScore * 100} className="h-2" />
          <p className="text-xs text-muted-foreground">
            Bilingual Evaluation Understudy - measures n-gram overlap
          </p>
        </div>

        {isExpanded && (
          <>
            {/* ROUGE Scores */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-orange-600" />
                <span className="font-medium">ROUGE Scores</span>
              </div>
              
              <Tabs defaultValue="rouge-1" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="rouge-1">ROUGE-1</TabsTrigger>
                  <TabsTrigger value="rouge-2">ROUGE-2</TabsTrigger>
                  <TabsTrigger value="rouge-l">ROUGE-L</TabsTrigger>
                </TabsList>
                
                <TabsContent value="rouge-1" className="space-y-2">
                  <div className="grid grid-cols-3 gap-2 text-sm">
                    <div className="text-center">
                      <div className="font-medium">Precision</div>
                      <Badge variant="outline" className="mt-1">
                        {formatScore(metrics.rougeScores["rouge-1"].precision)}%
                      </Badge>
                    </div>
                    <div className="text-center">
                      <div className="font-medium">Recall</div>
                      <Badge variant="outline" className="mt-1">
                        {formatScore(metrics.rougeScores["rouge-1"].recall)}%
                      </Badge>
                    </div>
                    <div className="text-center">
                      <div className="font-medium">F1</div>
                      <Badge variant={getScoreBadgeVariant(metrics.rougeScores["rouge-1"].f1)} className="mt-1">
                        {formatScore(metrics.rougeScores["rouge-1"].f1)}%
                      </Badge>
                    </div>
                  </div>
                </TabsContent>
                
                <TabsContent value="rouge-2" className="space-y-2">
                  <div className="grid grid-cols-3 gap-2 text-sm">
                    <div className="text-center">
                      <div className="font-medium">Precision</div>
                      <Badge variant="outline" className="mt-1">
                        {formatScore(metrics.rougeScores["rouge-2"].precision)}%
                      </Badge>
                    </div>
                    <div className="text-center">
                      <div className="font-medium">Recall</div>
                      <Badge variant="outline" className="mt-1">
                        {formatScore(metrics.rougeScores["rouge-2"].recall)}%
                      </Badge>
                    </div>
                    <div className="text-center">
                      <div className="font-medium">F1</div>
                      <Badge variant={getScoreBadgeVariant(metrics.rougeScores["rouge-2"].f1)} className="mt-1">
                        {formatScore(metrics.rougeScores["rouge-2"].f1)}%
                      </Badge>
                    </div>
                  </div>
                </TabsContent>
                
                <TabsContent value="rouge-l" className="space-y-2">
                  <div className="grid grid-cols-3 gap-2 text-sm">
                    <div className="text-center">
                      <div className="font-medium">Precision</div>
                      <Badge variant="outline" className="mt-1">
                        {formatScore(metrics.rougeScores["rouge-l"].precision)}%
                      </Badge>
                    </div>
                    <div className="text-center">
                      <div className="font-medium">Recall</div>
                      <Badge variant="outline" className="mt-1">
                        {formatScore(metrics.rougeScores["rouge-l"].recall)}%
                      </Badge>
                    </div>
                    <div className="text-center">
                      <div className="font-medium">F1</div>
                      <Badge variant={getScoreBadgeVariant(metrics.rougeScores["rouge-l"].f1)} className="mt-1">
                        {formatScore(metrics.rougeScores["rouge-l"].f1)}%
                      </Badge>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
              
              <p className="text-xs text-muted-foreground">
                Recall-Oriented Understudy for Gisting Evaluation - measures n-gram and LCS overlap
              </p>
            </div>

            {/* Semantic Similarity */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Brain className="h-4 w-4 text-purple-600" />
                <span className="font-medium">Semantic Similarity</span>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">TF-IDF Cosine</span>
                  <div className="flex items-center gap-2">
                    <Progress value={metrics.semanticSimilarity.tfidf * 100} className="w-20 h-2" />
                    <Badge variant={getScoreBadgeVariant(metrics.semanticSimilarity.tfidf)}>
                      {formatScore(metrics.semanticSimilarity.tfidf)}%
                    </Badge>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm">Jaccard</span>
                  <div className="flex items-center gap-2">
                    <Progress value={metrics.semanticSimilarity.jaccard * 100} className="w-20 h-2" />
                    <Badge variant={getScoreBadgeVariant(metrics.semanticSimilarity.jaccard)}>
                      {formatScore(metrics.semanticSimilarity.jaccard)}%
                    </Badge>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm">Sequence</span>
                  <div className="flex items-center gap-2">
                    <Progress value={metrics.semanticSimilarity.sequence * 100} className="w-20 h-2" />
                    <Badge variant={getScoreBadgeVariant(metrics.semanticSimilarity.sequence)}>
                      {formatScore(metrics.semanticSimilarity.sequence)}%
                    </Badge>
                  </div>
                </div>
              </div>
              
              <p className="text-xs text-muted-foreground">
                Different methods for measuring semantic similarity between texts
              </p>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
} 