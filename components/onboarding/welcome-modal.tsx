"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Upload, Bot, BarChart3, Shield, Play, Download, ChevronRight, ChevronLeft } from "lucide-react"

interface WelcomeModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const steps = [
  {
    title: "Welcome to LLM Evaluation Tool",
    description: "A comprehensive platform for evaluating and comparing language model performance",
    icon: <BarChart3 className="w-8 h-8 text-blue-500" />,
    content:
      "Get started by uploading your dataset and selecting models to evaluate. This tool helps you analyze model performance, detect security issues, and compare results across different LLMs.",
  },
  {
    title: "Upload Your Dataset",
    description: "Drag and drop CSV or JSONL files",
    icon: <Upload className="w-8 h-8 text-green-500" />,
    content:
      "Your dataset should contain 'prompt' and 'expected_output' columns. Supported formats: CSV and JSONL. Files are processed locally for privacy.",
  },
  {
    title: "Select Models",
    description: "Choose one or multiple LLMs to evaluate",
    icon: <Bot className="w-8 h-8 text-purple-500" />,
    content:
      "Select from popular models like GPT-4, Claude, Gemini, and more. You can compare multiple models side-by-side to see performance differences.",
  },
  {
    title: "Security & Safety",
    description: "Monitor for prompt injection and toxicity",
    icon: <Shield className="w-8 h-8 text-red-500" />,
    content:
      "The tool automatically detects potential security risks, prompt injection attempts, and toxic content to help you maintain safe AI deployments.",
  },
  {
    title: "Live Playground",
    description: "Test prompts in real-time",
    icon: <Play className="w-8 h-8 text-orange-500" />,
    content:
      "Use the live playground to test individual prompts, adjust model parameters, and immediately see results added to your evaluation table.",
  },
  {
    title: "Export & Share",
    description: "Export results and share insights",
    icon: <Download className="w-8 h-8 text-indigo-500" />,
    content:
      "Export your evaluation results as CSV or PDF reports. Generate shareable links to collaborate with your team on model performance insights.",
  },
]

export function WelcomeModal({ open, onOpenChange }: WelcomeModalProps) {
  const [currentStep, setCurrentStep] = useState(0)

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleComplete = () => {
    localStorage.setItem("llm-eval-onboarding-completed", "true")
    onOpenChange(false)
  }

  const currentStepData = steps[currentStep]

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {currentStepData.icon}
            {currentStepData.title}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">{currentStepData.description}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">{currentStepData.content}</p>
            </CardContent>
          </Card>

          {/* Progress indicator */}
          <div className="flex justify-center space-x-2">
            {steps.map((_, index) => (
              <div
                key={index}
                className={`w-2 h-2 rounded-full ${index === currentStep ? "bg-primary" : "bg-muted"}`}
              />
            ))}
          </div>

          {/* Navigation */}
          <div className="flex justify-between">
            <Button variant="outline" onClick={prevStep} disabled={currentStep === 0}>
              <ChevronLeft className="w-4 h-4 mr-2" />
              Previous
            </Button>

            {currentStep === steps.length - 1 ? (
              <Button onClick={handleComplete}>Get Started</Button>
            ) : (
              <Button onClick={nextStep}>
                Next
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
