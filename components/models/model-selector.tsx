"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ProviderInfo } from "./provider-info"
import { ModelInfo, Provider } from "@/types/models"
import { Search, Filter, Grid, List } from "lucide-react"

interface ModelSelectorProps {
  onModelSelect: (model: ModelInfo) => void
  selectedModel?: ModelInfo
  className?: string
}

export function ModelSelector({ onModelSelect, selectedModel, className }: ModelSelectorProps) {
  const [models, setModels] = useState<ModelInfo[]>([])
  const [providers, setProviders] = useState<Provider[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedProvider, setSelectedProvider] = useState<string>("all")
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid")

  useEffect(() => {
    fetchModels()
  }, [])

  const fetchModels = async () => {
    try {
      setLoading(true)
      const response = await fetch("/api/v1/models")
      if (!response.ok) {
        throw new Error("Failed to fetch models")
      }
      const modelData: ModelInfo[] = await response.json()
      setModels(modelData)
      
      // Group models by provider
      const providerMap = new Map<string, ModelInfo[]>()
      modelData.forEach(model => {
        if (!providerMap.has(model.provider)) {
          providerMap.set(model.provider, [])
        }
        providerMap.get(model.provider)!.push(model)
      })
      
      const providerList: Provider[] = Array.from(providerMap.entries()).map(([name, models]) => ({
        name,
        models,
        is_configured: true, // This would be determined by backend
        api_key_configured: true // This would be determined by backend
      }))
      
      setProviders(providerList)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch models")
    } finally {
      setLoading(false)
    }
  }

  const filteredModels = models.filter(model => {
    const matchesSearch = model.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         model.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         model.provider.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesProvider = selectedProvider === "all" || model.provider === selectedProvider
    
    return matchesSearch && matchesProvider
  })

  const getProviderStats = () => {
    const totalModels = models.length
    const availableModels = models.filter(m => m.is_available).length
    const configuredProviders = providers.filter(p => p.is_configured).length
    
    return { totalModels, availableModels, configuredProviders }
  }

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Loading Models...</CardTitle>
          <CardDescription>Fetching available models from all providers</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="text-red-600">Error Loading Models</CardTitle>
          <CardDescription>{error}</CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={fetchModels} variant="outline">
            Retry
          </Button>
        </CardContent>
      </Card>
    )
  }

  const stats = getProviderStats()

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Select Model</CardTitle>
            <CardDescription>
              Choose from {stats.availableModels} available models across {stats.configuredProviders} providers
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant={viewMode === "grid" ? "default" : "outline"}
              size="sm"
              onClick={() => setViewMode("grid")}
            >
              <Grid className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === "list" ? "default" : "outline"}
              size="sm"
              onClick={() => setViewMode("list")}
            >
              <List className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Search and Filter */}
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search models..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select value={selectedProvider} onValueChange={setSelectedProvider}>
            <SelectTrigger className="w-48">
              <Filter className="h-4 w-4 mr-2" />
              <SelectValue placeholder="All Providers" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Providers</SelectItem>
              {providers.map(provider => (
                <SelectItem key={provider.name} value={provider.name}>
                  {provider.name} ({provider.models.length})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Provider Stats */}
        <div className="flex gap-4 text-sm">
          <Badge variant="outline">
            {stats.totalModels} Total Models
          </Badge>
          <Badge variant="outline">
            {stats.availableModels} Available
          </Badge>
          <Badge variant="outline">
            {stats.configuredProviders} Providers
          </Badge>
        </div>

        {/* Models Display */}
        <Tabs defaultValue="all" className="w-full">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="all">All</TabsTrigger>
            {providers.map(provider => (
              <TabsTrigger key={provider.name} value={provider.name}>
                {provider.name}
              </TabsTrigger>
            ))}
          </TabsList>
          
          <TabsContent value="all" className="mt-4">
            {filteredModels.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No models found matching your criteria
              </div>
            ) : (
              <div className={viewMode === "grid" ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" : "space-y-2"}>
                {filteredModels.map(model => (
                  <ProviderInfo
                    key={model.id}
                    model={model}
                    isSelected={selectedModel?.id === model.id}
                    onSelect={onModelSelect}
                  />
                ))}
              </div>
            )}
          </TabsContent>
          
          {providers.map(provider => (
            <TabsContent key={provider.name} value={provider.name} className="mt-4">
              <div className={viewMode === "grid" ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" : "space-y-2"}>
                {provider.models
                  .filter(model => 
                    model.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    model.description?.toLowerCase().includes(searchTerm.toLowerCase())
                  )
                  .map(model => (
                    <ProviderInfo
                      key={model.id}
                      model={model}
                      isSelected={selectedModel?.id === model.id}
                      onSelect={onModelSelect}
                    />
                  ))}
              </div>
            </TabsContent>
          ))}
        </Tabs>
      </CardContent>
    </Card>
  )
}
