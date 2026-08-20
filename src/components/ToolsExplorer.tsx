import React, { useState } from 'react';
import { 
  Wrench, 
  Play, 
  Terminal, 
  CheckCircle2, 
  AlertCircle, 
  ShieldAlert, 
  ShieldCheck, 
  Folder, 
  Eye, 
  BrainCircuit, 
  Cpu, 
  Search,
  Check
} from 'lucide-react';
import { ToolDefinition, ToolExecutionResult, Language } from '../types';

interface ToolsExplorerProps {
  tools: ToolDefinition[];
  onExecuteTool: (toolName: string, params: Record<string, any>) => Promise<ToolExecutionResult>;
  language: Language;
}

export const ToolsExplorer: React.FC<ToolsExplorerProps> = ({
  tools,
  onExecuteTool,
  language,
}) => {
  const isFa = language === 'fa';
  const [selectedTool, setSelectedTool] = useState<ToolDefinition | null>(tools[0] || null);
  const [paramValues, setParamValues] = useState<Record<string, any>>({});
  const [isExecuting, setIsExecuting] = useState(false);
  const [lastResult, setLastResult] = useState<ToolExecutionResult | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState<string>('all');

  const filteredTools = tools.filter(t => {
    const matchesSearch = t.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
      t.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.descriptionFa.includes(searchQuery);
    const matchesCat = activeCategory === 'all' || t.category === activeCategory;
    return matchesSearch && matchesCat;
  });

  const handleSelectTool = (tool: ToolDefinition) => {
    setSelectedTool(tool);
    const defaultParams: Record<string, any> = {};
    tool.params.forEach(p => {
      defaultParams[p.name] = p.default !== undefined ? p.default : '';
    });
    setParamValues(defaultParams);
    setLastResult(null);
  };

  const handleExecute = async () => {
    if (!selectedTool) return;
    setIsExecuting(true);
    try {
      const res = await onExecuteTool(selectedTool.name, paramValues);
      setLastResult(res);
    } catch (err: any) {
      setLastResult({
        tool: selectedTool.name,
        params: paramValues,
        success: false,
        error: err.message,
        durationMs: 0,
        timestamp: new Date().toISOString()
      });
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 h-[750px] bg-slate-950/60 p-4 rounded-2xl border border-slate-800">
      {/* Left Sidebar: Tool Registry */}
      <div className="lg:col-span-5 flex flex-col bg-slate-900/90 rounded-xl border border-slate-800 p-3.5 overflow-hidden">
        <div className="mb-3 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Wrench className="w-4 h-4 text-cyan-400" />
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                {isFa ? 'ثبت ابزارهای کانونی (۲۰ ابزار)' : 'Canonical Tool Registry (20 Tools)'}
              </h3>
            </div>
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">
              {filteredTools.length}
            </span>
          </div>

          {/* Search box */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5 rtl:right-2.5 rtl:left-auto" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={isFa ? 'جستجوی ابزار...' : 'Search tools...'}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 rtl:pr-8 rtl:pl-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          {/* Category Filter Pills */}
          <div className="flex items-center gap-1 overflow-x-auto pb-1 text-[11px] no-scrollbar">
            {['all', 'system', 'desktop_ui', 'vision', 'filesystem', 'memory'].map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-2 py-0.5 rounded-md whitespace-nowrap transition-colors ${
                  activeCategory === cat
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-medium'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {cat === 'all' ? (isFa ? 'همه' : 'All') : cat}
              </button>
            ))}
          </div>
        </div>

        {/* Tool List */}
        <div className="flex-1 overflow-y-auto space-y-1.5 pr-1">
          {filteredTools.map((t) => {
            const isSelected = selectedTool?.name === t.name;
            return (
              <div
                key={t.name}
                onClick={() => handleSelectTool(t)}
                className={`p-2.5 rounded-lg border cursor-pointer transition-all ${
                  isSelected
                    ? 'bg-cyan-950/40 border-cyan-500/60 shadow-sm'
                    : 'bg-slate-950/50 border-slate-800/80 hover:bg-slate-800/60'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-mono text-xs font-semibold text-cyan-300">{t.name}</span>
                  <span className={`text-[10px] px-1.5 py-0.2 rounded font-mono ${
                    t.riskLevel === 'high' ? 'bg-rose-500/20 text-rose-300' :
                    t.riskLevel === 'medium' ? 'bg-amber-500/20 text-amber-300' :
                    t.riskLevel === 'low' ? 'bg-blue-500/20 text-blue-300' :
                    'bg-emerald-500/20 text-emerald-300'
                  }`}>
                    {t.riskLevel}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 line-clamp-2">
                  {isFa ? t.descriptionFa : t.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Right Panel: Tool Parameters & Execution Console */}
      <div className="lg:col-span-7 flex flex-col bg-slate-900/90 rounded-xl border border-slate-800 p-4 overflow-hidden">
        {selectedTool ? (
          <div className="flex-1 flex flex-col justify-between space-y-4 overflow-y-auto">
            {/* Header of selected tool */}
            <div className="border-b border-slate-800 pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-base font-bold text-white font-mono">{selectedTool.name}</span>
                  <span className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                    {selectedTool.category}
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  {selectedTool.riskLevel === 'high' ? (
                    <ShieldAlert className="w-4 h-4 text-rose-400" />
                  ) : (
                    <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  )}
                  <span className="text-xs font-mono text-slate-400 capitalize">{selectedTool.riskLevel} Risk</span>
                </div>
              </div>
              <p className="text-xs text-slate-300 mt-1">
                {isFa ? selectedTool.descriptionFa : selectedTool.description}
              </p>
            </div>

            {/* Parameters Form */}
            <div className="space-y-3">
              <h4 className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <span>{isFa ? 'پارامترهای ورودی ابزار:' : 'Tool Parameters:'}</span>
              </h4>

              {selectedTool.params.length === 0 ? (
                <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800 text-xs text-slate-500">
                  {isFa ? 'این ابزار نیازی به پارامتر ورودی ندارد.' : 'This tool takes no parameters.'}
                </div>
              ) : (
                selectedTool.params.map((p) => (
                  <div key={p.name} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <label className="font-mono text-cyan-400">
                        {p.name} {p.required && <span className="text-rose-400">*</span>}
                      </label>
                      <span className="text-[10px] text-slate-500 font-mono">({p.type})</span>
                    </div>
                    <input
                      type="text"
                      value={paramValues[p.name] !== undefined ? paramValues[p.name] : ''}
                      onChange={(e) => setParamValues({ ...paramValues, [p.name]: e.target.value })}
                      placeholder={p.description}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
                    />
                    <p className="text-[10px] text-slate-500">
                      {isFa ? p.descriptionFa || p.description : p.description}
                    </p>
                  </div>
                ))
              )}
            </div>

            {/* Execution Result Box */}
            {lastResult && (
              <div className="bg-slate-950 border border-slate-800 rounded-xl p-3.5 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    {lastResult.success ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <AlertCircle className="w-4 h-4 text-rose-400" />
                    )}
                    <span className="text-xs font-semibold text-slate-200 font-mono">
                      {lastResult.success ? (isFa ? 'اجرای موفقیت‌آمیز' : 'Execution Successful') : (isFa ? 'خطا در اجرا' : 'Execution Failed')}
                    </span>
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">{lastResult.durationMs}ms</span>
                </div>
                <pre className="text-[11px] text-emerald-400 bg-slate-900 p-2.5 rounded border border-slate-800 font-mono overflow-x-auto max-h-36">
                  {JSON.stringify(lastResult.output || lastResult.error, null, 2)}
                </pre>
              </div>
            )}

            {/* Execute Button */}
            <div className="pt-3 border-t border-slate-800 flex justify-end">
              <button
                onClick={handleExecute}
                disabled={isExecuting}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium text-xs flex items-center gap-2 shadow-lg shadow-cyan-600/20 disabled:opacity-50 cursor-pointer"
              >
                <Play className="w-3.5 h-3.5" />
                <span>
                  {isExecuting ? (isFa ? 'در حال اجرا...' : 'Executing...') : (isFa ? 'اجرای مستقیم ابزار' : 'Execute Tool')}
                </span>
              </button>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center text-xs text-slate-500">
            {isFa ? 'یک ابزار را از منوی سمت راست انتخاب کنید.' : 'Select a tool from the left list to inspect & execute.'}
          </div>
        )}
      </div>
    </div>
  );
};
