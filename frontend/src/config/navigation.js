import {
  LayoutDashboard,
  Code2,
  FolderKanban,
  ShieldAlert,
  Settings2,
  BarChart3,
} from 'lucide-react';

export const NAV_ITEMS = [
  {
    id: 'overview',
    label: 'Overview',
    description: 'Recent executions and sandbox summary',
    icon: LayoutDashboard,
    ready: true,
  },
  {
    id: 'playground',
    label: 'Playground',
    description: 'Monaco editor — compile and run plugins',
    icon: Code2,
    ready: true,
  },
  {
    id: 'plugins',
    label: 'Plugins',
    description: 'Saved plugins, versions, webhooks',
    icon: FolderKanban,
    ready: false,
  },
  {
    id: 'security',
    label: 'Security Lab',
    description: 'Curated attacks and denial reasons',
    icon: ShieldAlert,
    ready: false,
  },
  {
    id: 'operations',
    label: 'Operations',
    description: 'Sandbox health, violations, logs',
    icon: Settings2,
    ready: false,
  },
  {
    id: 'metrics',
    label: 'Metrics',
    description: 'Grafana, Prometheus, API metrics',
    icon: BarChart3,
    ready: false,
  },
];

export const DEFAULT_PAGE = 'overview';
