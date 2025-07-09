"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { toast } from "@/hooks/use-toast"
import { Download, Share2, FileText, Copy, Mail, Link, CheckCircle, Settings } from "lucide-react"

interface ExportShareProps {
  data: any[]
  summary: {
    totalPrompts: number
    averageExactMatch: number
    averageFuzzyMatch: number
    flaggedPrompts: number
  }
}

export function ExportShare({ data, summary }: ExportShareProps) {
  const [shareUrl, setShareUrl] = useState("")
  const [isGeneratingShare, setIsGeneratingShare] = useState(false)
  const [exportFormat, setExportFormat] = useState("csv")
  const [includeParameters, setIncludeParameters] = useState(true)
  const [includeTimestamps, setIncludeTimestamps] = useState(true)

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
      ...(includeTimestamps ? ["Timestamp"] : []),
      ...(includeParameters ? ["Temperature", "Max Tokens", "Top P", "Frequency Penalty"] : []),
    ]

    const csvContent = [
      headers.join(","),
      ...data.map((row) => {
        const baseRow = [
          `"${row.prompt.replace(/"/g, '""')}"`,
          `"${row.modelResponse.replace(/"/g, '""')}"`,
          `"${row.expectedOutput.replace(/"/g, '""')}"`,
          row.exactMatch,
          row.fuzzyMatch,
          row.toxicity ? "Yes" : "No",
          row.model || "Unknown",
        ]

        if (includeTimestamps) {
          baseRow.push(row.timestamp || "")
        }

        if (includeParameters && row.parameters) {
          baseRow.push(
            row.parameters.temperature || "",
            row.parameters.maxTokens || "",
            row.parameters.topP || "",
            row.parameters.frequencyPenalty || "",
          )
        }

        return baseRow.join(",")
      }),
    ].join("\n")

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
    const link = document.createElement("a")
    const url = URL.createObjectURL(blob)
    link.setAttribute("href", url)
    link.setAttribute("download", `llm-evaluation-results-${new Date().toISOString().split("T")[0]}.csv`)
    link.style.visibility = "hidden"
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    toast({
      title: "Export Successful",
      description: "CSV file has been downloaded",
    })
  }

  const exportToPDF = async () => {
    // In a real implementation, you'd use a library like jsPDF or Puppeteer
    toast({
      title: "PDF Export",
      description: "PDF export functionality would be implemented here",
    })
  }

  const generateShareableLink = async () => {
    setIsGeneratingShare(true)

    try {
      // Simulate API call to generate shareable link
      await new Promise((resolve) => setTimeout(resolve, 1500))

      // In a real implementation, you'd send the data to your backend
      // and get back a unique share ID
      const shareId = Math.random().toString(36).substring(2, 15)
      const url = `${window.location.origin}/shared/${shareId}`
      setShareUrl(url)

      toast({
        title: "Share Link Generated",
        description: "Your evaluation results can now be shared",
      })
    } catch (error) {
      toast({
        title: "Error Generating Link",
        description: "Failed to create shareable link. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsGeneratingShare(false)
    }
  }

  const copyShareLink = async () => {
    if (!shareUrl) return

    try {
      await navigator.clipboard.writeText(shareUrl)
      toast({
        title: "Link Copied",
        description: "Share link has been copied to clipboard",
      })
    } catch (error) {
      toast({
        title: "Copy Failed",
        description: "Please copy the link manually",
        variant: "destructive",
      })
    }
  }

  const shareViaEmail = () => {
    const subject = encodeURIComponent("LLM Evaluation Results")
    const body = encodeURIComponent(
      `Check out these LLM evaluation results:\n\n${shareUrl}\n\nSummary:\n- Total Prompts: ${summary.totalPrompts}\n- Average Exact Match: ${summary.averageExactMatch.toFixed(1)}%\n- Average Fuzzy Match: ${summary.averageFuzzyMatch.toFixed(1)}%\n- Flagged Prompts: ${summary.flaggedPrompts}`,
    )

    window.open(`mailto:?subject=${subject}&body=${body}`)
  }

  return (
    <div className="flex flex-wrap gap-2">
      {/* Export Dropdown */}
      <Dialog>
        <DialogTrigger asChild>
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </DialogTrigger>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Download className="w-5 h-5" />
              Export Results
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Export Format</Label>
              <Select value={exportFormat} onValueChange={setExportFormat}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="csv">CSV File</SelectItem>
                  <SelectItem value="pdf">PDF Report</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-3">
              <Label>Include Options</Label>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="timestamps"
                    checked={includeTimestamps}
                    onChange={(e) => setIncludeTimestamps(e.target.checked)}
                    className="rounded"
                  />
                  <Label htmlFor="timestamps" className="text-sm">
                    Timestamps
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="parameters"
                    checked={includeParameters}
                    onChange={(e) => setIncludeParameters(e.target.checked)}
                    className="rounded"
                  />
                  <Label htmlFor="parameters" className="text-sm">
                    Model Parameters
                  </Label>
                </div>
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={exportFormat === "csv" ? exportToCSV : exportToPDF}
                className="flex-1"
                disabled={!data.length}
              >
                <FileText className="w-4 h-4 mr-2" />
                Export {exportFormat.toUpperCase()}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Share Dropdown */}
      <Dialog>
        <DialogTrigger asChild>
          <Button variant="outline" size="sm">
            <Share2 className="w-4 h-4 mr-2" />
            Share
          </Button>
        </DialogTrigger>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Share2 className="w-5 h-5" />
              Share Results
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {!shareUrl ? (
              <div className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  Generate a shareable link to collaborate with your team on these evaluation results.
                </p>
                <Button onClick={generateShareableLink} disabled={isGeneratingShare || !data.length} className="w-full">
                  {isGeneratingShare ? (
                    <>
                      <Settings className="w-4 h-4 mr-2 animate-spin" />
                      Generating Link...
                    </>
                  ) : (
                    <>
                      <Link className="w-4 h-4 mr-2" />
                      Generate Share Link
                    </>
                  )}
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-green-600">
                  <CheckCircle className="w-4 h-4" />
                  <span className="text-sm font-medium">Link Generated</span>
                </div>

                <div className="space-y-2">
                  <Label>Shareable Link</Label>
                  <div className="flex gap-2">
                    <Input value={shareUrl} readOnly className="text-xs" />
                    <Button size="sm" onClick={copyShareLink}>
                      <Copy className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                <Separator />

                <div className="space-y-2">
                  <Label>Quick Share</Label>
                  <Button variant="outline" size="sm" onClick={shareViaEmail} className="w-full bg-transparent">
                    <Mail className="w-4 h-4 mr-2" />
                    Share via Email
                  </Button>
                </div>

                <div className="p-3 bg-muted rounded-lg">
                  <p className="text-xs text-muted-foreground">
                    This link will remain active for 30 days and can be accessed by anyone with the URL.
                  </p>
                </div>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
