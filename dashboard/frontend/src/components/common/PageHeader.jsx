import { useState, useEffect } from 'react';

const PageHeader = ({ title, subtitle }) => {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex items-start justify-between mb-6">
      <div>
        <h1 className="text-2xl font-bold text-white">{title}</h1>
        {subtitle && (
          <p className="text-sm text-slate-400 mt-1">{subtitle}</p>
        )}
      </div>
      <span className="text-sm text-slate-500 font-mono tabular-nums">
        {currentTime.toLocaleTimeString('en-GB')}
      </span>
    </div>
  );
};

export default PageHeader;
