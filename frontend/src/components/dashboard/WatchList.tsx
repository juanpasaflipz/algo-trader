import React from 'react';
import { motion } from 'framer-motion';
import { ArrowUpRight, ArrowDownRight, MoreVertical, Star } from 'lucide-react';

const watchlistData = [
  {
    symbol: 'BTC/USDT',
    name: 'Bitcoin',
    price: 43521.32,
    change: 2.45,
    volume: '24.5B',
    sparkline: [40000, 41000, 41500, 42000, 41800, 42500, 43000, 43521],
  },
  {
    symbol: 'ETH/USDT',
    name: 'Ethereum',
    price: 2342.18,
    change: 3.12,
    volume: '12.3B',
    sparkline: [2200, 2250, 2280, 2300, 2250, 2320, 2300, 2342],
  },
  {
    symbol: 'AAPL',
    name: 'Apple Inc.',
    price: 182.52,
    change: -0.85,
    volume: '52.4M',
    sparkline: [185, 184, 183.5, 184, 183, 182.8, 183, 182.52],
  },
  {
    symbol: 'TSLA',
    name: 'Tesla Inc.',
    price: 238.45,
    change: 1.23,
    volume: '98.7M',
    sparkline: [235, 236, 237, 236.5, 237.5, 238, 237.8, 238.45],
  },
  {
    symbol: 'EUR/USD',
    name: 'Euro/US Dollar',
    price: 1.0892,
    change: -0.12,
    volume: '5.2B',
    sparkline: [1.0910, 1.0905, 1.0900, 1.0895, 1.0898, 1.0890, 1.0895, 1.0892],
  },
];

function Sparkline({ data, positive }: { data: number[]; positive: boolean }) {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min;
  
  const points = data
    .map((value, i) => {
      const x = (i / (data.length - 1)) * 60;
      const y = 20 - ((value - min) / range) * 20;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <svg width="60" height="20" className="overflow-visible">
      <polyline
        fill="none"
        stroke={positive ? '#10b981' : '#ef4444'}
        strokeWidth="1.5"
        points={points}
      />
    </svg>
  );
}

export function WatchList() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="rounded-2xl bg-white dark:bg-gray-900 p-6 shadow-sm border border-gray-200 dark:border-gray-800"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Watchlist
        </h3>
        <div className="flex items-center gap-2">
          <button className="text-sm text-violet-600 hover:text-violet-700 font-medium">
            View All
          </button>
          <button className="rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-800">
            <MoreVertical className="h-5 w-5 text-gray-500" />
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-800">
              <th className="pb-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400">
                Symbol
              </th>
              <th className="pb-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400">
                Price
              </th>
              <th className="pb-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400">
                Change
              </th>
              <th className="pb-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400">
                Volume
              </th>
              <th className="pb-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400">
                Chart
              </th>
              <th className="pb-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400">
                
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
            {watchlistData.map((item) => (
              <tr key={item.symbol} className="group hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <td className="py-4">
                  <div className="flex items-center gap-3">
                    <button className="opacity-0 group-hover:opacity-100 transition-opacity">
                      <Star className="h-4 w-4 text-gray-400 hover:text-yellow-500" />
                    </button>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">
                        {item.symbol}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {item.name}
                      </p>
                    </div>
                  </div>
                </td>
                <td className="py-4 text-right">
                  <p className="font-medium text-gray-900 dark:text-white">
                    ${item.price.toLocaleString()}
                  </p>
                </td>
                <td className="py-4 text-right">
                  <div className={`flex items-center justify-end gap-1 text-sm font-medium ${
                    item.change > 0 ? 'text-emerald-600' : 'text-red-600'
                  }`}>
                    {item.change > 0 ? (
                      <ArrowUpRight className="h-3 w-3" />
                    ) : (
                      <ArrowDownRight className="h-3 w-3" />
                    )}
                    {Math.abs(item.change)}%
                  </div>
                </td>
                <td className="py-4 text-right">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {item.volume}
                  </p>
                </td>
                <td className="py-4 text-right">
                  <Sparkline data={item.sparkline} positive={item.change > 0} />
                </td>
                <td className="py-4 text-right">
                  <button className="rounded-lg bg-violet-600 px-3 py-1 text-xs font-medium text-white hover:bg-violet-700 opacity-0 group-hover:opacity-100 transition-opacity">
                    Trade
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}