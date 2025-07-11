import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, XCircle, Clock, TrendingUp, TrendingDown } from 'lucide-react';

const activities = [
  {
    id: 1,
    type: 'trade',
    status: 'completed',
    title: 'Buy BTC/USDT',
    amount: '+0.15 BTC',
    price: '$43,250',
    time: '2 minutes ago',
    profit: 125.50,
  },
  {
    id: 2,
    type: 'trade',
    status: 'completed',
    title: 'Sell ETH/USDT',
    amount: '-2.5 ETH',
    price: '$2,340',
    time: '15 minutes ago',
    profit: -45.20,
  },
  {
    id: 3,
    type: 'strategy',
    status: 'pending',
    title: 'EMA Crossover Signal',
    description: 'Waiting for confirmation',
    time: '30 minutes ago',
  },
  {
    id: 4,
    type: 'trade',
    status: 'failed',
    title: 'Buy AAPL',
    description: 'Insufficient funds',
    time: '1 hour ago',
  },
  {
    id: 5,
    type: 'trade',
    status: 'completed',
    title: 'Sell TSLA',
    amount: '-50 shares',
    price: '$238.45',
    time: '2 hours ago',
    profit: 890.00,
  },
];

export function RecentActivity() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="rounded-2xl bg-white dark:bg-gray-900 p-6 shadow-sm border border-gray-200 dark:border-gray-800"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Recent Activity
        </h3>
        <button className="text-sm text-violet-600 hover:text-violet-700 font-medium">
          View All
        </button>
      </div>

      <div className="space-y-4">
        {activities.map((activity) => (
          <motion.div
            key={activity.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-start gap-3"
          >
            <div className="mt-1">
              {activity.status === 'completed' ? (
                <CheckCircle2 className="h-5 w-5 text-emerald-500" />
              ) : activity.status === 'failed' ? (
                <XCircle className="h-5 w-5 text-red-500" />
              ) : (
                <Clock className="h-5 w-5 text-amber-500" />
              )}
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {activity.title}
                </p>
                {activity.profit !== undefined && (
                  <div className={`flex items-center gap-1 text-sm font-medium ${
                    activity.profit > 0 ? 'text-emerald-600' : 'text-red-600'
                  }`}>
                    {activity.profit > 0 ? (
                      <TrendingUp className="h-3 w-3" />
                    ) : (
                      <TrendingDown className="h-3 w-3" />
                    )}
                    ${Math.abs(activity.profit).toFixed(2)}
                  </div>
                )}
              </div>
              
              <div className="mt-1 flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                {activity.amount && (
                  <>
                    <span>{activity.amount}</span>
                    {activity.price && (
                      <>
                        <span>•</span>
                        <span>{activity.price}</span>
                      </>
                    )}
                  </>
                )}
                {activity.description && (
                  <span>{activity.description}</span>
                )}
              </div>
              
              <p className="mt-1 text-xs text-gray-400">
                {activity.time}
              </p>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}