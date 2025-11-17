import React from 'react';
import { cn } from '@/lib/utils/cn';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  gradient?: boolean;
}

export function Card({ children, className = '', hover = false, gradient = false }: CardProps) {
  // Use deterministic className to ensure consistent SSR and client rendering
  // overflow-hidden is always included to prevent hydration mismatches
  return (
    <div
      className={cn(
        'bg-white rounded-2xl border border-slate-200/60 shadow-fintech overflow-hidden backdrop-blur-sm',
        gradient && 'gradient-card',
        hover && 'hover:shadow-fintech-lg hover:border-primary-300/60 transition-all duration-300 transform hover:-translate-y-0.5',
        className
      )}
    >
      {children}
    </div>
  );
}

interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
}

export function CardHeader({ children, className = '' }: CardHeaderProps) {
  return (
    <div className={cn('px-6 py-5 border-b border-gray-100 bg-gray-50/50', className)}>
      {children}
    </div>
  );
}

interface CardContentProps {
  children: React.ReactNode;
  className?: string;
}

export function CardContent({ children, className = '' }: CardContentProps) {
  return <div className={cn('px-6 py-5', className)}>{children}</div>;
}

interface CardFooterProps {
  children: React.ReactNode;
  className?: string;
}

export function CardFooter({ children, className = '' }: CardFooterProps) {
  return (
    <div className={cn('px-6 py-4 border-t border-gray-100 bg-gray-50/50', className)}>
      {children}
    </div>
  );
}

