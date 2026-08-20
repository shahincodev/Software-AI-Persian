import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Mic, 
  MicOff, 
  Sparkles, 
  Bot, 
  User, 
  ShieldAlert, 
  ShieldCheck, 
  Terminal, 
  CheckCircle2, 
  Copy, 
  Check,
  ChevronRight,
  HelpCircle,
  FileCode
} from 'lucide-react';
import { SessionMessage, Language, ReasoningStageLog } from '../types';
import { ReasoningPipelineView } from './ReasoningPipelineView';

interface AgentChatProps {
  messages: SessionMessage[];
  isLoading: boolean;
  onSendMessage: (prompt: string) => void;
  language: Language;
  currentStages: ReasoningStageLog[];
}

export const AgentChat: React.FC<AgentChatProps> = ({
  messages,
  isLoading,
  onSendMessage,
  language,
  currentStages,
}) => {
  const isFa = language === 'fa';
  const [inputPrompt, setInputPrompt] = useState('');
  const [isVoiceActive, setIsVoiceActive] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, currentStages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputPrompt.trim() || isLoading) return;
    const prompt = inputPrompt;
    setInputPrompt('');
    onSendMessage(prompt);
  };

  const samplePromptsFa = [
    'فایل‌های Downloads من چیست؟',
    'notepad را باز کن و یک یادداشت بنویس',
    'ماشین حساب (Calculator) را باز کن',
    'وضعیت سخت‌افزار و مصرف RAM چقدر است؟',
    'یک پوشه جدید در مسیر D:\\test بساز',
    'اسکرین‌شات از صفحه بگیر و عناصر را با OCR بخوان'
  ];

  const samplePromptsEn = [
    'What files are in my Downloads folder?',
    'Open notepad and write a quick note',
    'Launch Windows Calculator',
    'Show CPU and RAM hardware diagnostics',
    'Create a new folder in D:\\test',
    'Take a desktop screenshot and scan UI text'
  ];

  const samplePrompts = isFa ? samplePromptsFa : samplePromptsEn;

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="flex flex-col h-[750px] bg-slate-900/60 rounded-2xl border border-slate-800 shadow-xl overflow-hidden">
      {/* Chat Messages Stream */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => {
          const isUser = msg.role === 'user';

          return (
            <div
              key={msg.id}
              className={`flex gap-3 max-w-4xl ${isUser ? (isFa ? 'mr-auto flex-row-reverse' : 'ml-auto flex-row') : 'mr-auto'}`}
            >
              {/* Avatar */}
              <div className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
                isUser 
                  ? 'bg-cyan-600 text-white shadow-md' 
                  : 'bg-gradient-to-tr from-slate-800 to-slate-700 text-cyan-400 border border-slate-700'
              }`}>
                {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              {/* Message Bubble */}
              <div className={`flex-1 rounded-2xl p-4 shadow-sm ${
                isUser 
                  ? 'bg-cyan-600/90 text-white font-medium text-sm' 
                  : 'bg-slate-900 border border-slate-800 text-slate-200 text-sm'
              }`}>
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <span className="text-[11px] font-semibold opacity-75">
                    {isUser ? (isFa ? 'شما' : 'User') : (isFa ? 'دستیار هوشمند ویندوز (Software-AI)' : 'Software-AI Agent')}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-slate-400 font-mono">
                      {new Date(msg.timestamp).toLocaleTimeString(isFa ? 'fa-IR' : 'en-US', { hour: '2-digit', minute: '2-digit' })}
                    </span>
                    {!isUser && (
                      <button
                        onClick={() => handleCopy(msg.id, msg.content)}
                        className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-200 transition-colors"
                        title={isFa ? 'کپی متن' : 'Copy'}
                      >
                        {copiedId === msg.id ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                      </button>
                    )}
                  </div>
                </div>

                {/* Content */}
                <div className="whitespace-pre-wrap leading-relaxed">
                  {msg.content}
                </div>

                {/* 8-Stage Reasoning Pipeline Inspector for Assistant Messages */}
                {!isUser && msg.reasoningStages && msg.reasoningStages.length > 0 && (
                  <ReasoningPipelineView stages={msg.reasoningStages} language={language} />
                )}

                {/* Risk Assessment Pill */}
                {!isUser && msg.riskAssessment && (
                  <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-1.5">
                      {msg.riskAssessment.score > 50 ? (
                        <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
                      ) : (
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                      )}
                      <span className="text-slate-400 text-[11px]">
                        {isFa ? 'ارزیابی امنیتی:' : 'Safety Score:'}
                      </span>
                      <span className={`font-mono text-[11px] font-semibold ${
                        msg.riskAssessment.score > 75 
                          ? 'text-rose-400' 
                          : msg.riskAssessment.score > 40 
                          ? 'text-amber-400' 
                          : 'text-emerald-400'
                      }`}>
                        {msg.riskAssessment.score}/100 ({msg.riskAssessment.level})
                      </span>
                    </div>

                    {msg.toolCalls && msg.toolCalls.length > 0 && (
                      <span className="text-[10px] text-slate-500 font-mono">
                        {msg.toolCalls.length} {isFa ? 'ابزار اجرا شد' : 'tools executed'}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Live Loading / Processing State with dynamic reasoning stages */}
        {isLoading && (
          <div className="flex gap-3 max-w-3xl mr-auto animate-in fade-in duration-200">
            <div className="w-8 h-8 rounded-xl bg-slate-800 flex items-center justify-center text-cyan-400 border border-slate-700 animate-pulse">
              <Bot className="w-4 h-4" />
            </div>
            <div className="flex-1 bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-3">
              <div className="flex items-center gap-2 text-xs text-cyan-400 font-medium">
                <Sparkles className="w-4 h-4 animate-spin text-cyan-400" />
                <span>
                  {isFa ? 'در حال پردازش در پایپ‌لاین استدلال هوشمند...' : 'Processing through 8-Stage Reasoning Pipeline...'}
                </span>
              </div>
              <ReasoningPipelineView stages={currentStages} language={language} />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompt Suggestions */}
      <div className="px-4 py-2 bg-slate-950/80 border-t border-slate-800/80">
        <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs no-scrollbar">
          <span className="text-[11px] text-slate-400 font-medium whitespace-nowrap flex items-center gap-1">
            <HelpCircle className="w-3 h-3 text-cyan-400" />
            {isFa ? 'پیشنهادها:' : 'Suggestions:'}
          </span>
          {samplePrompts.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => onSendMessage(prompt)}
              disabled={isLoading}
              className="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-[11px] text-slate-300 whitespace-nowrap hover:text-white transition-all cursor-pointer disabled:opacity-50"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Input Box & Voice Button */}
      <form onSubmit={handleSubmit} className="p-3.5 bg-slate-950 border-t border-slate-800 flex items-center gap-2">
        {/* Voice Simulation Toggle */}
        <button
          type="button"
          onClick={() => {
            setIsVoiceActive(!isVoiceActive);
            if (!isVoiceActive) {
              setInputPrompt(isFa ? 'notepad را باز کن' : 'Open notepad');
            }
          }}
          className={`p-2.5 rounded-xl border transition-all ${
            isVoiceActive
              ? 'bg-rose-500/20 border-rose-500 text-rose-400 animate-pulse'
              : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          }`}
          title={isFa ? 'ورودی صوتی (Voice IO)' : 'Voice Input (Voice IO)'}
        >
          {isVoiceActive ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
        </button>

        {/* Text Input */}
        <input
          type="text"
          value={inputPrompt}
          onChange={(e) => setInputPrompt(e.target.value)}
          placeholder={isFa ? 'دستور خود را بنویسید (مثلاً «فایل‌های Downloads را نشان بده» یا «notepad را باز کن»)...' : 'Type a command (e.g. "What files are in Downloads?" or "Launch Notepad")...'}
          className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-xs md:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
          disabled={isLoading}
        />

        {/* Send Button */}
        <button
          type="submit"
          disabled={!inputPrompt.trim() || isLoading}
          className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium text-xs md:text-sm flex items-center gap-1.5 disabled:opacity-40 disabled:cursor-not-allowed shadow-lg shadow-cyan-600/20 transition-all"
        >
          <span>{isFa ? 'ارسال' : 'Send'}</span>
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
};
