import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { AgentChat } from './components/AgentChat';
import { DesktopSimulator } from './components/DesktopSimulator';
import { ToolsExplorer } from './components/ToolsExplorer';
import { SystemFilesView } from './components/SystemFilesView';
import { SessionDrawer } from './components/SessionDrawer';
import { SafetyConsentModal } from './components/SafetyConsentModal';
import { 
  Language, 
  SystemHardware, 
  ProviderStatus, 
  Session, 
  SessionMessage, 
  MemoryItem, 
  VirtualApp, 
  ToolDefinition, 
  ReasoningStageLog,
  ConsentRequest
} from './types';
import { Sparkles, X } from 'lucide-react';

export default function App() {
  const [language, setLanguage] = useState<Language>('fa');
  const [activeTab, setActiveTab] = useState<'chat' | 'desktop' | 'tools' | 'files' | 'memory'>('chat');
  const [safetyMode, setSafetyMode] = useState<'strict' | 'standard' | 'power'>('power');
  const [hardware, setHardware] = useState<SystemHardware | null>(null);
  const [providers, setProviders] = useState<ProviderStatus[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string>('session-main');
  const [messages, setMessages] = useState<SessionMessage[]>([]);
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [virtualApps, setVirtualApps] = useState<VirtualApp[]>([]);
  const [tools, setTools] = useState<ToolDefinition[]>([]);
  const [filesystem, setFilesystem] = useState<any>(null);
  const [isLoadingChat, setIsLoadingChat] = useState<boolean>(false);
  const [currentStages, setCurrentStages] = useState<ReasoningStageLog[]>([]);
  const [consentRequest, setConsentRequest] = useState<ConsentRequest | null>(null);
  const [showProvidersModal, setShowProvidersModal] = useState<boolean>(false);

  const isFa = language === 'fa';

  // Sync RTL / LTR document direction
  useEffect(() => {
    document.documentElement.dir = language === 'fa' ? 'rtl' : 'ltr';
    document.documentElement.lang = language;
  }, [language]);

  // Initial Data Fetch
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sysRes, provRes, toolsRes, sessRes, memRes] = await Promise.all([
          fetch('/api/system/status').then(r => r.json()),
          fetch('/api/providers').then(r => r.json()),
          fetch('/api/tools').then(r => r.json()),
          fetch('/api/agent/sessions').then(r => r.json()),
          fetch('/api/agent/memories').then(r => r.json()),
        ]);

        if (sysRes.hardware) setHardware(sysRes.hardware);
        if (sysRes.apps) setVirtualApps(sysRes.apps);
        if (sysRes.files) setFilesystem(sysRes.files);
        if (provRes.providers) setProviders(provRes.providers);
        if (toolsRes.tools) setTools(toolsRes.tools);
        if (sessRes.sessions) setSessions(sessRes.sessions);
        if (memRes.memories) setMemories(memRes.memories);

        // Fetch messages for initial session
        const msgRes = await fetch(`/api/agent/sessions/session-main/messages`).then(r => r.json());
        if (msgRes.messages) setMessages(msgRes.messages);
      } catch (err) {
        console.error('Failed to fetch initial state:', err);
      }
    };

    fetchData();
  }, []);

  // Poll hardware telemetry periodically
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch('/api/system/status').then(r => r.json());
        if (res.hardware) setHardware(res.hardware);
      } catch {
        // ignore
      }
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  // Switch Session
  const handleSelectSession = async (sessionId: string) => {
    setActiveSessionId(sessionId);
    try {
      const res = await fetch(`/api/agent/sessions/${sessionId}/messages`).then(r => r.json());
      setMessages(res.messages || []);
    } catch (err) {
      console.error('Failed to load session messages:', err);
    }
  };

  // Create Session
  const handleCreateSession = async (name: string) => {
    try {
      const res = await fetch('/api/agent/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, tags: ['custom'] })
      }).then(r => r.json());

      if (res.session) {
        setSessions(prev => [res.session, ...prev]);
        setActiveSessionId(res.session.id);
        setMessages([]);
      }
    } catch (err) {
      console.error('Failed to create session:', err);
    }
  };

  // Delete Session
  const handleDeleteSession = async (sessionId: string) => {
    try {
      const res = await fetch(`/api/agent/sessions/${sessionId}`, { method: 'DELETE' }).then(r => r.json());
      if (res.remainingSessions) {
        setSessions(res.remainingSessions);
        if (activeSessionId === sessionId && res.remainingSessions.length > 0) {
          handleSelectSession(res.remainingSessions[0].id);
        }
      }
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  // Send Message through Agent
  const handleSendMessage = async (prompt: string) => {
    setIsLoadingChat(true);

    // Initial progressive reasoning stages simulation
    setCurrentStages([
      { id: 'understand', name: 'Understand', nameFa: '۱. درک نیت کاربر (Understand)', status: 'active', detailsFa: 'تحلیل گرامری و استخراج افعال و اهداف', durationMs: 40 },
      { id: 'think', name: 'Think', nameFa: '۲. تفکر و تحلیل پیش‌نیازها (Think)', status: 'pending', detailsFa: 'ارزیابی مدل‌های زبانی و حافظه سیستم' },
      { id: 'plan', name: 'Plan', nameFa: '۳. تدوین برنامه اجرایی (Plan)', status: 'pending', detailsFa: 'انتخاب از بین ۲۰ ابزار کانونی' },
      { id: 'observe', name: 'Observe', nameFa: '۴. مشاهده وضعیت دسکتاپ (Observe)', status: 'pending', detailsFa: 'بررسی OCR و پنجره‌های فعال' },
      { id: 'execute', name: 'Execute', nameFa: '۵. اجرای ابزارهای سیستمی (Execute)', status: 'pending', detailsFa: 'اجرای دستورات و فرامین' },
      { id: 'review', name: 'Review', nameFa: '۶. بازبینی خودکار نتایج (Review)', status: 'pending', detailsFa: 'تایید نتیجه خروجی' },
      { id: 'recover', name: 'Recover', nameFa: '۷. بازیابی در صورت خطا (Recover)', status: 'pending', detailsFa: 'مدیریت خطا و تلاش مجدد' },
      { id: 'continue', name: 'Continue', nameFa: '۸. جمع‌بندی و ادامه مکالمه (Continue)', status: 'pending', detailsFa: 'ذخیره نشست' },
    ]);

    try {
      const res = await fetch('/api/agent/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          sessionId: activeSessionId,
          language
        })
      }).then(r => r.json());

      if (res.userMessage && res.assistantMessage) {
        setMessages(prev => [...prev, res.userMessage, res.assistantMessage]);
      }

      // Refresh apps state
      const sysRes = await fetch('/api/system/status').then(r => r.json());
      if (sysRes.apps) setVirtualApps(sysRes.apps);
    } catch (err) {
      console.error('Chat error:', err);
    } finally {
      setIsLoadingChat(false);
      setCurrentStages([]);
    }
  };

  // Toggle Virtual Apps in Desktop
  const handleToggleApp = async (appId: string, action: 'open' | 'close' | 'minimize' | 'focus') => {
    try {
      const res = await fetch('/api/system/apps/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ appId, action })
      }).then(r => r.json());
      if (res.allApps) {
        setVirtualApps(res.allApps);
      }
    } catch (err) {
      console.error('App toggle error:', err);
    }
  };

  // Execute Tool Directly
  const handleExecuteTool = async (toolName: string, params: Record<string, any>) => {
    const res = await fetch('/api/agent/execute-tool', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tool: toolName, params })
    }).then(r => r.json());

    // Refresh apps
    const sysRes = await fetch('/api/system/status').then(r => r.json());
    if (sysRes.apps) setVirtualApps(sysRes.apps);

    return res;
  };

  // Filesystem Actions
  const handleReadFile = async (path: string) => {
    const res = await handleExecuteTool('read_file', { path });
    return res.output?.content || '';
  };

  const handleCreateFolder = async (path: string) => {
    await handleExecuteTool('create_folder', { path });
  };

  const handleDeleteFile = async (path: string) => {
    await handleExecuteTool('delete_file', { path });
  };

  // Memory Actions
  const handleAddMemory = async (content: string, category: string) => {
    try {
      const res = await fetch('/api/agent/memories', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content, category, tags: [category] })
      }).then(r => r.json());
      if (res.memory) {
        setMemories(prev => [res.memory, ...prev]);
      }
    } catch (err) {
      console.error('Failed to save memory:', err);
    }
  };

  const handleDeleteMemory = async (id: string) => {
    try {
      const res = await fetch(`/api/agent/memories/${id}`, { method: 'DELETE' }).then(r => r.json());
      if (res.memories) {
        setMemories(res.memories);
      }
    } catch (err) {
      console.error('Failed to delete memory:', err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Header */}
      <Header
        language={language}
        onLanguageChange={setLanguage}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        hardware={hardware}
        providers={providers}
        onOpenProvidersModal={() => setShowProvidersModal(true)}
        safetyMode={safetyMode}
        onSafetyModeChange={setSafetyMode}
      />

      {/* Main App Canvas */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6">
        {activeTab === 'chat' && (
          <AgentChat
            messages={messages}
            isLoading={isLoadingChat}
            onSendMessage={handleSendMessage}
            language={language}
            currentStages={currentStages}
          />
        )}

        {activeTab === 'desktop' && (
          <DesktopSimulator
            apps={virtualApps}
            onToggleApp={handleToggleApp}
            language={language}
            onExecutePrompt={handleSendMessage}
          />
        )}

        {activeTab === 'tools' && (
          <ToolsExplorer
            tools={tools}
            onExecuteTool={handleExecuteTool}
            language={language}
          />
        )}

        {activeTab === 'files' && (
          <SystemFilesView
            filesystem={filesystem}
            language={language}
            onReadFile={handleReadFile}
            onCreateFolder={handleCreateFolder}
            onDeleteFile={handleDeleteFile}
          />
        )}

        {activeTab === 'memory' && (
          <SessionDrawer
            sessions={sessions}
            activeSessionId={activeSessionId}
            onSelectSession={handleSelectSession}
            onCreateSession={handleCreateSession}
            onDeleteSession={handleDeleteSession}
            memories={memories}
            onAddMemory={handleAddMemory}
            onDeleteMemory={handleDeleteMemory}
            providers={providers}
            language={language}
          />
        )}
      </main>

      {/* AI Providers Info Modal */}
      {showProvidersModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-cyan-400" />
                <h3 className="text-sm font-bold text-white">
                  {isFa ? 'ارائه‌دهندگان هوش مصنوعی و زنجیره Failover' : 'AI Providers & Failover Chain'}
                </h3>
              </div>
              <button
                onClick={() => setShowProvidersModal(false)}
                className="p-1 hover:bg-slate-800 rounded text-slate-400"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              {isFa 
                ? 'پروژه Software-AI از چندین ارائه‌دهنده پشتیبانی می‌کند (Google Gemini, Groq, OpenRouter, OpenAI, Ollama). ارائه‌دهنده فعال بر اساس کلیدهای API شناسایی می‌شود.'
                : 'Software-AI supports a multi-provider failover chain. It detects available API keys at runtime and automatically routes requests to available models.'}
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-72 overflow-y-auto">
              {providers.map((p) => (
                <div key={p.name} className="p-3.5 bg-slate-950 border border-slate-800 rounded-xl space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-200">{p.displayName}</span>
                    <span className={`text-[10px] px-1.5 py-0.2 rounded font-mono ${
                      p.isAvailable ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-800 text-slate-500'
                    }`}>
                      {p.isAvailable ? (isFa ? 'فعال' : 'Active') : (isFa ? 'غیرفعال' : 'Disabled')}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-400 font-mono">
                    <div>{p.envVar}</div>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setShowProvidersModal(false)}
                className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-medium"
              >
                {isFa ? 'بستن' : 'Close'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Safety Consent Confirmation Modal */}
      <SafetyConsentModal
        request={consentRequest}
        onApprove={() => setConsentRequest(null)}
        onReject={() => setConsentRequest(null)}
        language={language}
      />
    </div>
  );
}
