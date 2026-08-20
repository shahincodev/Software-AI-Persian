import React from 'react';
import { ShieldAlert, ShieldCheck, X, AlertTriangle } from 'lucide-react';
import { ConsentRequest, Language } from '../types';

interface SafetyConsentModalProps {
  request: ConsentRequest | null;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
  language: Language;
}

export const SafetyConsentModal: React.FC<SafetyConsentModalProps> = ({
  request,
  onApprove,
  onReject,
  language,
}) => {
  if (!request) return null;
  const isFa = language === 'fa';

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-amber-500/40 rounded-2xl max-w-lg w-full p-5 space-y-4 shadow-2xl animate-in zoom-in-95 duration-150">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center border border-amber-500/30">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">
                {isFa ? 'درخواست تایید اقدام با ریسک امنیتی' : 'Security Consent Confirmation'}
              </h3>
              <p className="text-[11px] text-amber-300 font-mono">
                {isFa ? 'سیستم امنیتی Software-AI Security Engine' : 'Software-AI Security Engine'}
              </p>
            </div>
          </div>
          <button
            onClick={() => onReject(request.id)}
            className="p-1 hover:bg-slate-800 rounded text-slate-400"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 space-y-2 text-xs">
          <div className="flex items-center justify-between">
            <span className="text-slate-400">{isFa ? 'ابزار مورد تقاضا:' : 'Requested Tool:'}</span>
            <span className="font-mono font-bold text-cyan-400">{request.tool}</span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-slate-400">{isFa ? 'نمره ریسک ارزیابی شده:' : 'Evaluated Risk Score:'}</span>
            <span className="font-mono font-bold text-rose-400">{request.riskScore} / 100 ({request.riskLevel})</span>
          </div>

          <div className="pt-2 border-t border-slate-900 text-slate-300 leading-relaxed">
            {isFa ? request.reasonFa : request.reason}
          </div>
        </div>

        <div className="flex items-center justify-end gap-2.5 pt-2">
          <button
            onClick={() => onReject(request.id)}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-colors"
          >
            {isFa ? 'رد و لغو عملیات' : 'Cancel & Reject'}
          </button>
          <button
            onClick={() => onApprove(request.id)}
            className="px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold shadow-lg shadow-amber-600/20 transition-colors"
          >
            {isFa ? 'تایید و ادامه اجرا' : 'Approve & Execute'}
          </button>
        </div>
      </div>
    </div>
  );
};
