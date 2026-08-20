import React, { useState } from 'react';
import { 
  Monitor, 
  Terminal, 
  FileText, 
  Calculator, 
  Folder, 
  X, 
  Minus, 
  Square, 
  Camera, 
  Eye, 
  MousePointer2, 
  RefreshCw,
  Search,
  Volume2,
  Wifi,
  BatteryCharging
} from 'lucide-react';
import { VirtualApp, DesktopElement, Language } from '../types';

interface DesktopSimulatorProps {
  apps: VirtualApp[];
  onToggleApp: (appId: string, action: 'open' | 'close' | 'minimize' | 'focus') => void;
  language: Language;
  onExecutePrompt?: (prompt: string) => void;
}

export const DesktopSimulator: React.FC<DesktopSimulatorProps> = ({
  apps,
  onToggleApp,
  language,
  onExecutePrompt
}) => {
  const isFa = language === 'fa';
  const [showOcrOverlay, setShowOcrOverlay] = useState(true);
  const [mousePosition, setMousePosition] = useState({ x: 380, y: 240 });
  const [calcInput, setCalcInput] = useState('0');
  const [screenshotModal, setScreenshotModal] = useState(false);

  // Simulated OCR bounding boxes
  const ocrElements: DesktopElement[] = [
    { id: 'el-1', text: 'Untitled - Notepad', textFa: 'بدون عنوان - نوت‌پد', type: 'window', bounds: { x: 40, y: 40, w: 420, h: 300 }, confidence: 0.98 },
    { id: 'el-2', text: 'Calculator', textFa: 'ماشین حساب', type: 'window', bounds: { x: 500, y: 40, w: 260, h: 340 }, confidence: 0.97 },
    { id: 'el-3', text: 'PowerShell', textFa: 'پاورشل', type: 'window', bounds: { x: 80, y: 140, w: 520, h: 280 }, confidence: 0.99 },
    { id: 'el-4', text: 'Start (شروع)', textFa: 'شروع', type: 'button', bounds: { x: 10, y: 480, w: 40, h: 36 }, confidence: 0.99 }
  ];

  const handleCalcClick = (val: string) => {
    if (val === 'C') {
      setCalcInput('0');
    } else if (val === '=') {
      try {
        // Safe evaluation
        const sanitized = calcInput.replace(/[^0-9+\-*/.]/g, '');
        const res = Function(`'use strict'; return (${sanitized})`)();
        setCalcInput(String(res));
      } catch {
        setCalcInput('Error');
      }
    } else {
      setCalcInput(prev => prev === '0' ? val : prev + val);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-950 rounded-2xl border border-slate-800 overflow-hidden shadow-2xl">
      {/* Simulation Control Bar */}
      <div className="px-4 py-2.5 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Monitor className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-semibold text-white">
            {isFa ? 'شبیه‌ساز محیط دسکتاپ و بینایی ویندوز (Windows 11 Desktop Vision)' : 'Windows 11 Desktop & Vision Simulator'}
          </span>
          <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
            1920x1080 (Virtual DPI: 96)
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* OCR overlay toggle */}
          <button
            onClick={() => setShowOcrOverlay(!showOcrOverlay)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs transition-colors ${
              showOcrOverlay
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                : 'bg-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            <span>{isFa ? 'نمایش جعبه‌های OCR' : 'OCR Boxes'}</span>
          </button>

          {/* Capture screenshot button */}
          <button
            onClick={() => setScreenshotModal(true)}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 border border-slate-700 transition-colors"
          >
            <Camera className="w-3.5 h-3.5 text-cyan-400" />
            <span>{isFa ? 'عکس‌برداری (Screenshot)' : 'Capture'}</span>
          </button>
        </div>
      </div>

      {/* Main Virtual Desktop Canvas */}
      <div 
        className="relative flex-1 bg-gradient-to-br from-slate-900 via-indigo-950/40 to-slate-950 p-6 min-h-[480px] overflow-hidden select-none"
        onClick={(e) => {
          const rect = e.currentTarget.getBoundingClientRect();
          setMousePosition({ x: e.clientX - rect.left, y: e.clientY - rect.top });
        }}
      >
        {/* Desktop Icons */}
        <div className="absolute top-6 left-6 flex flex-col gap-5 z-0">
          <div 
            onClick={() => onToggleApp('notepad', 'open')}
            className="group flex flex-col items-center gap-1 w-18 p-2 rounded-lg hover:bg-white/10 cursor-pointer transition-all"
          >
            <div className="w-10 h-10 rounded-lg bg-blue-500/20 border border-blue-400/40 flex items-center justify-center shadow-md">
              <FileText className="w-6 h-6 text-blue-400 group-hover:scale-110 transition-transform" />
            </div>
            <span className="text-[11px] text-slate-200 text-center font-medium drop-shadow">Notepad</span>
          </div>

          <div 
            onClick={() => onToggleApp('calc', 'open')}
            className="group flex flex-col items-center gap-1 w-18 p-2 rounded-lg hover:bg-white/10 cursor-pointer transition-all"
          >
            <div className="w-10 h-10 rounded-lg bg-amber-500/20 border border-amber-400/40 flex items-center justify-center shadow-md">
              <Calculator className="w-6 h-6 text-amber-400 group-hover:scale-110 transition-transform" />
            </div>
            <span className="text-[11px] text-slate-200 text-center font-medium drop-shadow">Calculator</span>
          </div>

          <div 
            onClick={() => onToggleApp('terminal', 'open')}
            className="group flex flex-col items-center gap-1 w-18 p-2 rounded-lg hover:bg-white/10 cursor-pointer transition-all"
          >
            <div className="w-10 h-10 rounded-lg bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center shadow-md">
              <Terminal className="w-6 h-6 text-emerald-400 group-hover:scale-110 transition-transform" />
            </div>
            <span className="text-[11px] text-slate-200 text-center font-medium drop-shadow">PowerShell</span>
          </div>

          <div 
            onClick={() => onToggleApp('explorer', 'open')}
            className="group flex flex-col items-center gap-1 w-18 p-2 rounded-lg hover:bg-white/10 cursor-pointer transition-all"
          >
            <div className="w-10 h-10 rounded-lg bg-indigo-500/20 border border-indigo-400/40 flex items-center justify-center shadow-md">
              <Folder className="w-6 h-6 text-indigo-400 group-hover:scale-110 transition-transform" />
            </div>
            <span className="text-[11px] text-slate-200 text-center font-medium drop-shadow">Downloads</span>
          </div>
        </div>

        {/* Windows Applications */}

        {/* 1. Notepad Window */}
        {apps.find(a => a.id === 'notepad')?.isOpen && !apps.find(a => a.id === 'notepad')?.isMinimized && (
          <div 
            className="absolute top-10 left-28 w-96 md:w-[440px] bg-slate-900/95 border border-slate-700 rounded-xl shadow-2xl overflow-hidden flex flex-col z-20 backdrop-blur-md animate-in fade-in zoom-in-95 duration-150"
            onClick={() => onToggleApp('notepad', 'focus')}
          >
            <div className="px-3 py-2 bg-slate-800/90 border-b border-slate-700 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-blue-400" />
                <span className="text-xs font-medium text-slate-200">Untitled - Notepad (یادداشت)</span>
              </div>
              <div className="flex items-center gap-1">
                <button onClick={() => onToggleApp('notepad', 'minimize')} className="p-1 hover:bg-slate-700 rounded text-slate-400">
                  <Minus className="w-3 h-3" />
                </button>
                <button onClick={() => onToggleApp('notepad', 'close')} className="p-1 hover:bg-rose-500 hover:text-white rounded text-slate-400">
                  <X className="w-3 h-3" />
                </button>
              </div>
            </div>
            <div className="p-3">
              <textarea
                value={apps.find(a => a.id === 'notepad')?.content || ''}
                readOnly
                placeholder={isFa ? 'عامل هوشمند می‌تواند در این فضا تایپ کند...' : 'AI Agent can type notes here...'}
                className="w-full h-40 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 font-mono resize-none focus:outline-none"
              />
              <div className="mt-2 flex items-center justify-between text-[10px] text-slate-400">
                <span>UTF-8 | Windows (CRLF)</span>
                <span>{apps.find(a => a.id === 'notepad')?.content?.length || 0} characters</span>
              </div>
            </div>
          </div>
        )}

        {/* 2. Calculator Window */}
        {apps.find(a => a.id === 'calc')?.isOpen && !apps.find(a => a.id === 'calc')?.isMinimized && (
          <div 
            className="absolute top-12 right-12 w-64 bg-slate-900/95 border border-slate-700 rounded-xl shadow-2xl overflow-hidden flex flex-col z-25 backdrop-blur-md"
            onClick={() => onToggleApp('calc', 'focus')}
          >
            <div className="px-3 py-2 bg-slate-800/90 border-b border-slate-700 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Calculator className="w-4 h-4 text-amber-400" />
                <span className="text-xs font-medium text-slate-200">Calculator</span>
              </div>
              <div className="flex items-center gap-1">
                <button onClick={() => onToggleApp('calc', 'minimize')} className="p-1 hover:bg-slate-700 rounded text-slate-400">
                  <Minus className="w-3 h-3" />
                </button>
                <button onClick={() => onToggleApp('calc', 'close')} className="p-1 hover:bg-rose-500 hover:text-white rounded text-slate-400">
                  <X className="w-3 h-3" />
                </button>
              </div>
            </div>
            <div className="p-3 space-y-2">
              <div className="bg-slate-950 p-2.5 rounded-lg text-right font-mono text-lg font-bold text-slate-100 border border-slate-800">
                {calcInput}
              </div>
              <div className="grid grid-cols-4 gap-1.5 text-xs font-medium">
                {['C', '/', '*', '-'].map(k => (
                  <button key={k} onClick={() => handleCalcClick(k)} className="p-2 bg-slate-800 hover:bg-slate-700 text-amber-300 rounded-lg">
                    {k}
                  </button>
                ))}
                {['7', '8', '9', '+'].map(k => (
                  <button key={k} onClick={() => handleCalcClick(k)} className="p-2 bg-slate-800/60 hover:bg-slate-700 text-slate-200 rounded-lg">
                    {k}
                  </button>
                ))}
                {['4', '5', '6', '='].map(k => (
                  <button key={k} onClick={() => handleCalcClick(k)} className={`p-2 rounded-lg ${k === '=' ? 'bg-cyan-600 hover:bg-cyan-500 text-white row-span-2' : 'bg-slate-800/60 hover:bg-slate-700 text-slate-200'}`}>
                    {k}
                  </button>
                ))}
                {['1', '2', '3', '0'].map(k => (
                  <button key={k} onClick={() => handleCalcClick(k)} className="p-2 bg-slate-800/60 hover:bg-slate-700 text-slate-200 rounded-lg">
                    {k}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* 3. PowerShell Terminal Window */}
        {apps.find(a => a.id === 'terminal')?.isOpen && !apps.find(a => a.id === 'terminal')?.isMinimized && (
          <div 
            className="absolute bottom-16 left-32 w-11/12 max-w-xl bg-slate-950 border border-slate-700 rounded-xl shadow-2xl overflow-hidden flex flex-col z-15 backdrop-blur-md"
            onClick={() => onToggleApp('terminal', 'focus')}
          >
            <div className="px-3 py-2 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-medium text-slate-300 font-mono">Windows PowerShell</span>
              </div>
              <div className="flex items-center gap-1">
                <button onClick={() => onToggleApp('terminal', 'minimize')} className="p-1 hover:bg-slate-800 rounded text-slate-400">
                  <Minus className="w-3 h-3" />
                </button>
                <button onClick={() => onToggleApp('terminal', 'close')} className="p-1 hover:bg-rose-500 hover:text-white rounded text-slate-400">
                  <X className="w-3 h-3" />
                </button>
              </div>
            </div>
            <pre className="p-3 text-[11px] text-emerald-400 font-mono h-36 overflow-y-auto leading-relaxed whitespace-pre-wrap">
              {apps.find(a => a.id === 'terminal')?.content}
            </pre>
          </div>
        )}

        {/* OCR Bounding Boxes Visualizer */}
        {showOcrOverlay && (
          <div className="absolute inset-0 pointer-events-none z-30">
            {ocrElements.map((el) => (
              <div
                key={el.id}
                style={{
                  left: `${el.bounds.x}px`,
                  top: `${el.bounds.y}px`,
                  width: `${el.bounds.w}px`,
                  height: `${el.bounds.h}px`
                }}
                className="absolute border border-cyan-400/60 bg-cyan-500/5 rounded transition-all"
              >
                <span className="absolute -top-3.5 left-0 px-1 py-0.2 bg-cyan-900/90 text-cyan-300 text-[9px] font-mono rounded border border-cyan-400/40 whitespace-nowrap shadow">
                  {el.text} [{(el.confidence * 100).toFixed(0)}%]
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Simulated Animated Mouse Pointer */}
        <div 
          className="absolute z-40 transition-all duration-300 pointer-events-none"
          style={{ left: `${mousePosition.x}px`, top: `${mousePosition.y}px` }}
        >
          <MousePointer2 className="w-5 h-5 text-amber-400 drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)] -rotate-12 fill-amber-400" />
          <span className="ml-4 -mt-1 px-1.5 py-0.5 bg-slate-900/90 text-[9px] text-amber-300 font-mono rounded border border-amber-500/30">
            {mousePosition.x},{mousePosition.y}
          </span>
        </div>
      </div>

      {/* Windows Taskbar */}
      <div className="h-11 bg-slate-900/95 border-t border-slate-800 px-3 flex items-center justify-between z-30">
        <div className="flex items-center gap-1.5">
          {/* Start Button */}
          <button 
            className="flex items-center justify-center w-8 h-8 rounded-lg bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-400 transition-colors"
            title={isFa ? 'منوی استارت' : 'Start Menu'}
          >
            <div className="grid grid-cols-2 gap-0.5 w-3.5 h-3.5">
              <div className="bg-cyan-400 rounded-[1px]" />
              <div className="bg-cyan-400 rounded-[1px]" />
              <div className="bg-cyan-400 rounded-[1px]" />
              <div className="bg-cyan-400 rounded-[1px]" />
            </div>
          </button>

          {/* Search bar */}
          <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 bg-slate-800/80 rounded-lg border border-slate-700/60 text-xs text-slate-400 w-36">
            <Search className="w-3.5 h-3.5" />
            <span>{isFa ? 'جستجو...' : 'Search...'}</span>
          </div>

          {/* Running App Icons in Taskbar */}
          <div className="flex items-center gap-1 ml-2">
            {apps.map((app) => (
              <button
                key={app.id}
                onClick={() => onToggleApp(app.id, app.isOpen && !app.isMinimized ? 'minimize' : 'open')}
                className={`p-1.5 rounded-lg flex items-center gap-1 text-xs transition-all ${
                  app.isOpen && !app.isMinimized
                    ? 'bg-slate-700/80 text-cyan-300 border-b-2 border-cyan-400'
                    : app.isOpen
                    ? 'bg-slate-800 text-slate-400'
                    : 'hover:bg-slate-800 text-slate-500'
                }`}
                title={app.title}
              >
                {app.id === 'notepad' && <FileText className="w-4 h-4 text-blue-400" />}
                {app.id === 'calc' && <Calculator className="w-4 h-4 text-amber-400" />}
                {app.id === 'terminal' && <Terminal className="w-4 h-4 text-emerald-400" />}
                {app.id === 'explorer' && <Folder className="w-4 h-4 text-indigo-400" />}
              </button>
            ))}
          </div>
        </div>

        {/* System Tray */}
        <div className="flex items-center gap-3 text-xs text-slate-400 font-mono">
          <div className="flex items-center gap-1.5">
            <Wifi className="w-3.5 h-3.5 text-slate-300" />
            <Volume2 className="w-3.5 h-3.5 text-slate-300" />
            <BatteryCharging className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <div className="text-[11px] text-right">
            <div>{new Date().toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' })}</div>
            <div className="text-[9px] text-slate-500">2026/06/24</div>
          </div>
        </div>
      </div>

      {/* Screenshot Modal preview */}
      {screenshotModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Camera className="w-5 h-5 text-cyan-400" />
                <h3 className="text-sm font-semibold text-white">
                  {isFa ? 'تصویر برداری دسکتاپ و تحلیل بینایی OCR' : 'Desktop Screenshot & OCR Vision Capture'}
                </h3>
              </div>
              <button onClick={() => setScreenshotModal(false)} className="p-1 hover:bg-slate-800 rounded text-slate-400">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2 text-xs font-mono text-slate-300">
              <div className="text-emerald-400">✅ Screen Captured: 1920x1080 @ 96 DPI</div>
              <div>• OCR Engine: Tesseract 5.3 + OpenCV Vision Loop</div>
              <div>• Detected text regions: {ocrElements.length} elements</div>
              <div className="p-2 bg-slate-900 rounded border border-slate-800 text-[11px]">
                {ocrElements.map(e => `[${e.type.toUpperCase()}] "${e.text}" at (${e.bounds.x}, ${e.bounds.y})`).join('\n')}
              </div>
            </div>

            <div className="flex justify-end gap-2">
              <button
                onClick={() => setScreenshotModal(false)}
                className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-medium"
              >
                {isFa ? 'بستن' : 'Close'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
