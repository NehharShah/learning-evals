"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Play, Loader2, Settings, Zap } from "lucide-react"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"

interface PlaygroundProps {
  availableModels: string[]
  onAddResult: (result: any) => void
}

export function LivePlayground({ availableModels, onAddResult }: PlaygroundProps) {
  const [prompt, setPrompt] = useState("")
  const [selectedModel, setSelectedModel] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)

  // Model parameters
  const [temperature, setTemperature] = useState([0.7])
  const [maxTokens, setMaxTokens] = useState([1000])
  const [topP, setTopP] = useState([1.0])
  const [frequencyPenalty, setFrequencyPenalty] = useState([0.0])

  const handleRunEvaluation = async () => {
    if (!prompt.trim() || !selectedModel) return

    setIsLoading(true)

    try {
      // Simulate API call with model parameters
      await new Promise((resolve) => setTimeout(resolve, 2000))

      // Mock response generation with parameters influence
      const baseResponse = `This is a simulated response for: ${prompt.substring(0, 50)}...`
      const tempInfluence = temperature[0] > 0.8 ? " (creative)" : temperature[0] < 0.3 ? " (focused)" : ""
      const mockResponse = baseResponse + tempInfluence

      const result = {
        id: Date.now(),
        prompt,
        modelResponse: mockResponse,
        expectedOutput: "Expected output for comparison",
        exactMatch: Math.floor(Math.random() * 100),
        fuzzyMatch: Math.floor(Math.random() * 100),
        toxicity: Math.random() > 0.9,
        model: selectedModel,
        timestamp: new Date().toISOString(),
        parameters: {
          temperature: temperature[0],
          maxTokens: maxTokens[0],
          topP: topP[0],
          frequencyPenalty: frequencyPenalty[0],
        },
      }

      onAddResult(result)
      setPrompt("")
    } catch (error) {
      console.error("Error running evaluation:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const presetPrompts = [
    "Explain quantum computing in simple terms",
    "Write a creative story about a robot learning to paint",
    "Analyze the pros and cons of renewable energy",
    "Describe the process of photosynthesis",
    "What are the key principles of good software design?",
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Play className="w-5 h-5" />
          Live Prompt Playground
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Quick Presets */}
        <div className="space-y-2">
          <Label className="text-sm font-medium">Quick Presets</Label>
          <div className="flex flex-wrap gap-2">
            {presetPrompts.map((preset, index) => (
              <Button key={index} variant="outline" size="sm" onClick={() => setPrompt(preset)} className="text-xs">
                {preset.substring(0, 30)}...
              </Button>
            ))}
          </div>
        </div>

        <Separator />

        {/* Prompt Input */}
        <div className="space-y-2">
          <Label htmlFor="playground-prompt">Prompt</Label>
          <Textarea
            id="playground-prompt"
            placeholder="Enter your prompt here..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="min-h-[100px]"
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>{prompt.length} characters</span>
            <span>~{Math.ceil(prompt.length / 4)} tokens</span>
          </div>
        </div>

        {/* Model Selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="playground-model">Model</Label>
            <Select value={selectedModel} onValueChange={setSelectedModel}>
              <SelectTrigger>
                <SelectValue placeholder="Select a model" />
              </SelectTrigger>
              <SelectContent>
                {availableModels.map((model) => (
                  <SelectItem key={model} value={model}>
                    {model}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-end">
            <Button
              onClick={handleRunEvaluation}
              disabled={!prompt.trim() || !selectedModel || isLoading}
              className="w-full"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 mr-2" />
                  Run Evaluation
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Advanced Parameters */}
        <Collapsible open={showAdvanced} onOpenChange={setShowAdvanced}>
          <CollapsibleTrigger asChild>
            <Button variant="ghost" className="w-full justify-start p-0">
              <Settings className="w-4 h-4 mr-2" />
              Advanced Parameters
              {showAdvanced ? " (Hide)" : " (Show)"}
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent className="space-y-4 mt-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Temperature */}
              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label className="text-sm">Temperature</Label>
                  <Badge variant="outline" className="text-xs">
                    {temperature[0]}
                  </Badge>
                </div>
                <Slider
                  value={temperature}
                  onValueChange={setTemperature}
                  max={2}
                  min={0}
                  step={0.1}
                  className="w-full"
                />
                <p className="text-xs text-muted-foreground">
                  Controls randomness. Higher = more creative, Lower = more focused
                </p>
              </div>

              {/* Max Tokens */}
              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label className="text-sm">Max Tokens</Label>
                  <Badge variant="outline" className="text-xs">
                    {maxTokens[0]}
                  </Badge>
                </div>
                <Slider
                  value={maxTokens}
                  onValueChange={setMaxTokens}
                  max={4000}
                  min={50}
                  step={50}
                  className="w-full"
                />
                <p className="text-xs text-muted-foreground">Maximum length of the response</p>
              </div>

              {/* Top P */}
              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label className="text-sm">Top P</Label>
                  <Badge variant="outline" className="text-xs">
                    {topP[0]}
                  </Badge>
                </div>
                <Slider value={topP} onValueChange={setTopP} max={1} min={0} step={0.1} className="w-full" />
                <p className="text-xs text-muted-foreground">Controls diversity via nucleus sampling</p>
              </div>

              {/* Frequency Penalty */}
              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label className="text-sm">Frequency Penalty</Label>
                  <Badge variant="outline" className="text-xs">
                    {frequencyPenalty[0]}
                  </Badge>
                </div>
                <Slider
                  value={frequencyPenalty}
                  onValueChange={setFrequencyPenalty}
                  max={2}
                  min={-2}
                  step={0.1}
                  className="w-full"
                />
                <p className="text-xs text-muted-foreground">Reduces repetition. Positive = less repetitive</p>
              </div>
            </div>
          </CollapsibleContent>
        </Collapsible>
      </CardContent>
    </Card>
  )
}
