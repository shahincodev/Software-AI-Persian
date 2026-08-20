import React, { useState } from 'react';
import { 
  BrainCircuit, 
  MessageSquare, 
  Plus, 
  Trash2, 
  Search, 
  Sparkles, 
  Bookmark, 
  Check, 
  Cpu, 
  X,
  History,
  Activity
} from 'lucide-react';
import { Session, MemoryItem, ProviderStatus, Language } from '../types';

interface SessionDrawerProps {
  sessions: Session[];
  activeSessionId: string;
  onSelectSession: (id: string) => void;
  onCreateSession: (name: string) => void;
  onDeleteSession: (id: string) => void;
  memories: MemoryItem[];
  onAddMemory: (content: string, category: string) => void;
  onDeleteMemory: (id: string) => void;
  providers: ProviderStatus[];
  language: Language;
}

export const SessionDrawer: React.FC<SessionDrawerProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onCreateSession,
  onDeleteSession,
  memories,
  onAddMemory,
  onDeleteMemory,
  providers,
  language,
}) => {
  const isFa = language === 'fa';
  const [activeTab, setActiveTab] = useState<'sessions' | 'memories' | 'providers'>('sessions');
  const [newSessionName, setNewSessionName] = useState('');
  const [memoryContent, setMemoryContent] = useState('');
  const [memoryCategory, setMemoryCategory] = useState('preference');
  const [searchQuery, setSearchQuery] = useState('');

  const handleCreateSession = () => {
    if (!newSessionName.trim()) return;
    onCreateSession(newSessionName);
    setNewSessionName('');
  };

  const handleCreateMemory = () => {
    if (!memoryContent.trim()) return;
    onAddMemory(memoryContent, memoryCategory);
    setMemoryContent('');
  };

  const filteredSessions = sessions.filter(s => 
    s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (s.summary && s.summary.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const filteredMemories = memories.filter(m =>
    m.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
    m.tags.some(t => t.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="flex flex-col h-[750px] bg-slate-950/60 p-4 rounded-2xl border border-slate-800 space-y-4">
      {/* Sub Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
        <button
          onClick={() => setActiveTab('sessions')}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
            activeTab === 'sessions'
              ? 'bg-cyan-600 text-white shadow-md'
              : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
          }`}
        >
          <MessageSquare className="w-4 h-4" />
          <span>{isFa ? 'نشست‌های مکالمه (Sessions)' : 'Conversation Sessions'}</span>
          <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-black/20 font-mono">
            {sessions.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab('memories')}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
            activeTab === 'memories'
              ? 'bg-cyan-600 text-white shadow-md'
              : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
          }`}
        >
          <BrainCircuit className="w-4 h-4" />
          <span>{isFa ? 'حافظه بلندمدت (Memory)' : 'Long-Term Memory'}</span>
          <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-black/20 font-mono">
            {memories.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab('providers')}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
            activeTab === 'providers'
              ? 'bg-cyan-600 text-white shadow-md'
              : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>{isFa ? 'وضعیت ارائه‌دهندگان API' : 'AI Providers'}</span>
        </button>
      </div>

      {/* 1. SESSIONS TAB */}
      {activeTab === 'sessions' && (
        <div className="flex-1 flex flex-col space-y-3 overflow-hidden">
          {/* Create new session */}
          <div className="flex gap-2">
            <input
              type="text"
              value={newSessionName}
              onChange={(e) => setNewSessionName(e.target.value)}
              placeholder={isFa ? 'نام نشست جدید (مثلاً: تست اتوماسیون)...' : 'New session name...'}
              className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            />
            <button
              onClick={handleCreateSession}
              disabled={!newSessionName.trim()}
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 text-white text-xs font-medium rounded-xl flex items-center gap-1.5 transition-colors shadow"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>{isFa ? 'ایجاد نشست' : 'New Session'}</span>
            </button>
          </div>

          {/* Session List */}
          <div className="flex-1 overflow-y-auto space-y-2">
            {filteredSessions.map((s) => {
              const isActive = s.id === activeSessionId;
              return (
                <div
                  key={s.id}
                  onClick={() => onSelectSession(s.id)}
                  className={`p-3.5 rounded-xl border cursor-pointer flex items-center justify-between transition-all ${
                    isActive
                      ? 'bg-cyan-950/40 border-cyan-500/60 shadow-sm'
                      : 'bg-slate-900/60 border-slate-800 hover:bg-slate-900'
                  }`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-slate-200">{s.name}</span>
                      {isActive && (
                        <span className="text-[10px] px-1.5 py-0.2 rounded bg-cyan-500/20 text-cyan-300 font-mono">
                          {isFa ? 'فعال' : 'Active'}
                        </span>
                      )}
                    </div>
                    {s.summary && (
                      <p className="text-[11px] text-slate-400 line-clamp-1">{s.summary}</p>
                    )}
                    <div className="text-[10px] text-slate-500 font-mono">
                      {s.messageCount} {isFa ? 'پیام' : 'messages'} | {new Date(s.updatedAt).toLocaleTimeString(isFa ? 'fa-IR' : 'en-US')}
                    </div>
                  </div>

                  {sessions.length > 1 && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteSession(s.id);
                      }}
                      className="p-1.5 text-slate-500 hover:text-rose-400 rounded-lg hover:bg-slate-800 transition-colors"
                      title={isFa ? 'حذف نشست' : 'Delete session'}
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 2. MEMORIES TAB */}
      {activeTab === 'memories' && (
        <div className="flex-1 flex flex-col space-y-3 overflow-hidden">
          {/* Add memory form */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5 space-y-2.5">
            <div className="text-xs font-semibold text-slate-200">
              {isFa ? 'ذخیره در حافظه بلندمدت دستیار' : 'Save to Long-Term Memory'}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={memoryContent}
                onChange={(e) => setMemoryContent(e.target.value)}
                placeholder={isFa ? 'محتوای حافظه (مثلاً: همیشه مسیر D:\\test را ترجیح می‌دهم)...' : 'Memory fact or instruction...'}
                className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              />
              <select
                value={memoryCategory}
                onChange={(e) => setMemoryCategory(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-lg px-2 py-1.5 text-xs text-slate-300 focus:outline-none"
              >
                <option value="preference">Preference (ترجیح)</option>
                <option value="fact">Fact (واقعیت)</option>
                <option value="instruction">Instruction (دستور)</option>
                <option value="general">General (عمومی)</option>
              </select>
              <button
                onClick={handleCreateMemory}
                disabled={!memoryContent.trim()}
                className="px-3.5 py-1.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 text-white text-xs font-medium rounded-lg flex items-center gap-1 shadow"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>{isFa ? 'ذخیره' : 'Save'}</span>
              </button>
            </div>
          </div>

          {/* Memories List */}
          <div className="flex-1 overflow-y-auto space-y-2">
            {filteredMemories.map((m) => (
              <div
                key={m.id}
                className="p-3 bg-slate-900/60 border border-slate-800 rounded-xl flex items-start justify-between gap-3"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 font-mono border border-cyan-500/20 uppercase">
                      {m.category}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono">
                      {m.accessCount} {isFa ? 'بار فراخوانی شده' : 'times recalled'}
                    </span>
                  </div>
                  <p className="text-xs text-slate-200 leading-relaxed font-sans">{m.content}</p>
                </div>

                <button
                  onClick={() => onDeleteMemory(m.id)}
                  className="p-1 text-slate-500 hover:text-rose-400 rounded transition-colors"
                  title={isFa ? 'حذف از حافظه' : 'Delete memory'}
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 3. PROVIDERS TAB */}
      {activeTab === 'providers' && (
        <div className="flex-1 overflow-y-auto space-y-3">
          <div className="p-3 bg-cyan-950/30 border border-cyan-800/40 rounded-xl text-xs text-cyan-200">
            {isFa 
              ? 'سیستم به‌صورت خودکار کلیدهای API تنظیم شده در فایل .env را شناسایی کرده و زنجیره هوشمند Failover بین ارائه‌دهندگان برقرار می‌کند.'
              : 'Software-AI automatically detects configured API keys from .env and creates a multi-provider failover chain.'}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {providers.map((p) => (
              <div
                key={p.name}
                className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl space-y-2"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-cyan-400" />
                    <span className="text-xs font-bold text-white">{p.displayName}</span>
                  </div>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-mono ${
                    p.isAvailable
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      : 'bg-slate-800 text-slate-500'
                  }`}>
                    {p.isAvailable ? (isFa ? 'فعال و آماده' : 'Active & Ready') : (isFa ? 'تنظیم نشده' : 'Not Configured')}
                  </span>
                </div>

                <div className="text-[11px] text-slate-400 font-mono">
                  <div>Env: <span className="text-slate-200">{p.envVar}</span></div>
                  {p.latencyMs && <div>Latency: <span className="text-emerald-400">{p.latencyMs}ms</span></div>}
                </div>

                <div className="pt-2 border-t border-slate-800">
                  <div className="text-[10px] text-slate-500 mb-1">{isFa ? 'مدل‌های پشتیبانی شده:' : 'Supported models:'}</div>
                  <div className="flex flex-wrap gap-1">
                    {p.models.map(m => (
                      <span key={m} className="text-[10px] px-1.5 py-0.5 bg-slate-950 text-slate-400 rounded border border-slate-800 font-mono">
                        {m}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
