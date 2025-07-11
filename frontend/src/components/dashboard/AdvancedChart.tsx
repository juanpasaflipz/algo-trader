import React from 'react';
import { motion } from 'framer-motion';
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from 'recharts';
import { MoreVertical, TrendingUp } from 'lucide-react';

const generateData = () => {
  const data = [];
  const baseValue = 100000;
  let currentValue = baseValue;
  
  for (let i = 30; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    
    const change = (Math.random() - 0.45) * 0.03;
    currentValue = currentValue * (1 + change);
    
    data.push({
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      value: Math.round(currentValue),
      profit: Math.round(currentValue - baseValue),
    });
  }
  
  return data;
};

export function AdvancedChart() {
  const [data] = React.useState(generateData);
  const [timeframe, setTimeframe] = React.useState('1M');
  
  const profit = data[data.length - 1].profit;
  const profitPercent = ((profit / 100000) * 100).toFixed(2);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl bg-white dark:bg-gray-900 p-6 shadow-sm border border-gray-200 dark:border-gray-800"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Portfolio Performance
          </h3>
          <div className="mt-2 flex items-center gap-2">
            <span className="text-3xl font-bold text-gray-900 dark:text-white">
              ${data[data.length - 1].value.toLocaleString()}
            </span>
            <div className={`flex items-center gap-1 rounded-full px-2 py-1 text-sm font-medium ${
              profit > 0 
                ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
                : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
            }`}>
              <TrendingUp className="h-3 w-3" />
              {profit > 0 ? '+' : ''}{profitPercent}%
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <div className="flex rounded-lg bg-gray-100 dark:bg-gray-800 p-1">
            {['1D', '1W', '1M', '3M', '1Y'].map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`rounded-md px-3 py-1 text-sm font-medium transition-all ${
                  timeframe === tf
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
          <button className="rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-800">
            <MoreVertical className="h-5 w-5 text-gray-500" />
          </button>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
          <XAxis
            dataKey="date"
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: '#6b7280' }}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: '#6b7280' }}
            tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                return (
                  <div className="rounded-lg bg-white dark:bg-gray-800 p-3 shadow-lg border border-gray-200 dark:border-gray-700">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {payload[0].payload.date}
                    </p>
                    <p className="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
                      ${payload[0].value?.toLocaleString()}
                    </p>
                    <p className={`mt-1 text-sm font-medium ${
                      payload[0].payload.profit > 0 ? 'text-emerald-600' : 'text-red-600'
                    }`}>
                      {payload[0].payload.profit > 0 ? '+' : ''}
                      ${payload[0].payload.profit?.toLocaleString()}
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke="#8b5cf6"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorValue)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </motion.div>
  );
}