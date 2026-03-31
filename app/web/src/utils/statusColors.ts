import type { StageStatus } from '../types/events';

interface StatusStyle {
  bg: string;
  bgGradient: string;
  border: string;
  text: string;
  glow: string;
  iconBg: string;
  pulse: boolean;
  label: string;
  icon: string;
}

export const STATUS_STYLES: Record<StageStatus, StatusStyle> = {
  pending: {
    bg: 'rgba(30, 41, 59, 0.5)',
    bgGradient: 'linear-gradient(135deg, rgba(30, 41, 59, 0.6), rgba(15, 23, 42, 0.6))',
    border: 'rgba(71, 85, 105, 0.4)',
    text: '#94a3b8',
    glow: 'transparent',
    iconBg: 'rgba(71, 85, 105, 0.2)',
    pulse: false,
    label: '대기',
    icon: '⏸',
  },
  running: {
    bg: 'rgba(29, 78, 216, 0.15)',
    bgGradient: 'linear-gradient(135deg, rgba(29, 78, 216, 0.2), rgba(59, 130, 246, 0.1))',
    border: 'rgba(59, 130, 246, 0.5)',
    text: '#93c5fd',
    glow: 'rgba(59, 130, 246, 0.3)',
    iconBg: 'rgba(59, 130, 246, 0.15)',
    pulse: true,
    label: '실행 중',
    icon: '▶',
  },
  succeeded: {
    bg: 'rgba(5, 150, 105, 0.12)',
    bgGradient: 'linear-gradient(135deg, rgba(5, 150, 105, 0.18), rgba(16, 185, 129, 0.08))',
    border: 'rgba(16, 185, 129, 0.4)',
    text: '#6ee7b7',
    glow: 'rgba(16, 185, 129, 0.2)',
    iconBg: 'rgba(16, 185, 129, 0.12)',
    pulse: false,
    label: '성공',
    icon: '✓',
  },
  succeeded_with_warning: {
    bg: 'rgba(180, 83, 9, 0.12)',
    bgGradient: 'linear-gradient(135deg, rgba(180, 83, 9, 0.18), rgba(245, 158, 11, 0.08))',
    border: 'rgba(245, 158, 11, 0.4)',
    text: '#fcd34d',
    glow: 'rgba(245, 158, 11, 0.2)',
    iconBg: 'rgba(245, 158, 11, 0.12)',
    pulse: false,
    label: '경고',
    icon: '⚠',
  },
  failed: {
    bg: 'rgba(185, 28, 28, 0.12)',
    bgGradient: 'linear-gradient(135deg, rgba(185, 28, 28, 0.18), rgba(239, 68, 68, 0.08))',
    border: 'rgba(239, 68, 68, 0.4)',
    text: '#fca5a5',
    glow: 'rgba(239, 68, 68, 0.25)',
    iconBg: 'rgba(239, 68, 68, 0.12)',
    pulse: false,
    label: '실패',
    icon: '✕',
  },
  blocked: {
    bg: 'rgba(185, 28, 28, 0.12)',
    bgGradient: 'linear-gradient(135deg, rgba(185, 28, 28, 0.18), rgba(239, 68, 68, 0.08))',
    border: 'rgba(239, 68, 68, 0.4)',
    text: '#fca5a5',
    glow: 'rgba(239, 68, 68, 0.25)',
    iconBg: 'rgba(239, 68, 68, 0.12)',
    pulse: false,
    label: '차단',
    icon: '⊘',
  },
};

export function edgeColor(
  sourceStatus: StageStatus,
  targetStatus: StageStatus,
): { stroke: string; strokeDasharray?: string } {
  if (targetStatus === 'pending' && sourceStatus === 'pending') {
    return { stroke: 'rgba(71, 85, 105, 0.3)', strokeDasharray: '6,4' };
  }
  if (sourceStatus === 'running' || targetStatus === 'running') {
    return { stroke: 'rgba(59, 130, 246, 0.6)' };
  }
  if (sourceStatus === 'succeeded' && targetStatus !== 'pending') {
    return { stroke: 'rgba(16, 185, 129, 0.5)' };
  }
  if (sourceStatus === 'failed' || sourceStatus === 'blocked') {
    return { stroke: 'rgba(239, 68, 68, 0.5)' };
  }
  return { stroke: 'rgba(71, 85, 105, 0.3)', strokeDasharray: '6,4' };
}
