function StatCard({ value, label, subtext, accentColor, subtextColor }) {
  const colorClass = accentColor === 'red' ? 'text-red-500' : accentColor === 'green' ? 'text-emerald-400' : 'text-white'
  const subColorClass = subtextColor === 'red' ? 'text-red-500' : subtextColor === 'green' ? 'text-emerald-400' : 'text-gray-500'

  return (
    <div className="bg-[#0d1017] border border-gray-800 rounded-xl p-4 flex-1">
      <p className={`text-3xl font-bold whitespace-nowrap ${colorClass}`}>
        {value}
      </p>
      <p className="text-gray-300 text-sm mt-1 whitespace-nowrap">{label}</p>
      <p className={`text-sm mt-2 whitespace-nowrap ${subColorClass}`}>
        {subtext}
      </p>
    </div>
  )
}

export default StatCard