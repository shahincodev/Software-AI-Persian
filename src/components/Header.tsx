import React from 'react';
import { 
  Bot, 
  Cpu, 
  HardDrive, 
  Shield, 
  Globe, 
  Sparkles, 
  Monitor, 
  Wrench, 
  FolderTree, 
  BrainCircuit, 
  Activity,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { Language, SystemHardware, ProviderStatus } from '../types';

interface HeaderProps {
  language: Language;
  onLanguageChange: (lang: Language) => void;
  activeTab: 'chat' | 'desktop' | 'tools' | 'files' | 'memory';
  onTabChange: (tab: 'chat' | 'desktop' | 'tools' | 'files' | 'memory') => void;
  hardware: SystemHardware | null;
  providers: ProviderStatus[];
  onOpenProvidersModal: () => void;
  safetyMode: 'strict' | 'standard' | 'power';
  onSafetyModeChange: (mode: 'strict' | 'standard' | 'power') => void;
}

export const Header: React.FC<HeaderProps> = ({
  language,
  onLanguageChange,
  activeTab,
  onTabChange,
  hardware,
  providers,
  onOpenProvidersModal,
  safetyMode,
  onSafetyModeChange,
}) => {
  const isFa = language === 'fa';
  const availableCount = providers.filter(p => p.isAvailable).length;

  return (
    <header className="bg-slate-900/90 backdrop-blur-md border-b border-slate-800 sticky top-0 z-40 px-4 py-2.5">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Brand & Status */}
        <div className="flex items-center gap-3 w-full md:w-auto justify-between md:justify-start">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-base tracking-tight text-white">Software-AI</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-mono border border-cyan-500/30">
                  v1.2.0
                </span>
              </div>
              <p className="text-xs text-slate-400">
                {isFa ? 'عامل هوشمند ویندوز با استدلال فارسی' : 'Autonomous Windows AI Agent'}
              </p>
            </div>
          </div>

          {/* Quick status pill */}
          <button 
            onClick={onOpenProvidersModal}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700/80 hover:bg-slate-700/80 transition-colors text-xs text-slate-300"
            title={isFa ? 'مشاهده وضعیت ارائه‌دهندگان هوش مصنوعی' : 'View AI Providers'}
          >
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>{isFa ? 'ارائه‌دهندگان:' : 'Providers:'}</span>
            <span className="font-semibold text-emerald-400">{availableCount}/{providers.length}</span>
          </button>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 bg-slate-950/80 p-1 rounded-xl border border-slate-800 text-xs font-medium w-full md:w-auto overflow-x-auto">
          <button
            onClick={() => onTabChange('chat')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all whitespace-nowrap ${
              activeTab === 'chat'
                ? 'bg-cyan-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Bot className="w-4 h-4" />
            <span>{isFa ? 'کنسول عامل هوشمند' : 'Agent Console'}</span>
          </button>

          <button
            onClick={() => onTabChange('desktop')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all whitespace-nowrap ${
              activeTab === 'desktop'
                ? 'bg-cyan-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Monitor className="w-4 h-4" />
            <span>{isFa ? 'شبیه‌ساز دسکتاپ و بینایی' : 'Desktop & Vision'}</span>
          </button>

          <button
            onClick={() => onTabChange('tools')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all whitespace-nowrap ${
              activeTab === 'tools'
                ? 'bg-cyan-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Wrench className="w-4 h-4" />
            <span>{isFa ? '۲۰ ابزار سیستمی' : '20 Tools'}</span>
          </button>

          <button
            onClick={() => onTabChange('files')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all whitespace-nowrap ${
              activeTab === 'files'
                ? 'bg-cyan-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <FolderTree className="w-4 h-4" />
            <span>{isFa ? 'فایل‌ها و ویندوز' : 'File Explorer'}</span>
          </button>

          <button
            onClick={() => onTabChange('memory')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all whitespace-nowrap ${
              activeTab === 'memory'
                ? 'bg-cyan-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <BrainCircuit className="w-4 h-4" />
            <span>{isFa ? 'نشست‌ها و حافظه' : 'Sessions & Memory'}</span>
          </button>
        </nav>

        {/* Right actions: Hardware, Safety, Language */}
        <div className="flex items-center gap-2.5 w-full md:w-auto justify-end">
          {/* Hardware mini-telemetry */}
          {hardware && (
            <div className="hidden lg:flex items-center gap-3 px-3 py-1 bg-slate-950/60 border border-slate-800 rounded-lg text-[11px] text-slate-400 font-mono">
              <div className="flex items-center gap-1">
                <Cpu className="w-3.5 h-3.5 text-cyan-400" />
                <span>CPU: {hardware.cpuUsage}%</span>
              </div>
              <div className="flex items-center gap-1">
                <HardDrive className="w-3.5 h-3.5 text-indigo-400" />
                <span>RAM: {hardware.ramUsage}%</span>
              </div>
            </div>
          )}

          {/* Safety mode selector */}
          <div className="flex items-center bg-slate-950/80 p-0.5 rounded-lg border border-slate-800 text-xs">
            <button
              onClick={() => onSafetyModeChange('power')}
              className={`px-2 py-1 rounded text-[11px] font-medium transition-colors ${
                safetyMode === 'power'
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  : 'text-slate-400 hover:text-slate-300'
              }`}
              title={isFa ? 'حالت قدرت: اجرای خودکار دستورات استاندارد' : 'Power Mode: Auto-approve safe actions'}
            >
              <span className="flex items-center gap-1">
                <Shield className="w-3 h-3 text-amber-400" />
                <span>Power</span>
              </span>
            </button>
            <button
              onClick={() => onSafetyModeChange('strict')}
              className={`px-2 py-1 rounded text-[11px] font-medium transition-colors ${
                safetyMode === 'strict'
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                  : 'text-slate-400 hover:text-slate-300'
              }`}
              title={isFa ? 'حالت سخت‌گیرانه: تایید دستی تمامی اقدامات' : 'Strict Mode: Require manual confirmation'}
            >
              <span>Strict</span>
            </button>
          </div>

          {/* Language toggle */}
          <button
            onClick={() => onLanguageChange(isFa ? 'en' : 'fa')}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700 hover:bg-slate-700 text-xs text-slate-200 font-medium transition-colors"
          >
            <Globe className="w-3.5 h-3.5 text-cyan-400" />
            <span>{isFa ? 'English' : 'فارسی'}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
