import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { 
  Activity, 
  CreditCard, 
  DollarSign, 
  TrendingUp,
  LineChart,
  Settings,
  User,
  Bell,
  Menu,
  Moon,
  Sun
} from 'lucide-react';
import { PerformanceChart } from './PerformanceChart';
import { PositionsTable } from './PositionsTable';
import { StrategyControl } from './StrategyControl';
import { RecentTrades } from './RecentTrades';

export function Dashboard() {
  const [darkMode, setDarkMode] = React.useState(true);

  React.useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center px-4">
          <div className="mr-4 flex">
            <Button variant="ghost" size="icon" className="lg:hidden">
              <Menu className="h-5 w-5" />
            </Button>
            <a className="mr-6 flex items-center space-x-2" href="/">
              <LineChart className="h-6 w-6 text-primary" />
              <span className="hidden font-bold sm:inline-block">
                AlgoTrader Pro
              </span>
            </a>
          </div>
          <nav className="flex items-center space-x-6 text-sm font-medium flex-1">
            <a className="transition-colors hover:text-foreground/80 text-foreground" href="/">
              Dashboard
            </a>
            <a className="transition-colors hover:text-foreground/80 text-foreground/60" href="/strategies">
              Strategies
            </a>
            <a className="transition-colors hover:text-foreground/80 text-foreground/60" href="/backtests">
              Backtests
            </a>
            <a className="transition-colors hover:text-foreground/80 text-foreground/60" href="/analytics">
              Analytics
            </a>
          </nav>
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setDarkMode(!darkMode)}
            >
              {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </Button>
            <Button variant="ghost" size="icon">
              <Bell className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon">
              <Settings className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon">
              <User className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto p-4 space-y-4">
        {/* Metrics Row */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Total Revenue
              </CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">$45,231.89</div>
              <p className="text-xs text-muted-foreground">
                +20.1% from last month
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Win Rate
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">68.5%</div>
              <p className="text-xs text-muted-foreground">
                +4.5% from last week
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Trades</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">12</div>
              <p className="text-xs text-muted-foreground">
                4 pending orders
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Account Balance
              </CardTitle>
              <CreditCard className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">$124,853</div>
              <p className="text-xs text-muted-foreground">
                $12,400 available
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts and Strategy Row */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
          <Card className="col-span-4">
            <CardHeader>
              <CardTitle>Performance Overview</CardTitle>
              <CardDescription>
                Your portfolio performance over the last 30 days
              </CardDescription>
            </CardHeader>
            <CardContent>
              <PerformanceChart />
            </CardContent>
          </Card>
          <Card className="col-span-3">
            <CardHeader>
              <CardTitle>Strategy Control</CardTitle>
              <CardDescription>
                Manage your active trading strategies
              </CardDescription>
            </CardHeader>
            <CardContent>
              <StrategyControl />
            </CardContent>
          </Card>
        </div>

        {/* Positions and Trades Row */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
          <Card className="col-span-4">
            <CardHeader>
              <CardTitle>Open Positions</CardTitle>
              <CardDescription>
                Your current active positions across all exchanges
              </CardDescription>
            </CardHeader>
            <CardContent>
              <PositionsTable />
            </CardContent>
          </Card>
          <Card className="col-span-3">
            <CardHeader>
              <CardTitle>Recent Trades</CardTitle>
              <CardDescription>
                Latest executed trades
              </CardDescription>
            </CardHeader>
            <CardContent>
              <RecentTrades />
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}