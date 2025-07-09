"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Upload, FileText, CheckCircle, AlertCircle, X } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface DatasetUploadProps {
  onDatasetUpload: (data: any[]) => void
}

export function DatasetUpload({ onDatasetUpload }: DatasetUploadProps) {
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [previewData, setPreviewData] = useState<any[] | null>(null)
  const [isDragActive, setIsDragActive] = useState(false)

  const parseCSV = (text: string) => {
    const lines = text.split("\n").filter((line) => line.trim())
    if (lines.length === 0) return []

    const headers = lines[0].split(",").map((h) => h.trim().replace(/"/g, ""))

    return lines.slice(1).map((line) => {
      const values = line.split(",").map((v) => v.trim().replace(/"/g, ""))
      const obj: any = {}
      headers.forEach((header, index) => {
        obj[header] = values[index] || ""
      })
      return obj
    })
  }

  const parseJSONL = (text: string) => {
    return text
      .split("\n")
      .filter((line) => line.trim())
      .map((line) => JSON.parse(line))
  }

  const processFile = async (file: File) => {
    setIsUploading(true)
    setError(null)
    setUploadProgress(0)

    try {
      const text = await file.text()
      let data: any[]

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => Math.min(prev + 10, 90))
      }, 100)

      if (file.name.endsWith(".csv")) {
        data = parseCSV(text)
      } else if (file.name.endsWith(".jsonl")) {
        data = parseJSONL(text)
      } else {
        throw new Error("Unsupported file format. Please upload CSV or JSONL files.")
      }

      // Validate required columns
      if (data.length === 0) {
        throw new Error("File is empty or could not be parsed.")
      }

      const firstRow = data[0]
      if (!firstRow.prompt && !firstRow.question) {
        throw new Error('Dataset must contain a "prompt" or "question" column.')
      }

      if (!firstRow.expected_output && !firstRow.expected && !firstRow.answer) {
        throw new Error('Dataset must contain an "expected_output", "expected", or "answer" column.')
      }

      clearInterval(progressInterval)
      setUploadProgress(100)

      // Normalize column names
      const normalizedData = data.map((row) => ({
        prompt: row.prompt || row.question || "",
        expected_output: row.expected_output || row.expected || row.answer || "",
        ...row,
      }))

      setPreviewData(normalizedData.slice(0, 5)) // Show first 5 rows
      setUploadedFile(file)
      onDatasetUpload(normalizedData)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to process file")
      setUploadProgress(0)
    } finally {
      setIsUploading(false)
    }
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (files && files.length > 0) {
      processFile(files[0])
    }
  }

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault()
    setIsDragActive(false)

    const files = event.dataTransfer.files
    if (files && files.length > 0) {
      processFile(files[0])
    }
  }

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault()
    setIsDragActive(true)
  }

  const handleDragLeave = (event: React.DragEvent) => {
    event.preventDefault()
    setIsDragActive(false)
  }

  const clearUpload = () => {
    setUploadedFile(null)
    setPreviewData(null)
    setError(null)
    setUploadProgress(0)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="w-5 h-5" />
          Dataset Upload
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {!uploadedFile ? (
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50"
            }`}
            data-upload-area
            tabIndex={0}
          >
            <input type="file" accept=".csv,.jsonl" onChange={handleFileSelect} className="hidden" id="file-upload" />
            <Upload className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
            {isDragActive ? (
              <p className="text-lg">Drop your dataset here...</p>
            ) : (
              <div>
                <p className="text-lg mb-2">Drag & drop your dataset here</p>
                <p className="text-sm text-muted-foreground mb-4">or click to browse files</p>
                <Button variant="outline" onClick={() => document.getElementById("file-upload")?.click()}>
                  Choose File
                </Button>
              </div>
            )}
            <div className="mt-4 flex justify-center gap-2">
              <Badge variant="secondary">.CSV</Badge>
              <Badge variant="secondary">.JSONL</Badge>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <div>
                  <p className="font-medium">{uploadedFile.name}</p>
                  <p className="text-sm text-muted-foreground">{(uploadedFile.size / 1024).toFixed(1)} KB</p>
                </div>
              </div>
              <Button variant="ghost" size="sm" onClick={clearUpload}>
                <X className="w-4 h-4" />
              </Button>
            </div>

            {previewData && (
              <div>
                <h4 className="font-medium mb-2">Data Preview (First 5 rows)</h4>
                <div className="border rounded-lg overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-muted">
                        <tr>
                          <th className="p-2 text-left">Prompt</th>
                          <th className="p-2 text-left">Expected Output</th>
                        </tr>
                      </thead>
                      <tbody>
                        {previewData.map((row, index) => (
                          <tr key={index} className="border-t">
                            <td className="p-2 max-w-xs truncate">{row.prompt}</td>
                            <td className="p-2 max-w-xs truncate">{row.expected_output}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {isUploading && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              <span className="text-sm">Processing file...</span>
            </div>
            <Progress value={uploadProgress} className="w-full" />
          </div>
        )}

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  )
}
