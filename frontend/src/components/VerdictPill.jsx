import { CheckCircle, XCircle, AlertTriangle, HelpCircle, Info } from 'lucide-react';

const verdictConfig = {
  'True': {
    color: 'bg-success-100 text-success-800 border-success-300',
    icon: CheckCircle,
    label: 'True',
  },
  'False': {
    color: 'bg-danger-100 text-danger-800 border-danger-300',
    icon: XCircle,
    label: 'False',
  },
  'Misleading': {
    color: 'bg-warning-100 text-warning-800 border-warning-300',
    icon: AlertTriangle,
    label: 'Misleading',
  },
  'Partially True': {
    color: 'bg-blue-100 text-blue-800 border-blue-300',
    icon: Info,
    label: 'Partially True',
  },
  'Unverified': {
    color: 'bg-gray-100 text-gray-800 border-gray-300',
    icon: HelpCircle,
    label: 'Unverified',
  },
};

function VerdictPill({ verdict, size = 'md', showIcon = true }) {
  const config = verdictConfig[verdict] || verdictConfig['Unverified'];
  const Icon = config.icon;
  
  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  };
  
  return (
    <span className={`
      inline-flex items-center gap-1.5 font-medium rounded-full border
      ${config.color}
      ${sizeClasses[size]}
    `}>
      {showIcon && <Icon className={size === 'sm' ? 'w-3 h-3' : 'w-4 h-4'} />}
      <span>{config.label}</span>
    </span>
  );
}

export default VerdictPill;
