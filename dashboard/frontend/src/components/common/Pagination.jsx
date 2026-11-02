const Pagination = ({ page, pageSize, total, onChange }) => {
    if (total <= pageSize) return null
    const from = page * pageSize + 1
    const to = Math.min((page + 1) * pageSize, total)
    const btn =
        'rounded border border-slate-700 px-3 py-1 text-slate-300 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40'
    return (
        <div className="mt-6 flex items-center justify-between text-xs text-slate-400">
            <span>
                {from}–{to} of {total}
            </span>
            <div className="flex gap-2">
                <button type="button" className={btn} disabled={page === 0} onClick={() => onChange(page - 1)}>
                    Prev
                </button>
                <button type="button" className={btn} disabled={to >= total} onClick={() => onChange(page + 1)}>
                    Next
                </button>
            </div>
        </div>
    )
}

export default Pagination