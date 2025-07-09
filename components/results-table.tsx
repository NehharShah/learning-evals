import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { ScoreBar } from "./score-bar"

interface EvaluationResult {
  prompt: string
  modelResponse: string
  expected: string
  score: number
}

interface ResultsTableProps {
  results: EvaluationResult[]
}

export function ResultsTable({ results }: ResultsTableProps) {
  if (results.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <p className="text-gray-500">No results yet. Upload a dataset and run evaluation to see results.</p>
        </CardContent>
      </Card>
    )
  }

  const averageScore = results.reduce((sum, result) => sum + result.score, 0) / results.length

  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold">Evaluation Results</CardTitle>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">Average Score:</span>
            <ScoreBar score={averageScore} />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-1/4">Prompt</TableHead>
                <TableHead className="w-1/4">Model Response</TableHead>
                <TableHead className="w-1/4">Expected</TableHead>
                <TableHead className="w-1/4">Score</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {results.map((result, index) => (
                <TableRow key={index}>
                  <TableCell className="font-medium">
                    <div className="max-w-xs truncate" title={result.prompt}>
                      {result.prompt}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="max-w-xs truncate" title={result.modelResponse}>
                      {result.modelResponse}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="max-w-xs truncate" title={result.expected}>
                      {result.expected}
                    </div>
                  </TableCell>
                  <TableCell>
                    <ScoreBar score={result.score} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}
