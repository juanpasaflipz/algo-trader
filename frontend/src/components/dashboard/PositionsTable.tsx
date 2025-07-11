import React from 'react';
import { ArrowUpIcon, ArrowDownIcon } from 'lucide-react';

interface Position {
  id: string;
  symbol: string;
  side: 'long' | 'short';
  quantity: number;
  entryPrice: number;
  currentPrice: number;
  pnl: number;
  pnlPercent: number;
  exchange: string;
}

const mockPositions: Position[] = [
  {
    id: '1',
    symbol: 'BTC/USDT',
    side: 'long',
    quantity: 0.5,
    entryPrice: 42000,
    currentPrice: 43500,
    pnl: 750,
    pnlPercent: 3.57,
    exchange: 'Binance',
  },
  {
    id: '2',
    symbol: 'ETH/USDT',
    side: 'long',
    quantity: 5,
    entryPrice: 2200,
    currentPrice: 2350,
    pnl: 750,
    pnlPercent: 6.82,
    exchange: 'Binance',
  },
  {
    id: '3',
    symbol: 'AAPL',
    side: 'short',
    quantity: 100,
    entryPrice: 185,
    currentPrice: 182,
    pnl: 300,
    pnlPercent: 1.62,
    exchange: 'Alpaca',
  },
  {
    id: '4',
    symbol: 'SPY',
    side: 'long',
    quantity: 50,
    entryPrice: 450,
    currentPrice: 448,
    pnl: -100,
    pnlPercent: -0.44,
    exchange: 'IBKR',
  },
];

export function PositionsTable() {
  return (
    <div className="space-y-4">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                Symbol
              </th>
              <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                Side
              </th>
              <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                Qty
              </th>
              <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                Entry
              </th>
              <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                Current
              </th>
              <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                P&L
              </th>
              <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                Exchange
              </th>
            </tr>
          </thead>
          <tbody>
            {mockPositions.map((position) => (
              <tr key={position.id} className="border-b">
                <td className="p-4 align-middle font-medium">
                  {position.symbol}
                </td>
                <td className="p-4 align-middle">
                  <span
                    className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-semibold ${
                      position.side === 'long'
                        ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400'
                        : 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400'
                    }`}
                  >
                    {position.side === 'long' ? (
                      <ArrowUpIcon className="h-3 w-3" />
                    ) : (
                      <ArrowDownIcon className="h-3 w-3" />
                    )}
                    {position.side.toUpperCase()}
                  </span>
                </td>
                <td className="p-4 align-middle">{position.quantity}</td>
                <td className="p-4 align-middle">
                  ${position.entryPrice.toLocaleString()}
                </td>
                <td className="p-4 align-middle">
                  ${position.currentPrice.toLocaleString()}
                </td>
                <td className="p-4 align-middle">
                  <div
                    className={`font-medium ${
                      position.pnl > 0 ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    ${position.pnl > 0 ? '+' : ''}{position.pnl.toLocaleString()}
                    <span className="text-xs ml-1">
                      ({position.pnlPercent > 0 ? '+' : ''}{position.pnlPercent.toFixed(2)}%)
                    </span>
                  </div>
                </td>
                <td className="p-4 align-middle text-muted-foreground">
                  {position.exchange}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}