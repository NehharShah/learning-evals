"use client"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { ModelInfo } from "@/types/models"
import { 
  Brain, 
  Zap, 
  Shield, 
  Clock, 
  Hash,
  CheckCircle,
  XCircle
} from "lucide-react"

interface ProviderInfoProps {
  model: ModelInfo
  isSelected?: boolean
  onSelect?: (model: ModelInfo) => void
}

export function ProviderInfo({ model, isSelected = false, onSelect }: ProviderInfoProps) {
  const getProviderIcon = (provider: string) => {
    switch (provider.toLowerCase()) {
      case "openai":
        return <Brain className="h-4 w-4" />
      case "anthropic":
        return <Shield className="h-4 w-4" />
      case "google":
        return <Zap className="h-4 w-4" />
      case "groq":
        return <Clock className="h-4 w-4" />
      default:
        return <Hash className="h-4 w-4" />
    }
  }

  const getProviderColor = (provider: string) => {
    switch (provider.toLowerCase()) {
      case "openai":
        return "bg-green-100 text-green-800 border-green-200"
      case "anthropic":
        return "bg-blue-100 text-blue-800 border-blue-200"
      case "google":
        return "bg-purple-100 text-purple-800 border-purple-200"
      case "groq":
        return "bg-orange-100 text-orange-800 border-orange-200"
      default:
        return "bg-gray-100 text-gray-800 border-gray-200"
    }
  }

  return (
    <Card 
      className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
        isSelected ? "ring-2 ring-blue-500 bg-blue-50" : ""
      }`}
      onClick={() => onSelect?.(model)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getProviderIcon(model.provider)}
            <CardTitle className="text-lg">{model.name}</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <Badge className={getProviderColor(model.provider)}>
              {model.provider}
            </Badge>
            {model.is_available ? (
              <CheckCircle className="h-4 w-4 text-green-500" />
            ) : (
              <XCircle className="h-4 w-4 text-red-500" />
            )}
          </div>
        </div>
        <CardDescription className="text-sm text-gray-600">
          {model.description}
        </CardDescription>
      </CardHeader>
      
      <CardContent className="pt-0">
        <div className="space-y-3">
          {/* Model Specifications */}
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="flex items-center gap-1">
              <Hash className="h-3 w-3 text-gray-500" />
              <span className="text-gray-600">Max Tokens:</span>
              <span className="font-medium">{model.max_tokens.toLocaleString()}</span>
            </div>
            {model.context_length && (
              <div className="flex items-center gap-1">
                <Brain className="h-3 w-3 text-gray-500" />
                <span className="text-gray-600">Context:</span>
                <span className="font-medium">{model.context_length.toLocaleString()}</span>
              </div>
            )}
          </div>

          {/* Capabilities */}
          {model.capabilities && model.capabilities.length > 0 && (
            <>
              <Separator />
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Capabilities</h4>
                <div className="flex flex-wrap gap-1">
                  {model.capabilities.map((capability, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {capability}
                    </Badge>
                  ))}
                </div>
              </div>
            </>
          )}

          {/* Model ID */}
          <Separator />
          <div className="text-xs text-gray-500 font-mono bg-gray-50 p-2 rounded">
            {model.id}
          </div>
        </div>
      </CardContent>
    </Card>
  )
} 