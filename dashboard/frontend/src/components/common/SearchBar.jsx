import {Search} from 'lucide-react'
const SearchBar = ({value,onChange}) => {
  return (
    <div className="relative w-full max-w-md">
      <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search by service, action or incident ID"
        className="w-full rounded-lg border border-slate-800 bg-slate-900 py-2.5 pl-10 pr-4 text-sm text-white placeholder-slate-500 outline-none transition-colors focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
      />
    </div>
  )
}

export default SearchBar
