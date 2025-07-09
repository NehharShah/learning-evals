"use client"

import { useState } from "react"
import { Info } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"

interface DiffModalProps {
  modelResponse: string
  expectedOutput: string
  score: number
}

export function DiffModal({ modelResponse, expectedOutput, score }: DiffModalProps) {
  const [open, setOpen] = useState(false)

  // Simple token-level diff (in a real app, you'd use a proper diff library)
  const generateDiff = () => {
    const modelTokens = modelResponse.split(" ")
    const expectedTokens = expectedOutput.split(" ")
    const maxLength = Math.max(modelTokens.length, expectedTokens.length)

    const diff = []
    for (let i = 0; i < maxLength; i++) {
      const modelToken = modelTokens[i] || ""
      const expectedToken = expectedTokens[i] || ""

      if (modelToken === expectedToken) {
        diff.push({ token: modelToken, type: "match" })
      } else if (modelToken && expectedToken) {
        diff.push({ token: modelToken, type: "mismatch", expected: expectedToken })
      } else if (modelToken) {
        diff.push({ token: modelToken, type: "extra" })
      } else {
        diff.push({ token: expectedToken, type: "missing" })
      }
    }
    return diff
  }

  if (score >= 70) return null

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
          <Info className="h-3 w-3" />
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Token-Level Diff Analysis</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="font-semibold mb-2">Model Response:</h4>
              <p className="text-sm bg-gray-50 dark:bg-gray-800 p-3 rounded">{modelResponse}</p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Expected Output:</h4>
              <p className="text-sm bg-gray-50 dark:bg-gray-800 p-3 rounded">{expectedOutput}</p>
            </div>
          </div>
          <div>
            <h4 className="font-semibold mb-2">Token Diff:</h4>
            <div className="text-sm bg-gray-50 dark:bg-gray-800 p-3 rounded space-x-1">
              {generateDiff().map((item, index) => (
                <span
                  key={index}
                  className={`px-1 rounded ${
                    item.type === "match"
                      ? "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200"
                      : item.type === "mismatch"
                        ? "bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200"
                        : item.type === "extra"
                          ? "bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200"
                          : "bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200"
                  }`}
                  title={item.type === "mismatch" ? `Expected: ${item.expected}` : item.type}
                >
                  {item.token}
                </span>
              ))}
            </div>
            <div className="mt-2 text-xs text-gray-600 dark:text-gray-400">
              <span className="inline-block w-3 h-3 bg-green-100 dark:bg-green-900 rounded mr-1"></span>Match
              <span className="inline-block w-3 h-3 bg-red-100 dark:bg-red-900 rounded mr-1 ml-3"></span>Mismatch
              <span className="inline-block w-3 h-3 bg-blue-100 dark:bg-blue-900 rounded mr-1 ml-3"></span>Extra
              <span className="inline-block w-3 h-3 bg-yellow-100 dark:bg-yellow-900 rounded mr-1 ml-3"></span>Missing
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
