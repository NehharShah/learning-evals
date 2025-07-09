interface ScoreBarProps {
  score: number
  className?: string
}

export function ScoreBar({ score, className = "" }: ScoreBarProps) {
  const getColor = (score: number) => {
    if (score >= 0.8) return "bg-green-500"
    if (score >= 0.6) return "bg-yellow-500"
    return "bg-red-500"
  }

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div className={`h-full transition-all duration-300 ${getColor(score)}`} style={{ width: `${score * 100}%` }} />
      </div>
      <span className="text-sm font-medium text-gray-600 min-w-[3rem]">{(score * 100).toFixed(0)}%</span>
    </div>
  )
}
