import React, { useState } from 'react';
import { 
  CheckCircle2, 
  Clock, 
  AlertTriangle, 
  ChevronDown, 
  ChevronUp, 
  Cpu, 
  Search, 
  ListOrdered, 
  Eye, 
  PlayCircle, 
  CheckCheck, 
  RotateCcw, 
  FastForward,
  Sparkles
} from 'lucide-react';
import { ReasoningStageLog, Language } from '../types';

interface ReasoningPipelineViewProps {
  stages: ReasoningStageLog[];
  language: Language;
}

const STAGE_ICONS: Record<string, any> = {
  understand: Search,
  think: Cpu,
  plan: ListOrdered,
  observe: Eye,
  execute: PlayCircle,
  review: CheckCheck,
  recover: RotateCcw,
  continue: FastForward,
};

export const ReasoningPipelineView: React.FC<ReasoningPipelineViewProps> = ({ stages, language }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const isFa = language === 'fa';

  if (!stages || stages.length === 0) return null;

  return (
    <div className="my-3 bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden shadow-md">
      {/* Header Bar */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-2.5 bg-slate-800/60 hover:bg-slate-800 flex items-center justify-between transition-colors text-left"
      >
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-semibold text-slate-200">
            {isFa ? 'پایپ‌لاین استدلال هوشمند (۸ مرحله‌ای)' : '8-Stage Reasoning Pipeline'}
          </span>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 font-mono border border-cyan-500/20">
            {stages.filter(s => s.status === 'completed').length}/{stages.length} {isFa ? 'مرحله کامل شد' : 'Stages Done'}
          </span>
        </div>
        <div className="flex items-center gap-2 text-slate-400">
          <span className="text-[11px]">
            {isExpanded ? (isFa ? 'بستن' : 'Collapse') : (isFa ? 'نمایش جزئیات' : 'Expand')}
          </span>
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {/* Expanded Stages Timeline */}
      {isExpanded && (
        <div className="p-3.5 space-y-2 text-xs">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {stages.map((stage, idx) => {
              const Icon = STAGE_ICONS[stage.id] || Cpu;
              const isCompleted = stage.status === 'completed';
              const isSkipped = stage.status === 'skipped';
              const isFailed = stage.status === 'failed';

              return (
                <div
                  key={stage.id || idx}
                  className={`p-2.5 rounded-lg border transition-all ${
                    isCompleted
                      ? 'bg-slate-950/60 border-slate-800 text-slate-300'
                      : isSkipped
                      ? 'bg-slate-950/30 border-slate-800/40 text-slate-500 opacity-60'
                      : isFailed
                      ? 'bg-rose-950/20 border-rose-800/40 text-rose-300'
                      : 'bg-cyan-950/20 border-cyan-800/40 text-cyan-200'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center gap-2 font-medium">
                      <div className={`p-1 rounded ${
                        isCompleted ? 'bg-emerald-500/10 text-emerald-400' : isSkipped ? 'bg-slate-800 text-slate-500' : 'bg-cyan-500/10 text-cyan-400'
                      }`}>
                        <Icon className="w-3.5 h-3.5" />
                      </div>
                      <span className="text-[11px]">
                        {isFa ? stage.nameFa : stage.name}
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5 text-[10px]">
                      {stage.durationMs && (
                        <span className="text-slate-500 font-mono">{stage.durationMs}ms</span>
                      )}
                      {isCompleted && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                      {isSkipped && <span className="text-slate-500">{isFa ? 'رد شد' : 'Skipped'}</span>}
                      {isFailed && <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />}
                    </div>
                  </div>

                  <p className="text-[11px] text-slate-400 font-mono leading-relaxed pl-6">
                    {isFa ? stage.detailsFa || stage.details : stage.details}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
