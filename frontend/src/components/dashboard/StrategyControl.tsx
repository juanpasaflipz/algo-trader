import React from 'react';
import { Button } from '../ui/button';
import { Play, Pause, Settings, TrendingUp, TrendingDown } from 'lucide-react';

interface Strategy {
  id: string;
  name: string;
  status: 'active' | 'paused' | 'stopped';
  performance: number;
  trades: number;
  description: string;
}

const strategies: Strategy[] = [
  {
    id: '1',
    name: 'EMA Crossover',
    status: 'active',
    performance: 12.5,
    trades: 45,
    description: 'Trades based on 9/21 EMA crossovers',
  },
  {
    id: '2',
    name: 'RSI Divergence',
    status: 'active',
    performance: 8.3,
    trades: 23,
    description: 'Identifies RSI divergences for entry',
  },
  {
    id: '3',
    name: 'AI Sentiment',
    status: 'paused',
    performance: -2.1,
    trades: 12,
    description: 'Uses AI to analyze market sentiment',
  },
];

export function StrategyControl() {
  const [strategyStates, setStrategyStates] = React.useState<Record<string, string>>(
    strategies.reduce((acc, s) => ({ ...acc, [s.id]: s.status }), {})
  );

  const toggleStrategy = (id: string) => {
    setStrategyStates(prev => ({
      ...prev,
      [id]: prev[id] === 'active' ? 'paused' : 'active'
    }));
  };

  return (
    <div className="space-y-4">
      {strategies.map((strategy) => (
        <div
          key={strategy.id}
          className="flex items-center justify-between rounded-lg border p-4"
        >
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold">{strategy.name}</h3>
              <span
                className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                  strategyStates[strategy.id] === 'active'
                    ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400'
                    : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400'
                }`}
              >
                {strategyStates[strategy.id]}
              </span>
            </div>
            <p className="text-sm text-muted-foreground">
              {strategy.description}
            </p>
            <div className="flex items-center gap-4 text-sm">
              <span className="flex items-center gap-1">
                {strategy.performance > 0 ? (
                  <TrendingUp className="h-4 w-4 text-green-600" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-600" />
                )}
                <span
                  className={
                    strategy.performance > 0 ? 'text-green-600' : 'text-red-600'
                  }
                >
                  {strategy.performance > 0 ? '+' : ''}
                  {strategy.performance}%
                </span>
              </span>
              <span className="text-muted-foreground">
                {strategy.trades} trades
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="icon"
              onClick={() => toggleStrategy(strategy.id)}
            >
              {strategyStates[strategy.id] === 'active' ? (
                <Pause className="h-4 w-4" />
              ) : (
                <Play className="h-4 w-4" />
              )}
            </Button>
            <Button variant="outline" size="icon">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>
      ))}
      <Button className="w-full" variant="outline">
        Add New Strategy
      </Button>
    </div>
  );
}