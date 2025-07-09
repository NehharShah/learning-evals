import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

import { SecurityFlag } from "./security-flag"
import { ScoreBars } from "./score-bars"
import { DiffModal } from "./diff-modal"

interface ResultsTableProps {
  results: any[] // Replace 'any' with a more specific type if possible
}

export function ResultsTable({ results }: ResultsTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-[300px]">Prompt</TableHead>
          <TableHead className="w-[250px]">Model Response</TableHead>
          <TableHead className="w-[250px]">Expected Output</TableHead>
          <TableHead className="w-[200px]">Scores</TableHead>
          <TableHead className="w-[50px]">Info</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {results.map((result) => (
          <TableRow key={result.id}>
            <TableCell>
              <div className="flex items-start">
                <span className="text-sm">
                  {result.prompt.length > 100 ? `${result.prompt.substring(0, 100)}...` : result.prompt}
                </span>
                <SecurityFlag prompt={result.prompt} />
              </div>
            </TableCell>
            <TableCell>
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {result.modelResponse.length > 100
                  ? `${result.modelResponse.substring(0, 100)}...`
                  : result.modelResponse}
              </span>
            </TableCell>
            <TableCell>
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {result.expectedOutput.length > 100
                  ? `${result.expectedOutput.substring(0, 100)}...`
                  : result.expectedOutput}
              </span>
            </TableCell>
            <TableCell>
              <ScoreBars exactMatch={result.exactMatch} fuzzyMatch={result.fuzzyMatch} toxicity={result.toxicity} />
            </TableCell>
            <TableCell>
              <DiffModal
                modelResponse={result.modelResponse}
                expectedOutput={result.expectedOutput}
                score={Math.max(result.exactMatch, result.fuzzyMatch)}
              />
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
