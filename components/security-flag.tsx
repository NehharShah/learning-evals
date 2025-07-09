"use client"

import { AlertTriangle } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface SecurityFlagProps {
  prompt: string
}

const SUSPICIOUS_PATTERNS = [
  /ignore\s+previous/i,
  /disregard\s+instructions/i,
  /act\s+as/i,
  /pretend\s+to\s+be/i,
  /forget\s+everything/i,
  /system\s+prompt/i,
  /jailbreak/i,
  /override/i,
]

export function SecurityFlag({ prompt }: SecurityFlagProps) {
  const isSuspicious = SUSPICIOUS_PATTERNS.some((pattern) => pattern.test(prompt))

  if (!isSuspicious) return null

  return (
    <Badge variant="destructive" className="ml-2 text-xs">
      <AlertTriangle className="w-3 h-3 mr-1" />
      Security Risk
    </Badge>
  )
}
