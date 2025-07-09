"use client"

import { Settings, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"

interface MetricsSidebarProps {
  selectedMetric: string
  onMetricChange: (metric: string) => void
}

export function MetricsSidebar({ selectedMetric, onMetricChange }: MetricsSidebarProps) {
  return (
    <Collapsible>
      <CollapsibleTrigger asChild>
        <Button variant="outline" size="sm" className="mb-4 bg-transparent">
          <Settings className="w-4 h-4 mr-2" />
          Evaluation Metrics
          <ChevronRight className="w-4 h-4 ml-2 transition-transform group-data-[state=open]:rotate-90" />
        </Button>
      </CollapsibleTrigger>
      <CollapsibleContent>
        <Card className="mb-6">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Select Metric</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <RadioGroup value={selectedMetric} onValueChange={onMetricChange}>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="exact" id="exact" />
                <Label htmlFor="exact" className="text-sm">
                  Exact Match
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="fuzzy" id="fuzzy" />
                <Label htmlFor="fuzzy" className="text-sm">
                  Fuzzy Match
                </Label>
              </div>
            </RadioGroup>
          </CardContent>
        </Card>
      </CollapsibleContent>
    </Collapsible>
  )
}
