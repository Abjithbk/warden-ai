const FilterTabs = ({ tabs, activeTab, onTabChange }) => {
  return (
    <div className="flex items-center gap-2 mb-6">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.key;
        return (
          <button
            key={tab.key}
            type="button"
            onClick={() => onTabChange(tab.key)}
            className={`px-4 py-1.5 rounded-full text-xs font-medium transition-all duration-200 cursor-pointer ${isActive
                ? 'bg-slate-700 text-white shadow-sm'
                : 'bg-transparent text-slate-400 border border-slate-700/50 hover:text-white hover:border-slate-600'
              }`}
          >
            {tab.label}
            {tab.count != null && (
              <span className={`ml-1.5 ${isActive ? 'text-white' : 'text-slate-500'}`}>
                ({tab.count})
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
};

export default FilterTabs;
