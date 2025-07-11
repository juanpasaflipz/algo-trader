import React from 'react';
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { format } from 'date-fns';

const generateData = () => {
  const data = [];
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - 30);
  
  let balance = 100000;
  
  for (let i = 0; i < 30; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    
    // Simulate daily returns
    const dailyReturn = (Math.random() - 0.48) * 0.03; // -1.5% to +1.5% daily
    balance = balance * (1 + dailyReturn);
    
    data.push({
      date: format(date, 'MMM dd'),
      balance: Math.round(balance),
      pnl: Math.round((balance - 100000)),
    });
  }
  
  return data;
};

export function PerformanceChart() {
  const [data] = React.useState(generateData);

  return (
    <ResponsiveContainer width="100%" height={350}>
      <LineChart data={data}>
        <XAxis
          dataKey="date"
          stroke="#888888"
          fontSize={12}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          stroke="#888888"
          fontSize={12}
          tickLine={false}
          axisLine={false}
          tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
        />
        <Tooltip
          content={({ active, payload }) => {
            if (active && payload && payload.length) {
              return (
                <div className="rounded-lg border bg-background p-2 shadow-sm">
                  <div className="grid grid-cols-2 gap-2">
                    <div className="flex flex-col">
                      <span className="text-[0.70rem] uppercase text-muted-foreground">
                        Balance
                      </span>
                      <span className="font-bold text-muted-foreground">
                        ${payload[0].value?.toLocaleString()}
                      </span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[0.70rem] uppercase text-muted-foreground">
                        P&L
                      </span>
                      <span className={`font-bold ${payload[1].value as number > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        ${payload[1].value?.toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
              );
            }
            return null;
          }}
        />
        <Line
          type="monotone"
          dataKey="balance"
          strokeWidth={2}
          stroke="hsl(var(--primary))"
          activeDot={{
            r: 6,
            style: { fill: "hsl(var(--primary))", opacity: 0.8 },
          }}
        />
        <Line
          type="monotone"
          dataKey="pnl"
          strokeWidth={2}
          stroke={data[data.length - 1].pnl > 0 ? "#10b981" : "#ef4444"}
          strokeDasharray="5 5"
          activeDot={{
            r: 4,
            style: { fill: data[data.length - 1].pnl > 0 ? "#10b981" : "#ef4444", opacity: 0.8 },
          }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}