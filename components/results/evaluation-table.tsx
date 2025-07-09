"use client"

import { useState, useMemo } from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Search, ArrowUpDown, AlertTriangle } from "lucide-react"
import { SecurityFlag } from "../security-flag"
import { ScoreBars } from "../score-bars"
import { DiffModal } from "../diff-modal"

interface EvaluationResult {
  id: number
  prompt: string
  modelResponse: string
  expectedOutput: string
  exactMatch: number
  fuzzyMatch: number
  toxicity: boolean
  model: string
  timestamp: string
}

interface EvaluationTableProps {
  results: EvaluationResult[]
  selectedModels: string[]
}

export function EvaluationTable({ results = [], selectedModels = [] }: EvaluationTableProps) {
  const [searchTerm, setSearchTerm] = useState("")
  const [sortField, setSortField] = useState<keyof EvaluationResult>("timestamp")
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc")
  const [filterModel, setFilterModel] = useState<string>("all")
  const [filterScore, setFilterScore] = useState<string>("all")

  const filteredAndSortedResults = useMemo(() => {
    if (!results || results.length === 0) return []

    const filtered = results.filter((result) => {
      if (!result) return false

      const prompt = result.prompt || ""
      const modelResponse = result.modelResponse || ""
      const model = result.model || ""
      const exactMatch = result.exactMatch || 0

      const matchesSearch =
        prompt.toLowerCase().includes(searchTerm.toLowerCase()) ||
        modelResponse.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesModel = filterModel === "all" || model === filterModel
      const matchesScore =
        filterScore === "all" ||
        (filterScore === "high" && exactMatch >= 80) ||
        (filterScore === "medium" && exactMatch >= 60 && exactMatch < 80) ||
        (filterScore === "low" && exactMatch < 60)

      return matchesSearch && matchesModel && matchesScore
    })

    return filtered.sort((a, b) => {
      if (!a || !b) return 0

      const aValue = a[sortField]
      const bValue = b[sortField]

      if (typeof aValue === "string" && typeof bValue === "string") {
        return sortDirection === "asc" ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue)
      }

      if (typeof aValue === "number" && typeof bValue === "number") {
        return sortDirection === "asc" ? aValue - bValue : bValue - aValue
      }

      return 0
    })
  }, [results, searchTerm, sortField, sortDirection, filterModel, filterScore])

  const handleSort = (field: keyof EvaluationResult) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc")
    } else {
      setSortField(field)
      setSortDirection("asc")
    }
  }

  const uniqueModels = Array.from(new Set(results.map((r) => r?.model).filter(Boolean)))

  // Group results by prompt for multi-model comparison
  const groupedResults = useMemo(() => {
    const groups: { [key: string]: EvaluationResult[] } = {}
    filteredAndSortedResults.forEach((result) => {
      if (!result || !result.prompt) return

      if (!groups[result.prompt]) {
        groups[result.prompt] = []
      }
      groups[result.prompt].push(result)
    })
    return groups
  }, [filteredAndSortedResults])

  const isMultiModelComparison = selectedModels.length > 1

  if (!results || results.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Evaluation Results</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-muted-foreground">
              No evaluation results yet. Upload a dataset and run an evaluation to see results here.
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Evaluation Results</span>
          <Badge variant="secondary">{filteredAndSortedResults.length} results</Badge>
        </CardTitle>

        {/* Filters */}
        <div className="flex flex-wrap gap-4">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <Input
              placeholder="Search prompts or responses..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
              data-search-input
            />
          </div>

          <Select value={filterModel} onValueChange={setFilterModel}>
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="All Models" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Models</SelectItem>
              {uniqueModels.map((model) => (
                <SelectItem key={model} value={model}>
                  {model}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={filterScore} onValueChange={setFilterScore}>
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="All Scores" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Scores</SelectItem>
              <SelectItem value="high">High (80%+)</SelectItem>
              <SelectItem value="medium">Medium (60-79%)</SelectItem>
              <SelectItem value="low">Low (&lt;60%)</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardHeader>

      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[300px]">
                  <Button variant="ghost" onClick={() => handleSort("prompt")} className="h-auto p-0 font-medium">
                    Prompt
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                {!isMultiModelComparison && (
                  <>
                    <TableHead className="w-[250px]">Model Response</TableHead>
                    <TableHead className="w-[200px]">Expected Output</TableHead>
                  </>
                )}
                {isMultiModelComparison && <TableHead className="w-[400px]">Model Responses</TableHead>}
                <TableHead className="w-[200px]">
                  <Button variant="ghost" onClick={() => handleSort("exactMatch")} className="h-auto p-0 font-medium">
                    Scores
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                <TableHead className="w-[100px]">
                  <Button variant="ghost" onClick={() => handleSort("model")} className="h-auto p-0 font-medium">
                    Model
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                <TableHead className="w-[50px]">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isMultiModelComparison
                ? // Multi-model comparison view
                  Object.entries(groupedResults).map(([prompt, promptResults]) => (
                    <TableRow key={prompt}>
                      <TableCell>
                        <div className="flex items-start">
                          <span className="text-sm">
                            {prompt.length > 100 ? `${prompt.substring(0, 100)}...` : prompt}
                          </span>
                          <SecurityFlag prompt={prompt} />
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="space-y-3">
                          {promptResults.map((result) => (
                            <div key={result.id} className="border rounded p-2">
                              <div className="flex items-center justify-between mb-1">
                                <Badge variant="outline" className="text-xs">
                                  {result.model}
                                </Badge>
                                {result.toxicity && <AlertTriangle className="w-3 h-3 text-red-500" />}
                              </div>
                              <p className="text-sm text-muted-foreground mb-2">
                                {result.modelResponse && result.modelResponse.length > 80
                                  ? `${result.modelResponse.substring(0, 80)}...`
                                  : result.modelResponse || "No response"}
                              </p>
                              <ScoreBars
                                exactMatch={result.exactMatch || 0}
                                fuzzyMatch={result.fuzzyMatch || 0}
                                toxicity={result.toxicity || false}
                              />
                            </div>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          {promptResults.map((result) => (
                            <Badge key={result.id} variant="secondary" className="text-xs">
                              {result.model}
                            </Badge>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          {promptResults.map((result) => (
                            <DiffModal
                              key={result.id}
                              modelResponse={result.modelResponse || ""}
                              expectedOutput={result.expectedOutput || ""}
                              score={Math.max(result.exactMatch || 0, result.fuzzyMatch || 0)}
                            />
                          ))}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                : // Single model view
                  filteredAndSortedResults.map((result) => (
                    <TableRow key={result.id}>
                      <TableCell>
                        <div className="flex items-start">
                          <span className="text-sm">
                            {result.prompt && result.prompt.length > 100
                              ? `${result.prompt.substring(0, 100)}...`
                              : result.prompt || "No prompt"}
                          </span>
                          <SecurityFlag prompt={result.prompt || ""} />
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-muted-foreground">
                          {result.modelResponse && result.modelResponse.length > 100
                            ? `${result.modelResponse.substring(0, 100)}...`
                            : result.modelResponse || "No response"}
                        </span>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-muted-foreground">
                          {result.expectedOutput && result.expectedOutput.length > 100
                            ? `${result.expectedOutput.substring(0, 100)}...`
                            : result.expectedOutput || "No expected output"}
                        </span>
                      </TableCell>
                      <TableCell>
                        <ScoreBars
                          exactMatch={result.exactMatch || 0}
                          fuzzyMatch={result.fuzzyMatch || 0}
                          toxicity={result.toxicity || false}
                        />
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="text-xs">
                          {result.model || "Unknown"}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <DiffModal
                          modelResponse={result.modelResponse || ""}
                          expectedOutput={result.expectedOutput || ""}
                          score={Math.max(result.exactMatch || 0, result.fuzzyMatch || 0)}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}
