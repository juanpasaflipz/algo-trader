import React from 'react';
import { format } from 'date-fns';
import { ArrowUpIcon, ArrowDownIcon } from 'lucide-react';

interface Trade {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  quantity: number;
  price: number;
  total: number;
  pnl?: number;
  timestamp: Date;
  exchange: string;
}

const mockTrades: Trade[] = [
  {
    id: '1',
    symbol: 'BTC/USDT',
    side: 'buy',
    quantity: 0.1,
    price: 43500,
    total: 4350,
    timestamp: new Date(Date.now() - 1000 * 60 * 5), // 5 min ago
    exchange: 'Binance',
  },
  {
    id: '2',
    symbol: 'ETH/USDT',
    side: 'sell',
    quantity: 2,
    price: 2350,
    total: 4700,
    pnl: 150,
    timestamp: new Date(Date.now() - 1000 * 60 * 15), // 15 min ago
    exchange: 'Binance',
  },
  {
    id: '3',
    symbol: 'AAPL',
    side: 'sell',
    quantity: 50,
    price: 182,
    total: 9100,
    pnl: -75,
    timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 min ago
    exchange: 'Alpaca',
  },
  {
    id: '4',
    symbol: 'SPY',
    side: 'buy',
    quantity: 25,
    price: 448,
    total: 11200,
    timestamp: new Date(Date.now() - 1000 * 60 * 45), // 45 min ago
    exchange: 'IBKR',
  },
  {
    id: '5',
    symbol: 'SOL/USDT',
    side: 'buy',
    quantity: 10,
    price: 98.5,
    total: 985,
    timestamp: new Date(Date.now() - 1000 * 60 * 60), // 1 hour ago
    exchange: 'Binance',
  },
];

export function RecentTrades() {
  return (
    <div className="space-y-4">
      <div className="space-y-3">
        {mockTrades.map((trade) => (
          <div
            key={trade.id}
            className="flex items-center justify-between rounded-lg border p-3"
          >
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="font-medium">{trade.symbol}</span>
                <span
                  className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold ${
                    trade.side === 'buy'
                      ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400'
                      : 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400'
                  }`}
                >
                  {trade.side === 'buy' ? (
                    <ArrowUpIcon className="h-3 w-3" />
                  ) : (
                    <ArrowDownIcon className="h-3 w-3" />
                  )}
                  {trade.side.toUpperCase()}
                </span>
              </div>
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <span>{trade.quantity} @ ${trade.price}</span>
                <span>•</span>
                <span>{format(trade.timestamp, 'HH:mm:ss')}</span>
                <span>•</span>
                <span>{trade.exchange}</span>
              </div>
            </div>
            <div className="text-right">
              <div className="font-medium">${trade.total.toLocaleString()}</div>
              {trade.pnl !== undefined && (
                <div
                  className={`text-sm ${
                    trade.pnl > 0 ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {trade.pnl > 0 ? '+' : ''}${trade.pnl}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}