"use client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Bot, Zap, Clock, DollarSign } from "lucide-react"

interface Model {
  id: string
  name: string
  provider: string
  description: string
  speed: "fast" | "medium" | "slow"
  cost: "low" | "medium" | "high"
  capabilities: string[]
}

const availableModels: Model[] = [
  {
    id: "gpt-4",
    name: "GPT-4",
    provider: "OpenAI",
    description: "Most capable model for complex reasoning tasks",
    speed: "medium",
    cost: "high",
    capabilities: ["reasoning", "coding", "analysis"],
  },
  {
    id: "gpt-3.5-turbo",
    name: "GPT-3.5 Turbo",
    provider: "OpenAI",
    description: "Fast and efficient for most tasks",
    speed: "fast",
    cost: "low",
    capabilities: ["general", "coding", "summarization"],
  },
  {
    id: "claude-3",
    name: "Claude 3",
    provider: "Anthropic",
    description: "Excellent for analysis and creative tasks",
    speed: "medium",
    cost: "medium",
    capabilities: ["analysis", "creative", "reasoning"],
  },
  {
    id: "gemini-pro",
    name: "Gemini Pro",
    provider: "Google",
    description: "Multimodal capabilities with strong performance",
    speed: "fast",
    cost: "medium",
    capabilities: ["multimodal", "reasoning", "coding"],
  },
  {
    id: "llama-2",
    name: "Llama 2",
    provider: "Meta",
    description: "Open-source model with good performance",
    speed: "medium",
    cost: "low",
    capabilities: ["general", "reasoning", "coding"],
  },
]

interface ModelSelectorProps {
  selectedModels: string[]
  onModelChange: (models: string[]) => void
}

export function ModelSelector({ selectedModels, onModelChange }: ModelSelectorProps) {
  const handleModelToggle = (modelId: string) => {
    if (selectedModels.includes(modelId)) {
      onModelChange(selectedModels.filter((id) => id !== modelId))
    } else {
      onModelChange([...selectedModels, modelId])
    }
  }

  const selectAll = () => {
    onModelChange(availableModels.map((m) => m.id))
  }

  const clearAll = () => {
    onModelChange([])
  }

  const getSpeedIcon = (speed: string) => {
    switch (speed) {
      case "fast":
        return <Zap className="w-3 h-3 text-green-500" />
      case "medium":
        return <Clock className="w-3 h-3 text-yellow-500" />
      case "slow":
        return <Clock className="w-3 h-3 text-red-500" />
      default:
        return null
    }
  }

  const getCostColor = (cost: string) => {
    switch (cost) {
      case "low":
        return "text-green-600"
      case "medium":
        return "text-yellow-600"
      case "high":
        return "text-red-600"
      default:
        return "text-gray-600"
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Bot className="w-5 h-5" />
            Model Selection
          </CardTitle>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={selectAll}>
              Select All
            </Button>
            <Button variant="outline" size="sm" onClick={clearAll}>
              Clear All
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {availableModels.map((model) => (
            <div
              key={model.id}
              className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                selectedModels.includes(model.id)
                  ? "border-primary bg-primary/5"
                  : "border-border hover:border-primary/50"
              }`}
              onClick={() => handleModelToggle(model.id)}
            >
              <div className="flex items-start gap-3">
                <Checkbox
                  checked={selectedModels.includes(model.id)}
                  onChange={() => handleModelToggle(model.id)}
                  className="mt-1"
                />
                <div className="flex-1 space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium">{model.name}</h4>
                      <p className="text-sm text-muted-foreground">{model.provider}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      {getSpeedIcon(model.speed)}
                      <DollarSign className={`w-3 h-3 ${getCostColor(model.cost)}`} />
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground">{model.description}</p>
                  <div className="flex flex-wrap gap-1">
                    {model.capabilities.map((capability) => (
                      <Badge key={capability} variant="secondary" className="text-xs">
                        {capability}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {selectedModels.length > 0 && (
          <div className="mt-4 p-3 bg-muted rounded-lg">
            <p className="text-sm font-medium mb-2">Selected Models ({selectedModels.length})</p>
            <div className="flex flex-wrap gap-2">
              {selectedModels.map((modelId) => {
                const model = availableModels.find((m) => m.id === modelId)
                return (
                  <Badge key={modelId} variant="default">
                    {model?.name}
                  </Badge>
                )
              })}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
