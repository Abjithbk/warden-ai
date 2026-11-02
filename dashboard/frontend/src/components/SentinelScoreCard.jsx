function SentinelScoreCard({ score, maxScore = 100, loading = false }) {
  const radius = 50
  const circumference = 2 * Math.PI * radius
  const progress = loading || score == null ? 0 : score / maxScore
  const offset = circumference - progress * circumference

  return (
    <div className="flex w-full flex-col gap-3 rounded-xl border border-gray-800 bg-slate-900 p-5 lg:w-48">
      <p className="text-xs tracking-wide text-gray-400">SENTINEL SCORE</p>
      <div className="relative flex justify-center">
        <svg width="120" height="120" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r={radius} fill="none" stroke="#1f2937" strokeWidth="10" />
          <circle
            cx="60"
            cy="60"
            r={radius}
            fill="none"
            stroke="#34d399"
            strokeWidth="10"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            transform="rotate(-90 60 60)"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <p className="text-2xl font-bold text-white">{loading || score == null ? '—' : score}</p>
          <p className="text-xs text-gray-500">/ {maxScore}</p>
        </div>
      </div>
    </div>
  )
}

export default SentinelScoreCard