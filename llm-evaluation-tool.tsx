"use client"

import { useState } from "react"
import { Play, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { FileUpload } from "./components/file-upload"
import { MetricsSidebar } from "./components/metrics-sidebar"
import { ResultsTable } from "./components/results-table"

interface EvaluationResult {
  prompt: string
  modelResponse: string
  expected: string
  score: number
}

const models = [
  { value: "gpt-4", label: "GPT-4" },
  { value: "gpt-4-turbo", label: "GPT-4 Turbo" },
  { value: "gpt-3.5-turbo", label: "GPT-3.5 Turbo" },
  { value: "claude-3", label: "Claude 3" },
  { value: "gemini-pro", label: "Gemini Pro" },
]

export default function LLMEvaluationTool() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [selectedModel, setSelectedModel] = useState<string>("")
  const [selectedMetric, setSelectedMetric] = useState<string>("exact")
  const [isEvaluating, setIsEvaluating] = useState(false)
  const [results, setResults] = useState<EvaluationResult[]>([])

  const handleRunEvaluation = async () => {
    if (!selectedFile || !selectedModel) return

    setIsEvaluating(true)

    // Simulate evaluation process
    await new Promise((resolve) => setTimeout(resolve, 2000))

    // Mock results
    const mockResults: EvaluationResult[] = [
      {
        prompt: "What is the capital of France?",
        modelResponse: "The capital of France is Paris.",
        expected: "Paris",
        score: 0.95,
      },
      {
        prompt: "Explain quantum computing in simple terms.",
        modelResponse: "Quantum computing uses quantum bits that can be in multiple states simultaneously.",
        expected: "Quantum computing leverages quantum mechanics principles for computation.",
        score: 0.78,
      },
      {
        prompt: "What is 2 + 2?",
        modelResponse: "2 + 2 equals 4.",
        expected: "4",
        score: 1.0,
      },
      {
        prompt: "Name three programming languages.",
        modelResponse: "Python, JavaScript, and Java are three popular programming languages.",
        expected: "Python, Java, C++",
        score: 0.67,
      },
    ]

    setResults(mockResults)
    setIsEvaluating(false)
  }

  const canRunEvaluation = selectedFile && selectedModel && !isEvaluating

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">LLM Evaluation Tool</h1>
          <p className="text-gray-600">
            Upload your dataset, select a model, and evaluate LLM performance with precision.
          </p>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <MetricsSidebar selectedMetric={selectedMetric} onMetricChange={setSelectedMetric} />
          </div>

          {/* Main Panel */}
          <div className="lg:col-span-3 space-y-6">
            {/* Configuration Panel */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg font-semibold">Configuration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* File Upload */}
                <div>
                  <FileUpload onFileSelect={setSelectedFile} selectedFile={selectedFile} />
                </div>

                {/* Model Selection and Run Button */}
                <div className="flex flex-col sm:flex-row gap-4 items-end">
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Select Model</label>
                    <Select value={selectedModel} onValueChange={setSelectedModel}>
                      <SelectTrigger>
                        <SelectValue placeholder="Choose a model..." />
                      </SelectTrigger>
                      <SelectContent>
                        {models.map((model) => (
                          <SelectItem key={model.value} value={model.value}>
                            {model.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <Button
                    onClick={handleRunEvaluation}
                    disabled={!canRunEvaluation}
                    size="lg"
                    className="bg-blue-600 hover:bg-blue-700 px-8"
                  >
                    {isEvaluating ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Evaluating...
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 mr-2" />
                        Run Evaluation
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Results */}
            <ResultsTable results={results} />
          </div>
        </div>
      </div>
    </div>
  )
}
