function SentinelScoreCard({ score, maxScore, nodesLabel, podsLabel }) {
  const radius = 50
  const circumference = 2 * Math.PI * radius
  const progress = score / maxScore
  const offset = circumference - progress * circumference

  return (
    <div className="bg-[#0d1017] border border-gray-800 rounded-xl p-5 flex flex-col justify-between">
      <p className="text-gray-400 text-xs tracking-wide">SENTINEL SCORE</p>
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
          <p className="text-white text-2xl font-bold">{score}</p>
          <p className="text-gray-500 text-xs">/ {maxScore}</p>
        </div>
      </div>
      <div className="flex justify-center gap-4 text-xs text-gray-400 whitespace-nowrap">
        <span className="flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          {nodesLabel}
        </span>
        <span className="flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
          {podsLabel}
        </span>
      </div>
    </div>
  )
}

export default SentinelScoreCard