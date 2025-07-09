"use client"

import { useState } from "react"
import { Play, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface TryItLiveProps {
  onAddResult: (result: any) => void
}

export function TryItLive({ onAddResult }: TryItLiveProps) {
  const [prompt, setPrompt] = useState("")
  const [selectedModel, setSelectedModel] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleRunEvaluation = async () => {
    if (!prompt.trim() || !selectedModel) return

    setIsLoading(true)

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000))

    // Mock response generation
    const mockResponse = `This is a simulated response for: ${prompt.substring(0, 50)}...`
    const mockExpected = "Expected output for comparison"

    const result = {
      id: Date.now(),
      prompt,
      modelResponse: mockResponse,
      expectedOutput: mockExpected,
      exactMatch: Math.floor(Math.random() * 100),
      fuzzyMatch: Math.floor(Math.random() * 100),
      toxicity: Math.random() > 0.8,
      model: selectedModel,
    }

    onAddResult(result)
    setPrompt("")
    setIsLoading(false)
  }

  return (
    <Card className="mt-6">
      <CardHeader>
        <CardTitle className="text-lg">Try It Live</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <Label htmlFor="live-prompt">Prompt</Label>
            <Input
              id="live-prompt"
              placeholder="Enter your prompt here..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="mt-1"
            />
          </div>
          <div>
            <Label htmlFor="live-model">Model</Label>
            <Select value={selectedModel} onValueChange={setSelectedModel}>
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="Select model" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="gpt-4">GPT-4</SelectItem>
                <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                <SelectItem value="claude-3">Claude 3</SelectItem>
                <SelectItem value="gemini-pro">Gemini Pro</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <Button
          onClick={handleRunEvaluation}
          disabled={!prompt.trim() || !selectedModel || isLoading}
          className="w-full md:w-auto"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Running...
            </>
          ) : (
            <>
              <Play className="w-4 h-4 mr-2" />
              Run Evaluation
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  )
}
