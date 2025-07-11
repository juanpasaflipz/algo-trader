import React from 'react';
import { motion } from 'framer-motion';
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Activity,
  Briefcase,
  PieChart,
  Bell,
  Search,
  Settings,
  Menu,
  ChevronDown,
  Sun,
  Moon,
  ArrowUpRight,
  ArrowDownRight,
  Plus,
  MoreVertical,
} from 'lucide-react';
import { AdvancedChart } from './AdvancedChart';
import { PortfolioAllocation } from './PortfolioAllocation';
import { WatchList } from './WatchList';
import { MetricCard } from './MetricCard';
import { RecentActivity } from './RecentActivity';

export function ModernDashboard() {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);
  const [darkMode, setDarkMode] = React.useState(true);

  React.useEffect(() => {
    // Apply dark mode class to HTML element on mount
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 z-40 h-screen transition-transform ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800`}
      >
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center gap-2 border-b border-gray-200 dark:border-gray-800 px-6">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600">
              <BarChart3 className="h-5 w-5 text-white" />
            </div>
            <span className="text-lg font-semibold">AlgoTrader Pro</span>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 p-4">
            <a
              href="#"
              className="flex items-center gap-3 rounded-lg bg-gradient-to-r from-violet-50 to-indigo-50 dark:from-violet-950/50 dark:to-indigo-950/50 px-3 py-2 text-violet-700 dark:text-violet-300"
            >
              <Activity className="h-5 w-5" />
              <span className="font-medium">Dashboard</span>
            </a>
            <a
              href="#"
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
            >
              <Briefcase className="h-5 w-5" />
              <span>Portfolio</span>
            </a>
            <a
              href="#"
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
            >
              <BarChart3 className="h-5 w-5" />
              <span>Strategies</span>
            </a>
            <a
              href="#"
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
            >
              <PieChart className="h-5 w-5" />
              <span>Analytics</span>
            </a>
          </nav>

          {/* User section */}
          <div className="border-t border-gray-200 dark:border-gray-800 p-4">
            <div className="flex items-center gap-3 rounded-lg px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer">
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-violet-500 to-indigo-500" />
              <div className="flex-1">
                <p className="text-sm font-medium">John Doe</p>
                <p className="text-xs text-gray-500">Premium Plan</p>
              </div>
              <ChevronDown className="h-4 w-4 text-gray-500" />
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className={`transition-all ${sidebarOpen ? 'ml-64' : 'ml-0'}`}>
        {/* Header */}
        <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-gray-200 bg-white/80 backdrop-blur-md dark:border-gray-800 dark:bg-gray-900/80 px-6">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <Menu className="h-5 w-5" />
          </button>

          <div className="flex flex-1 items-center gap-4">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search symbols, strategies..."
                className="w-full rounded-lg bg-gray-100 dark:bg-gray-800 py-2 pl-10 pr-4 text-sm outline-none placeholder:text-gray-500 focus:ring-2 focus:ring-violet-500"
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </button>
            <button className="relative rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-800">
              <Bell className="h-5 w-5" />
              <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-red-500" />
            </button>
            <button className="rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-800">
              <Settings className="h-5 w-5" />
            </button>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6 space-y-6">
          {/* Page title */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Trading Dashboard
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Welcome back! Here's your portfolio overview.
              </p>
            </div>
            <button className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 px-4 py-2 text-sm font-medium text-white hover:from-violet-700 hover:to-indigo-700">
              <Plus className="h-4 w-4" />
              New Trade
            </button>
          </div>

          {/* Metrics */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <MetricCard
              title="Total Balance"
              value="$142,384.92"
              change="+12.5%"
              trend="up"
              icon={DollarSign}
              gradient="from-violet-500 to-indigo-500"
            />
            <MetricCard
              title="Today's P&L"
              value="+$3,421.58"
              change="+2.4%"
              trend="up"
              icon={TrendingUp}
              gradient="from-emerald-500 to-teal-500"
            />
            <MetricCard
              title="Win Rate"
              value="73.2%"
              change="+5.1%"
              trend="up"
              icon={Activity}
              gradient="from-amber-500 to-orange-500"
            />
            <MetricCard
              title="Active Trades"
              value="18"
              change="-2"
              trend="down"
              icon={Briefcase}
              gradient="from-pink-500 to-rose-500"
            />
          </div>

          {/* Charts row */}
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <AdvancedChart />
            </div>
            <div>
              <PortfolioAllocation />
            </div>
          </div>

          {/* Bottom row */}
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <WatchList />
            </div>
            <div>
              <RecentActivity />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}