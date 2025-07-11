import React from 'react';
import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { MoreVertical } from 'lucide-react';

const data = [
  { name: 'Stocks', value: 45, amount: 64000, color: '#8b5cf6' },
  { name: 'Crypto', value: 30, amount: 42700, color: '#3b82f6' },
  { name: 'Forex', value: 15, amount: 21350, color: '#10b981' },
  { name: 'Commodities', value: 10, amount: 14234, color: '#f59e0b' },
];

export function PortfolioAllocation() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="rounded-2xl bg-white dark:bg-gray-900 p-6 shadow-sm border border-gray-200 dark:border-gray-800 h-full"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Portfolio Allocation
        </h3>
        <button className="rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-800">
          <MoreVertical className="h-5 w-5 text-gray-500" />
        </button>
      </div>

      <div className="relative">
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              paddingAngle={3}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="rounded-lg bg-white dark:bg-gray-800 p-2 shadow-lg border border-gray-200 dark:border-gray-700">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {payload[0].name}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {payload[0].value}%
                      </p>
                    </div>
                  );
                }
                return null;
              }}
            />
          </PieChart>
        </ResponsiveContainer>
        
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              $142.3k
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Total</p>
          </div>
        </div>
      </div>

      <div className="mt-6 space-y-3">
        {data.map((item) => (
          <div key={item.name} className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div
                className="h-3 w-3 rounded-full"
                style={{ backgroundColor: item.color }}
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                {item.name}
              </span>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                ${(item.amount / 1000).toFixed(1)}k
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {item.value}%
              </p>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}