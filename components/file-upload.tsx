"use client"

import type React from "react"

import { Upload, FileText } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

interface FileUploadProps {
  onFileSelect: (file: File) => void
  selectedFile: File | null
}

export function FileUpload({ onFileSelect, selectedFile }: FileUploadProps) {
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      onFileSelect(file)
    }
  }

  return (
    <Card className="border-2 border-dashed border-gray-300 hover:border-gray-400 transition-colors">
      <div className="p-8 text-center">
        <input type="file" accept=".csv,.jsonl" onChange={handleFileChange} className="hidden" id="file-upload" />
        <label htmlFor="file-upload" className="cursor-pointer">
          <div className="flex flex-col items-center gap-4">
            <div className="p-4 bg-gray-50 rounded-full">
              <Upload className="w-8 h-8 text-gray-400" />
            </div>
            <div>
              <p className="text-lg font-medium text-gray-900">Upload Dataset</p>
              <p className="text-sm text-gray-500 mt-1">CSV or JSONL files with prompt and expected_output fields</p>
            </div>
            <Button variant="outline" type="button">
              Choose File
            </Button>
          </div>
        </label>

        {selectedFile && (
          <div className="mt-4 p-3 bg-blue-50 rounded-lg flex items-center gap-2">
            <FileText className="w-4 h-4 text-blue-600" />
            <span className="text-sm text-blue-800 font-medium">{selectedFile.name}</span>
          </div>
        )}
      </div>
    </Card>
  )
}
