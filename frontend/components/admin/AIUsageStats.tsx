import React from 'react';

interface CategoryData {
  category_id: string;
  category_name: string;
  count: number;
}

interface AIUsageStatsProps {
  stats: {
    total_generations: number;
    successful: number;
    failed: number;
    avg_generation_time_ms: number;
    cache_hit_rate?: number;
    generations_by_category: CategoryData[];
  };
}

export default function AIUsageStats({ stats }: AIUsageStatsProps) {
  const {
    total_generations = 0,
    successful = 0,
    failed = 0,
    avg_generation_time_ms = 0,
    cache_hit_rate,
    generations_by_category = [],
  } = stats;

  // Calculate percentages
  const successRate = total_generations > 0 ? (successful / total_generations) * 100 : 0;
  const failureRate = total_generations > 0 ? (failed / total_generations) * 100 : 0;

  return (
    <div className="space-y-8">
      
      {/* Overview Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        
        {/* Total Generations */}
        <div className="relative overflow-hidden bg-galxy-charcoal/50 backdrop-blur-xl border border-galxy-charcoal/60 rounded-2xl p-6 transition-all duration-300 hover:-translate-y-1 hover:border-galxy-magenta/50 hover:shadow-2xl hover:shadow-galxy-magenta/5 group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-galxy-magenta/10 rounded-full blur-2xl group-hover:bg-galxy-magenta/20 transition-all duration-300" />
          <p className="text-xs font-semibold uppercase tracking-wider text-galxy-muted">Total Generations</p>
          <p className="text-4xl font-extrabold mt-3 text-galxy-primary">
            {total_generations.toLocaleString()}
          </p>
          <div className="mt-4 flex items-center space-x-2 text-xs text-galxy-muted">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-galxy-magenta animate-pulse" />
            <span>Total requests processed</span>
          </div>
        </div>

        {/* Success Rate */}
        <div className="relative overflow-hidden bg-galxy-charcoal/50 backdrop-blur-xl border border-galxy-charcoal/60 rounded-2xl p-6 transition-all duration-300 hover:-translate-y-1 hover:border-galxy-blue/50 hover:shadow-2xl hover:shadow-galxy-blue/5 group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-galxy-blue/10 rounded-full blur-2xl group-hover:bg-galxy-blue/20 transition-all duration-300" />
          <p className="text-xs font-semibold uppercase tracking-wider text-galxy-muted">Success Rate</p>
          <p className="text-4xl font-extrabold mt-3 text-galxy-blue">
            {successRate.toFixed(1)}%
          </p>
          <div className="mt-4 flex justify-between items-center text-xs text-galxy-muted">
            <span>{successful.toLocaleString()} successful</span>
            <span className="text-galxy-blue/80 font-medium">Healthy</span>
          </div>
        </div>

        {/* Average Latency */}
        <div className="relative overflow-hidden bg-galxy-charcoal/50 backdrop-blur-xl border border-galxy-charcoal/60 rounded-2xl p-6 transition-all duration-300 hover:-translate-y-1 hover:border-galxy-violet/50 hover:shadow-2xl hover:shadow-galxy-violet/5 group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-galxy-violet/10 rounded-full blur-2xl group-hover:bg-galxy-violet/20 transition-all duration-300" />
          <p className="text-xs font-semibold uppercase tracking-wider text-galxy-muted">Avg Generation Time</p>
          <p className="text-4xl font-extrabold mt-3 text-transparent bg-clip-text bg-gradient-to-r from-galxy-violet via-galxy-primary to-galxy-blue">
            {avg_generation_time_ms >= 1000 
              ? `${(avg_generation_time_ms / 1000).toFixed(2)}s` 
              : `${Math.round(avg_generation_time_ms)}ms`}
          </p>
          <div className="mt-4 flex items-center space-x-2 text-xs text-galxy-muted">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-galxy-violet" />
            <span>Response speed average</span>
          </div>
        </div>

        {/* Cache Hit Rate */}
        <div className="relative overflow-hidden bg-galxy-charcoal/50 backdrop-blur-xl border border-galxy-charcoal/60 rounded-2xl p-6 transition-all duration-300 hover:-translate-y-1 hover:border-galxy-yellow/50 hover:shadow-2xl hover:shadow-galxy-yellow/5 group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-galxy-yellow/10 rounded-full blur-2xl group-hover:bg-galxy-yellow/20 transition-all duration-300" />
          <p className="text-xs font-semibold uppercase tracking-wider text-galxy-muted">Cache Hit Rate</p>
          <p className="text-4xl font-extrabold mt-3 text-galxy-yellow">
            {cache_hit_rate !== undefined && cache_hit_rate !== null 
              ? `${(cache_hit_rate * 100).toFixed(1)}%` 
              : 'N/A'}
          </p>
          <div className="mt-4 flex items-center justify-between text-xs text-galxy-muted">
            <span>{cache_hit_rate !== undefined && cache_hit_rate !== null ? 'Cache serving active' : 'Awaiting Module 5 field'}</span>
            {cache_hit_rate === undefined && (
              <span className="px-1.5 py-0.5 rounded text-[10px] bg-galxy-charcoal text-galxy-yellow border border-galxy-charcoal/80">Blocked</span>
            )}
          </div>
        </div>

      </div>

      {/* Row details: Failures and Category Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Category Share Distribution Card */}
        <div className="lg:col-span-2 bg-galxy-charcoal/50 backdrop-blur-xl border border-galxy-charcoal/60 rounded-2xl p-6 shadow-xl">
          <h2 className="text-lg font-bold text-galxy-primary">Generations by Category</h2>
          <p className="text-xs text-galxy-muted mt-1 mb-6">Breakdown of content generation volume grouped by model categories.</p>
          
          {generations_by_category.length === 0 ? (
            <div className="text-center py-12 text-galxy-muted text-sm">
              No category distribution data available for this filter range.
            </div>
          ) : (
            <div className="space-y-5">
              {generations_by_category.map((item) => {
                const categoryPct = total_generations > 0 ? (item.count / total_generations) * 100 : 0;
                return (
                  <div key={item.category_id || item.category_name} className="group">
                    <div className="flex justify-between items-center text-sm mb-1.5">
                      <span className="font-semibold text-galxy-primary group-hover:text-galxy-magenta transition-colors duration-200">
                        {item.category_name}
                      </span>
                      <div className="space-x-2 text-xs">
                        <span className="text-galxy-muted font-medium">{item.count.toLocaleString()} calls</span>
                        <span className="text-galxy-magenta font-semibold">({categoryPct.toFixed(1)}%)</span>
                      </div>
                    </div>
                    {/* Visual Progress Bar */}
                    <div className="w-full bg-galxy-void rounded-full h-2.5 border border-galxy-charcoal/40 overflow-hidden">
                      <div 
                        className="bg-gradient-to-r from-galxy-magenta via-galxy-violet to-galxy-blue h-full rounded-full transition-all duration-500 group-hover:brightness-110" 
                        style={{ width: `${categoryPct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Health status checklist and metrics */}
        <div className="bg-galxy-charcoal/50 backdrop-blur-xl border border-galxy-charcoal/60 rounded-2xl p-6 flex flex-col justify-between shadow-xl">
          <div>
            <h2 className="text-lg font-bold text-galxy-primary">System Performance</h2>
            <p className="text-xs text-galxy-muted mt-1 mb-6">Diagnostic highlights and health summary.</p>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-galxy-charcoal/40 pb-3">
                <span className="text-sm text-galxy-muted">Total Outputs</span>
                <span className="text-sm font-semibold text-galxy-primary">{total_generations}</span>
              </div>
              <div className="flex items-center justify-between border-b border-galxy-charcoal/40 pb-3">
                <span className="text-sm text-galxy-muted">Success Rate</span>
                <span className={`text-sm font-semibold ${successRate >= 95 ? 'text-galxy-blue' : 'text-galxy-yellow'}`}>
                  {successRate.toFixed(2)}%
                </span>
              </div>
              <div className="flex items-center justify-between border-b border-galxy-charcoal/40 pb-3">
                <span className="text-sm text-galxy-muted">Failure Count</span>
                <span className={`text-sm font-semibold ${failed > 0 ? 'text-galxy-magenta' : 'text-galxy-primary'}`}>
                  {failed.toLocaleString()}
                </span>
              </div>
              <div className="flex items-center justify-between pb-3">
                <span className="text-sm text-galxy-muted">Average Duration</span>
                <span className="text-sm font-semibold text-galxy-violet">{avg_generation_time_ms.toFixed(1)} ms</span>
              </div>
            </div>
          </div>
          
          <div className="mt-8 pt-4 border-t border-galxy-charcoal/80 bg-galxy-void/40 rounded-xl p-3 border border-galxy-charcoal/60">
            <h3 className="text-xs font-bold text-galxy-muted uppercase tracking-wide">Handoff Validation Info</h3>
            <p className="text-[11px] text-galxy-muted/80 mt-1">
              Stats are compiled from collection read-replicas. Date bounds are evaluated using UTC datetime matching.
            </p>
          </div>
        </div>

      </div>

    </div>
  );
}
