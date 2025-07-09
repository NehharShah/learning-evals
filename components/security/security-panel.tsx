"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { Shield, AlertTriangle, Eye, ChevronDown, ChevronRight, Zap, Ban, Flag } from "lucide-react"

interface SecurityMetrics {
  totalPrompts: number
  promptInjectionAttempts: number
  toxicityAlerts: number
  flaggedContent: number
  securityScore: number
}

interface SecurityPanelProps {
  metrics: SecurityMetrics
  isCollapsed?: boolean
}

export function SecurityPanel({ metrics, isCollapsed = false }: SecurityPanelProps) {
  const [isOpen, setIsOpen] = useState(!isCollapsed)

  const getSecurityLevel = (score: number) => {
    if (score >= 90)
      return { level: "Excellent", color: "text-green-600", bgColor: "bg-green-100 dark:bg-green-900/20" }
    if (score >= 70) return { level: "Good", color: "text-blue-600", bgColor: "bg-blue-100 dark:bg-blue-900/20" }
    if (score >= 50) return { level: "Fair", color: "text-yellow-600", bgColor: "bg-yellow-100 dark:bg-yellow-900/20" }
    return { level: "Poor", color: "text-red-600", bgColor: "bg-red-100 dark:bg-red-900/20" }
  }

  const securityLevel = getSecurityLevel(metrics.securityScore)

  const riskCategories = [
    {
      name: "Prompt Injection",
      count: metrics.promptInjectionAttempts,
      total: metrics.totalPrompts,
      icon: <Zap className="w-4 h-4" />,
      color: "text-red-600",
      description: "Attempts to manipulate model behavior",
    },
    {
      name: "Toxic Content",
      count: metrics.toxicityAlerts,
      total: metrics.totalPrompts,
      icon: <Ban className="w-4 h-4" />,
      color: "text-orange-600",
      description: "Harmful or inappropriate content detected",
    },
    {
      name: "Flagged Content",
      count: metrics.flaggedContent,
      total: metrics.totalPrompts,
      icon: <Flag className="w-4 h-4" />,
      color: "text-yellow-600",
      description: "Content requiring manual review",
    },
  ]

  return (
    <Card className="h-fit">
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CollapsibleTrigger asChild>
          <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Security & Safety
              </div>
              {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </CardTitle>
          </CardHeader>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <CardContent className="space-y-6">
            {/* Overall Security Score */}
            <div className={`p-4 rounded-lg ${securityLevel.bgColor}`}>
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">Security Score</span>
                <Badge variant="outline" className={securityLevel.color}>
                  {securityLevel.level}
                </Badge>
              </div>
              <div className="flex items-center gap-3">
                <Progress value={metrics.securityScore} className="flex-1" />
                <span className={`font-bold ${securityLevel.color}`}>{metrics.securityScore}%</span>
              </div>
            </div>

            {/* Risk Categories */}
            <div className="space-y-4">
              <h4 className="font-medium text-sm">Risk Categories</h4>
              {riskCategories.map((category) => {
                const percentage = metrics.totalPrompts > 0 ? (category.count / metrics.totalPrompts) * 100 : 0

                return (
                  <div key={category.name} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className={category.color}>{category.icon}</span>
                        <span className="text-sm font-medium">{category.name}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-muted-foreground">
                          {category.count}/{metrics.totalPrompts}
                        </span>
                        <Badge variant={category.count > 0 ? "destructive" : "secondary"} className="text-xs">
                          {percentage.toFixed(1)}%
                        </Badge>
                      </div>
                    </div>
                    <Progress value={percentage} className="h-2" />
                    <p className="text-xs text-muted-foreground">{category.description}</p>
                  </div>
                )
              })}
            </div>

            {/* Quick Actions */}
            <div className="space-y-2">
              <h4 className="font-medium text-sm">Quick Actions</h4>
              <div className="grid grid-cols-1 gap-2">
                <Button variant="outline" size="sm" className="justify-start bg-transparent">
                  <Eye className="w-4 h-4 mr-2" />
                  View Flagged Content
                </Button>
                <Button variant="outline" size="sm" className="justify-start bg-transparent">
                  <AlertTriangle className="w-4 h-4 mr-2" />
                  Security Report
                </Button>
              </div>
            </div>

            {/* Security Tips */}
            {metrics.promptInjectionAttempts > 0 && (
              <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 text-yellow-600 mt-0.5" />
                  <div className="text-sm">
                    <p className="font-medium text-yellow-800 dark:text-yellow-200">Security Alert</p>
                    <p className="text-yellow-700 dark:text-yellow-300">
                      {metrics.promptInjectionAttempts} prompt injection attempts detected. Consider implementing
                      additional input validation.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  )
}
