"use client"

import { Download } from "lucide-react"
import { Button } from "@/components/ui/button"

interface ExportButtonProps {
  data: any[]
  filename?: string
}

export function ExportButton({ data, filename = "evaluation-results.csv" }: ExportButtonProps) {
  const exportToCSV = () => {
    if (!data.length) return

    const headers = [
      "Prompt",
      "Model Response",
      "Expected Output",
      "Exact Match (%)",
      "Fuzzy Match (%)",
      "Toxicity",
      "Model",
    ]
    const csvContent = [
      headers.join(","),
      ...data.map((row) =>
        [
          `"${row.prompt.replace(/"/g, '""')}"`,
          `"${row.modelResponse.replace(/"/g, '""')}"`,
          `"${row.expectedOutput.replace(/"/g, '""')}"`,
          row.exactMatch,
          row.fuzzyMatch,
          row.toxicity ? "Yes" : "No",
          row.model || "Unknown",
        ].join(","),
      ),
    ].join("\n")

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
    const link = document.createElement("a")
    const url = URL.createObjectURL(blob)
    link.setAttribute("href", url)
    link.setAttribute("download", filename)
    link.style.visibility = "hidden"
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <Button onClick={exportToCSV} variant="outline" size="sm" disabled={!data.length}>
      <Download className="w-4 h-4 mr-2" />
      Export CSV
    </Button>
  )
}
