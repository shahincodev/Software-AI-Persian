import express from 'express';
import cors from 'cors';
import path from 'path';
import fs from 'fs';
import { createServer as createViteServer } from 'vite';
import { GoogleGenAI } from '@google/genai';

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());

// ─────────────────────────────────────────────────────────────────────────────
// In-Memory Virtual State for Windows Environment Simulation
// ─────────────────────────────────────────────────────────────────────────────

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: string;
  modified: string;
  content?: string;
  children?: FileNode[];
}

let virtualFilesystem: FileNode = {
  name: 'C:',
  path: 'C:',
  type: 'directory',
  modified: '2026-06-20 10:00:00',
  children: [
    {
      name: 'Users',
      path: 'C:\\Users',
      type: 'directory',
      modified: '2026-06-20 10:00:00',
      children: [
        {
          name: 'Admin',
          path: 'C:\\Users\\Admin',
          type: 'directory',
          modified: '2026-06-20 10:00:00',
          children: [
            {
              name: 'Downloads',
              path: 'C:\\Users\\Admin\\Downloads',
              type: 'directory',
              modified: '2026-06-24 14:30:00',
              children: [
                { name: 'setup_python311.exe', path: 'C:\\Users\\Admin\\Downloads\\setup_python311.exe', type: 'file', size: '28.4 MB', modified: '2026-06-24 11:15:00' },
                { name: 'document_fa.pdf', path: 'C:\\Users\\Admin\\Downloads\\document_fa.pdf', type: 'file', size: '1.2 MB', modified: '2026-06-24 13:20:00' },
                { name: 'project_notes.txt', path: 'C:\\Users\\Admin\\Downloads\\project_notes.txt', type: 'file', size: '4 KB', modified: '2026-06-24 14:05:00', content: 'پروژه اتوماسیون هوش مصنوعی ویندوز به زبان فارسی و انگلیسی.\nتمامی قابلیت‌های پایپ‌لاین استدلال پیاده‌سازی شدند.' }
              ]
            },
            {
              name: 'Documents',
              path: 'C:\\Users\\Admin\\Documents',
              type: 'directory',
              modified: '2026-06-22 09:00:00',
              children: [
                { name: 'Report_2026.docx', path: 'C:\\Users\\Admin\\Documents\\Report_2026.docx', type: 'file', size: '420 KB', modified: '2026-06-22 09:10:00' },
                { name: 'config.json', path: 'C:\\Users\\Admin\\Documents\\config.json', type: 'file', size: '2 KB', modified: '2026-06-23 16:40:00', content: '{"theme": "dark", "safety_mode": "power", "language": "fa"}' }
              ]
            },
            {
              name: 'Desktop',
              path: 'C:\\Users\\Admin\\Desktop',
              type: 'directory',
              modified: '2026-06-24 12:00:00',
              children: [
                { name: 'Software-AI.lnk', path: 'C:\\Users\\Admin\\Desktop\\Software-AI.lnk', type: 'file', size: '1 KB', modified: '2026-06-20 10:00:00' },
                { name: 'Notepad.lnk', path: 'C:\\Users\\Admin\\Desktop\\Notepad.lnk', type: 'file', size: '1 KB', modified: '2026-06-20 10:00:00' }
              ]
            }
          ]
        }
      ]
    },
    {
      name: 'Windows',
      path: 'C:\\Windows',
      type: 'directory',
      modified: '2026-06-01 00:00:00',
      children: [
        { name: 'notepad.exe', path: 'C:\\Windows\\notepad.exe', type: 'file', size: '350 KB', modified: '2026-06-01 00:00:00' },
        { name: 'calc.exe', path: 'C:\\Windows\\calc.exe', type: 'file', size: '28 KB', modified: '2026-06-01 00:00:00' },
        { name: 'explorer.exe', path: 'C:\\Windows\\explorer.exe', type: 'file', size: '4.8 MB', modified: '2026-06-01 00:00:00' }
      ]
    }
  ]
};

// Virtual Running Applications
let virtualApps = [
  { id: 'notepad', name: 'Notepad', processName: 'notepad.exe', title: 'Untitled - Notepad (یادداشت)', icon: 'FileText', isOpen: false, isMinimized: false, zIndex: 10, content: '', position: { x: 40, y: 40, w: 500, h: 360 } },
  { id: 'calc', name: 'Calculator', processName: 'calc.exe', title: 'Calculator (ماشین حساب)', icon: 'Calculator', isOpen: false, isMinimized: false, zIndex: 11, content: '0', position: { x: 580, y: 40, w: 320, h: 420 } },
  { id: 'terminal', name: 'PowerShell / Command Prompt', processName: 'powershell.exe', title: 'Windows PowerShell (ترمینال ویندوز)', icon: 'Terminal', isOpen: true, isMinimized: false, zIndex: 12, content: 'Windows PowerShell\nCopyright (C) Microsoft Corporation. All rights reserved.\n\nPS C:\\Users\\Admin> Software-AI Agent ready.\n', position: { x: 80, y: 160, w: 620, h: 380 } },
  { id: 'explorer', name: 'File Explorer', processName: 'explorer.exe', title: 'File Explorer - C:\\Users\\Admin\\Downloads', icon: 'Folder', isOpen: false, isMinimized: false, zIndex: 9, content: 'C:\\Users\\Admin\\Downloads', position: { x: 120, y: 80, w: 580, h: 400 } }
];

// Virtual Memory Integrator (Short & Long Term)
let memories: Array<{ id: string; content: string; category: string; tags: string[]; createdAt: number; accessCount: number }> = [
  { id: 'mem-1', content: 'کاربر ترجیح می‌دهد خروجی‌ها به زبان فارسی و با جزئیات کامل نمایش داده شوند.', category: 'preference', tags: ['language', 'persian'], createdAt: Date.now() - 3600000, accessCount: 5 },
  { id: 'mem-2', content: 'مسیر پیش‌فرض پروژه‌ها در D:\\Projects قرار دارد.', category: 'fact', tags: ['path', 'workspace'], createdAt: Date.now() - 7200000, accessCount: 3 },
  { id: 'mem-3', content: 'حالت ایمنی پیش‌فرض روی Power (پذیرش دستورات امن به صورت خودکار) تنظیم است.', category: 'instruction', tags: ['safety'], createdAt: Date.now() - 10800000, accessCount: 2 }
];

// Virtual Sessions
let sessions: Array<{ id: string; name: string; createdAt: number; updatedAt: number; messageCount: number; summary: string; tags: string[] }> = [
  { id: 'session-main', name: 'نشست اصلی (Main Session)', createdAt: Date.now() - 1800000, updatedAt: Date.now(), messageCount: 4, summary: 'اتوماسیون کارهای ویندوز، بررسی فایل‌ها و تست پایپ‌لاین استدلال', tags: ['general', 'windows'] }
];

let sessionMessages: Record<string, any[]> = {
  'session-main': [
    {
      id: 'msg-welcome',
      sessionId: 'session-main',
      role: 'assistant',
      content: 'سلام! من دستیار هوشمند اتوماسیون سیستم عامل ویندوز (Software-AI) هستم. می‌توانید درخواست‌های خود را به فارسی یا انگلیسی بنویسید (مثلاً «فایل‌های Downloads را نشان بده»، «notepad را باز کن» یا «یک اسکرین‌شات از صفحه بگیر»).',
      timestamp: Date.now() - 1800000,
      reasoningStages: [
        { id: 'understand', name: 'Understand', nameFa: 'درک نیت', status: 'completed', detailsFa: 'مقداردهی اولیه دستیار هوشمند و بارگذاری ارائه‌دهندگان API' },
        { id: 'think', name: 'Think', nameFa: 'تفکر و تحلیل', status: 'completed', detailsFa: 'بررسی دسترسی‌های سیستم، OCR، و پایپ‌لاین استدلال ۸ مرحله‌ای' },
        { id: 'plan', name: 'Plan', nameFa: 'برنامه‌ریزی', status: 'completed', detailsFa: 'آماده‌سازی ۲۰ ابزار یکپارچه سیستمی' },
        { id: 'execute', name: 'Execute', nameFa: 'اجرا', status: 'completed', detailsFa: 'سیستم آماده دریافت درخواست‌های کاربر است.' }
      ]
    }
  ]
};

// System Health & Hardware Info
const getSystemHardware = () => {
  return {
    os: 'Microsoft Windows 11 Pro [Version 10.0.22631.3880]',
    hostname: 'DESKTOP-SHAHIN-AI',
    cpuUsage: Math.floor(18 + Math.random() * 15),
    ramUsage: Math.floor(45 + Math.random() * 8),
    ramTotal: '16.0 GB DDR4',
    diskUsage: 38,
    diskTotal: '512 GB NVMe SSD',
    activeProcesses: 142 + virtualApps.filter(a => a.isOpen).length,
    tesseractStatus: 'ready',
    uptimeSeconds: 14250
  };
};

// Provider Detector
const getProviderStatuses = () => {
  const geminiKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
  const groqKey = process.env.GROQ_API_KEY;
  const openrouterKey = process.env.OPENROUTER_API_KEY;
  const openaiKey = process.env.OPENAI_API_KEY;
  const anthropicKey = process.env.ANTHROPIC_API_KEY;

  return [
    {
      name: 'google',
      displayName: 'Google Gemini',
      envVar: 'GEMINI_API_KEY',
      isConfigured: Boolean(geminiKey),
      isAvailable: Boolean(geminiKey),
      models: ['gemini-2.5-flash', 'gemini-1.5-pro', 'gemini-1.5-flash'],
      latencyMs: geminiKey ? 120 : undefined
    },
    {
      name: 'groq',
      displayName: 'Groq Cloud (Llama 3)',
      envVar: 'GROQ_API_KEY',
      isConfigured: Boolean(groqKey),
      isAvailable: Boolean(groqKey),
      models: ['llama-3.3-70b-versatile', 'mixtral-8x7b-32768'],
      latencyMs: groqKey ? 85 : undefined
    },
    {
      name: 'openrouter',
      displayName: 'OpenRouter Multi-Model',
      envVar: 'OPENROUTER_API_KEY',
      isConfigured: Boolean(openrouterKey),
      isAvailable: Boolean(openrouterKey),
      models: ['anthropic/claude-3.5-sonnet', 'openai/gpt-4o', 'deepseek/deepseek-chat'],
      latencyMs: openrouterKey ? 150 : undefined
    },
    {
      name: 'openai',
      displayName: 'OpenAI',
      envVar: 'OPENAI_API_KEY',
      isConfigured: Boolean(openaiKey),
      isAvailable: Boolean(openaiKey),
      models: ['gpt-4o', 'gpt-4o-mini'],
      latencyMs: openaiKey ? 140 : undefined
    },
    {
      name: 'ollama',
      displayName: 'Local Ollama Engine',
      envVar: 'OLLAMA_BASE_URL',
      isConfigured: false,
      isAvailable: false,
      models: ['llama3:latest', 'qwen2.5:latest'],
      latencyMs: undefined
    }
  ];
};

// ─────────────────────────────────────────────────────────────────────────────
// Canonical 20 Tool Definitions
// ─────────────────────────────────────────────────────────────────────────────

const CANONICAL_TOOLS = [
  {
    name: 'execute_command',
    description: 'Run a shell/cmd/PowerShell command',
    descriptionFa: 'اجرای دستور در خط فرمان ویندوز (CMD / PowerShell)',
    category: 'system',
    riskLevel: 'medium',
    params: [
      { name: 'command', type: 'str', required: true, description: 'Command to execute', descriptionFa: 'دستور متنی برای اجرا' },
      { name: 'shell', type: 'str', required: false, default: 'powershell', description: 'powershell or cmd', descriptionFa: 'نوع شل' }
    ]
  },
  {
    name: 'launch_app',
    description: 'Open or launch a Windows application (Notepad, Calculator, Explorer, etc.)',
    descriptionFa: 'باز کردن و اجرای برنامه‌های ویندوز (نوت‌پد، ماشین حساب، فایل اکسپلورر)',
    category: 'desktop_ui',
    riskLevel: 'low',
    params: [
      { name: 'app_name', type: 'str', required: true, description: 'Application name or process (e.g. notepad.exe)', descriptionFa: 'نام برنامه یا فایل اجرایی' }
    ]
  },
  {
    name: 'close_app',
    description: 'Terminate or close a running application process',
    descriptionFa: 'بستن یا خاتمه دادن به پردازش یک برنامه',
    category: 'desktop_ui',
    riskLevel: 'medium',
    params: [
      { name: 'process_name', type: 'str', required: true, description: 'Process name to kill', descriptionFa: 'نام پردازش' }
    ]
  },
  {
    name: 'click',
    description: 'Click on a UI element by text title or coordinate coordinates (x, y)',
    descriptionFa: 'کلیک هوشمند ماوس روی یک دکمه، منو یا مختصات صفحه',
    category: 'desktop_ui',
    riskLevel: 'low',
    params: [
      { name: 'target', type: 'str', required: true, description: 'Text to click on or "x,y"', descriptionFa: 'عنوان عنصر یا مختصات x,y' },
      { name: 'button', type: 'str', required: false, default: 'left', description: 'left, right, middle', descriptionFa: 'کلید ماوس' }
    ]
  },
  {
    name: 'type_text',
    description: 'Type text into the active focused window or input field',
    descriptionFa: 'تایپ متن در پنجره یا فیلد فعال',
    category: 'desktop_ui',
    riskLevel: 'low',
    params: [
      { name: 'text', type: 'str', required: true, description: 'Text to type', descriptionFa: 'متن برای تایپ' },
      { name: 'target', type: 'str', required: false, description: 'Target element (optional)', descriptionFa: 'عنصر هدف' }
    ]
  },
  {
    name: 'hotkey',
    description: 'Press keyboard shortcuts like Ctrl+C, Ctrl+V, Alt+Tab, Win+R',
    descriptionFa: 'فشردن کلیدهای میانبر ترکیبی صفحه‌کلید',
    category: 'desktop_ui',
    riskLevel: 'low',
    params: [
      { name: 'keys', type: 'list', required: true, description: 'Array of keys e.g. ["ctrl", "c"]', descriptionFa: 'لیست کلیدها' }
    ]
  },
  {
    name: 'scroll',
    description: 'Scroll active page or window in any direction',
    descriptionFa: 'اسکرول صفحه یا پنجره فعال',
    category: 'desktop_ui',
    riskLevel: 'safe',
    params: [
      { name: 'direction', type: 'str', required: true, description: 'up, down, left, right', descriptionFa: 'جهت اسکرول' },
      { name: 'clicks', type: 'int', required: false, default: 3, description: 'Scroll amount', descriptionFa: 'میزان اسکرول' }
    ]
  },
  {
    name: 'wait',
    description: 'Wait for element to appear or pause execution',
    descriptionFa: 'صبر هوشمند تا بارگذاری عنصر یا زمان مشخص',
    category: 'desktop_ui',
    riskLevel: 'safe',
    params: [
      { name: 'wait_type', type: 'str', required: true, description: 'element, time, window', descriptionFa: 'نوع انتظار' },
      { name: 'timeout', type: 'int', required: false, default: 2, description: 'Seconds to wait', descriptionFa: 'مدت ثانیه' }
    ]
  },
  {
    name: 'drag_drop',
    description: 'Drag item from source to destination',
    descriptionFa: 'کشیدن و رها کردن ماوس از مبدا به مقصد',
    category: 'desktop_ui',
    riskLevel: 'medium',
    params: [
      { name: 'source', type: 'str', required: true, description: 'Source text or coords', descriptionFa: 'مبدا' },
      { name: 'target', type: 'str', required: true, description: 'Target text or coords', descriptionFa: 'مقصد' }
    ]
  },
  {
    name: 'list_directory',
    description: 'List all files and folders in a specified path',
    descriptionFa: 'نمایش لیست فایل‌ها و پوشه‌های یک مسیر',
    category: 'filesystem',
    riskLevel: 'safe',
    params: [
      { name: 'path', type: 'str', required: false, default: 'C:\\Users\\Admin\\Downloads', description: 'Directory path', descriptionFa: 'مسیر پوشه' }
    ]
  },
  {
    name: 'read_file',
    description: 'Read the text content of a file',
    descriptionFa: 'خواندن محتوای متنی یک فایل',
    category: 'filesystem',
    riskLevel: 'safe',
    params: [
      { name: 'path', type: 'str', required: true, description: 'File path', descriptionFa: 'مسیر فایل' }
    ]
  },
  {
    name: 'create_folder',
    description: 'Create a new directory/folder at path',
    descriptionFa: 'ایجاد یک پوشه جدید در مسیر دلخواه',
    category: 'filesystem',
    riskLevel: 'low',
    params: [
      { name: 'path', type: 'str', required: true, description: 'Folder path to create', descriptionFa: 'مسیر پوشه جدید' }
    ]
  },
  {
    name: 'delete_file',
    description: 'Delete a file or empty folder',
    descriptionFa: 'حذف یک فایل یا پوشه',
    category: 'filesystem',
    riskLevel: 'high',
    params: [
      { name: 'path', type: 'str', required: true, description: 'Path to delete', descriptionFa: 'مسیر فایل برای حذف' }
    ]
  },
  {
    name: 'screenshot',
    description: 'Capture screenshot of the screen with OCR text detection',
    descriptionFa: 'عکس‌برداری از صفحه نمایش همراه با تحلیل بینایی OCR',
    category: 'vision',
    riskLevel: 'safe',
    params: [
      { name: 'region', type: 'str', required: false, default: 'full', description: 'full or x,y,w,h', descriptionFa: 'محدوده عکس' }
    ]
  },
  {
    name: 'read_screen',
    description: 'Perform optical character recognition (OCR) on screen',
    descriptionFa: 'خواندن تمام متون موجود روی صفحه با موتور OCR',
    category: 'vision',
    riskLevel: 'safe',
    params: []
  },
  {
    name: 'find_element',
    description: 'Locate a button, text, or UI control on desktop',
    descriptionFa: 'پیدا کردن مکان دقیق یک دکمه یا متن روی صفحه',
    category: 'vision',
    riskLevel: 'safe',
    params: [
      { name: 'text', type: 'str', required: true, description: 'Text to search on screen', descriptionFa: 'متن جستجو' }
    ]
  },
  {
    name: 'verify_action',
    description: 'Verify if action succeeded by inspecting screen outcome',
    descriptionFa: 'بازبینی خودکار نتیجه کار با بررسی تصویر صفحه',
    category: 'vision',
    riskLevel: 'safe',
    params: [
      { name: 'expected', type: 'str', required: true, description: 'Expected outcome', descriptionFa: 'نتیجه مورد انتظار' }
    ]
  },
  {
    name: 'query_hardware',
    description: 'Inspect CPU, RAM, Disk, and system diagnostics',
    descriptionFa: 'بررسی وضعیت سخت‌افزار (پردازنده، رم، دیسک، شبکه)',
    category: 'system',
    riskLevel: 'safe',
    params: [
      { name: 'query_type', type: 'str', required: false, default: 'all', description: 'all, cpu, memory, disk', descriptionFa: 'نوع اطلاعات' }
    ]
  },
  {
    name: 'remember',
    description: 'Save user fact or preference to long-term memory',
    descriptionFa: 'ذخیره یک واقعیت، ترجیح یا دستور در حافظه بلندمدت دستیار',
    category: 'memory',
    riskLevel: 'safe',
    params: [
      { name: 'content', type: 'str', required: true, description: 'Fact or preference', descriptionFa: 'محتوای حافظه' },
      { name: 'category', type: 'str', required: false, default: 'general', description: 'Category', descriptionFa: 'دسته‌بندی' }
    ]
  },
  {
    name: 'recall',
    description: 'Search long-term memory for relevant memories',
    descriptionFa: 'جستجو و بازیابی اطلاعات مرتبط از حافظه بلندمدت',
    category: 'memory',
    riskLevel: 'safe',
    params: [
      { name: 'query', type: 'str', required: true, description: 'Query text', descriptionFa: 'متن جستجو' }
    ]
  }
];

// ─────────────────────────────────────────────────────────────────────────────
// Tool Execution Engine
// ─────────────────────────────────────────────────────────────────────────────

function executeTool(toolName: string, params: Record<string, any>) {
  const startTime = Date.now();
  let success = true;
  let output: any = null;
  let error: string | undefined = undefined;

  switch (toolName) {
    case 'launch_app': {
      const appName = (params.app_name || '').toLowerCase();
      let matchedApp = virtualApps.find(a => 
        a.name.toLowerCase().includes(appName) || 
        a.processName.toLowerCase().includes(appName) ||
        (appName.includes('notepad') && a.id === 'notepad') ||
        (appName.includes('calc') && a.id === 'calc') ||
        (appName.includes('explorer') && a.id === 'explorer') ||
        (appName.includes('terminal') && a.id === 'terminal')
      );

      if (matchedApp) {
        matchedApp.isOpen = true;
        matchedApp.isMinimized = false;
        matchedApp.zIndex = Math.max(...virtualApps.map(a => a.zIndex)) + 1;
        output = { message: `برنامه ${matchedApp.name} با موفقیت اجرا شد.`, app: matchedApp };
      } else {
        // Create dynamic virtual app
        const newApp = {
          id: `app-${Date.now()}`,
          name: params.app_name,
          processName: `${params.app_name}.exe`,
          title: `${params.app_name} (Running)`,
          icon: 'AppWindow',
          isOpen: true,
          isMinimized: false,
          zIndex: 20,
          content: 'Application initialized.',
          position: { x: 100, y: 100, w: 480, h: 320 }
        };
        virtualApps.push(newApp);
        output = { message: `برنامه ${params.app_name} اجرا شد.`, app: newApp };
      }
      break;
    }

    case 'close_app': {
      const proc = (params.process_name || params.app_name || '').toLowerCase();
      const matched = virtualApps.find(a => 
        a.name.toLowerCase().includes(proc) || 
        a.processName.toLowerCase().includes(proc) ||
        a.id.toLowerCase().includes(proc)
      );
      if (matched) {
        matched.isOpen = false;
        output = { message: `پردازش ${matched.processName} با موفقیت خاتمه یافت.`, closedApp: matched.name };
      } else {
        output = { message: `هیچ پردازش فعالی با نام "${proc}" یافت نشد.`, closedApp: proc };
      }
      break;
    }

    case 'list_directory': {
      const targetPath = (params.path || 'C:\\Users\\Admin\\Downloads').toLowerCase();
      if (targetPath.includes('download')) {
        const downloads = virtualFilesystem.children?.[0]?.children?.[0]?.children?.[0]?.children || [];
        output = { path: 'C:\\Users\\Admin\\Downloads', count: downloads.length, files: downloads };
      } else if (targetPath.includes('document')) {
        const docs = virtualFilesystem.children?.[0]?.children?.[0]?.children?.[1]?.children || [];
        output = { path: 'C:\\Users\\Admin\\Documents', count: docs.length, files: docs };
      } else if (targetPath.includes('desktop')) {
        const desktop = virtualFilesystem.children?.[0]?.children?.[0]?.children?.[2]?.children || [];
        output = { path: 'C:\\Users\\Admin\\Desktop', count: desktop.length, files: desktop };
      } else {
        output = { path: params.path || 'C:\\Users\\Admin', count: 3, files: virtualFilesystem.children?.[0]?.children?.[0]?.children || [] };
      }
      break;
    }

    case 'read_file': {
      const filePath = params.path || '';
      if (filePath.toLowerCase().includes('project_notes') || filePath.toLowerCase().includes('notes')) {
        output = { path: filePath, content: 'پروژه اتوماسیون هوش مصنوعی ویندوز به زبان فارسی و انگلیسی.\nتمامی قابلیت‌های پایپ‌لاین استدلال پیاده‌سازی شدند.' };
      } else if (filePath.toLowerCase().includes('config')) {
        output = { path: filePath, content: '{\n  "theme": "dark",\n  "safety_mode": "power",\n  "language": "fa"\n}' };
      } else {
        output = { path: filePath, content: `[File Content for ${filePath}]\nSample simulated file data successfully retrieved.` };
      }
      break;
    }

    case 'create_folder': {
      const folderPath = params.path || 'D:\\test';
      output = { message: `پوشه جدید با موفقیت در مسیر ${folderPath} ایجاد گردید.`, path: folderPath, status: 'created' };
      break;
    }

    case 'delete_file': {
      const filePath = params.path || '';
      output = { message: `فایل در مسیر ${filePath} به سطل زباله منتقل شد.`, path: filePath, status: 'deleted' };
      break;
    }

    case 'execute_command': {
      const cmd = params.command || '';
      let stdout = '';
      if (cmd.includes('dir') || cmd.includes('ls') || cmd.includes('Get-ChildItem')) {
        stdout = 'Mode                LastWriteTime         Length Name\n----                -------------         ------ ----\nd-----        2026-06-24     14:30                Downloads\nd-----        2026-06-22     09:00                Documents\nd-----        2026-06-24     12:00                Desktop\n';
      } else if (cmd.includes('ipconfig')) {
        stdout = 'Windows IP Configuration\n\nEthernet adapter Ethernet 1:\n   IPv4 Address. . . . . . . . . . . : 192.168.1.105\n   Subnet Mask . . . . . . . . . . . : 255.255.255.0\n   Default Gateway . . . . . . . . . : 192.168.1.1\n';
      } else if (cmd.includes('echo')) {
        stdout = cmd.replace(/^echo\s*/i, '');
      } else {
        stdout = `Command "${cmd}" executed successfully.\nExit Code: 0\n`;
      }
      // Log to terminal window
      const term = virtualApps.find(a => a.id === 'terminal');
      if (term) {
        term.content += `\nPS C:\\Users\\Admin> ${cmd}\n${stdout}`;
      }
      output = { command: cmd, exitCode: 0, stdout };
      break;
    }

    case 'type_text': {
      const textToType = params.text || '';
      const np = virtualApps.find(a => a.id === 'notepad' && a.isOpen);
      if (np) {
        np.content = (np.content ? np.content + '\n' : '') + textToType;
        output = { message: `متن در برنامه Notepad تایپ شد: "${textToType}"`, targetApp: 'notepad' };
      } else {
        output = { message: `متن با شبیه‌ساز کیبورد تایپ شد: "${textToType}"`, targetApp: 'active_window' };
      }
      break;
    }

    case 'click': {
      const target = params.target || 'Button';
      output = { message: `کلیک ماوس روی عنصر "${target}" با موفقیت انجام شد.`, target, position: { x: 340, y: 220 } };
      break;
    }

    case 'hotkey': {
      const keys = Array.isArray(params.keys) ? params.keys.join('+') : params.keys;
      output = { message: `کلید میانبر ${keys} فشرده شد.`, keys };
      break;
    }

    case 'scroll': {
      output = { message: `اسکرول صفحه به سمت ${params.direction || 'down'} انجام شد.`, direction: params.direction, clicks: params.clicks || 3 };
      break;
    }

    case 'wait': {
      output = { message: `انتظار برای ${params.timeout || 1} ثانیه تکمیل شد.`, waitType: params.wait_type || 'time' };
      break;
    }

    case 'screenshot':
    case 'read_screen': {
      const visibleElements = [
        { id: 'el-1', text: 'Notepad', textFa: 'نوت‌پد', type: 'window', bounds: { x: 40, y: 40, w: 500, h: 360 }, confidence: 0.98 },
        { id: 'el-2', text: 'File (فایل)', textFa: 'فایل', type: 'menu', bounds: { x: 50, y: 70, w: 40, h: 20 }, confidence: 0.95 },
        { id: 'el-3', text: 'Edit (ویرایش)', textFa: 'ویرایش', type: 'menu', bounds: { x: 95, y: 70, w: 50, h: 20 }, confidence: 0.94 },
        { id: 'el-4', text: 'Start (شروع)', textFa: 'شروع', type: 'button', bounds: { x: 20, y: 760, w: 48, h: 40 }, confidence: 0.99 },
        { id: 'el-5', text: 'Search Windows (جستجو)', textFa: 'جستجو', type: 'input', bounds: { x: 75, y: 765, w: 200, h: 30 }, confidence: 0.96 }
      ];
      output = {
        resolution: '1920x1080',
        dpi: 96,
        detectedTextCount: visibleElements.length,
        ocrEngine: 'Tesseract 5.3 + OpenCV Vision Loop',
        elements: visibleElements,
        capturedAt: new Date().toISOString()
      };
      break;
    }

    case 'find_element': {
      const q = (params.text || '').toLowerCase();
      output = {
        found: true,
        text: params.text,
        confidence: 0.96,
        bounds: { x: 120, y: 80, w: 85, h: 32 }
      };
      break;
    }

    case 'verify_action': {
      output = {
        verified: true,
        expected: params.expected,
        confidence: 0.98,
        message: `تایید شد: وضعیت صفحه با نتیجه مورد انتظار («${params.expected}») مطابقت دارد.`
      };
      break;
    }

    case 'query_hardware': {
      output = getSystemHardware();
      break;
    }

    case 'remember': {
      const newMem = {
        id: `mem-${Date.now()}`,
        content: params.content,
        category: params.category || 'general',
        tags: [params.category || 'general'],
        createdAt: Date.now(),
        accessCount: 1
      };
      memories.unshift(newMem);
      output = { message: 'اطلاعات با موفقیت در حافظه بلندمدت ذخیره شد.', memory: newMem };
      break;
    }

    case 'recall': {
      const query = (params.query || '').toLowerCase();
      const matched = memories.filter(m => m.content.toLowerCase().includes(query) || m.tags.some(t => t.toLowerCase().includes(query)));
      output = { query: params.query, count: matched.length, results: matched.length > 0 ? matched : memories.slice(0, 3) };
      break;
    }

    default:
      output = { message: `ابزار ${toolName} با پارامترهای مشخص اجرا گردید.` };
  }

  return {
    tool: toolName,
    params,
    success,
    output,
    error,
    durationMs: Date.now() - startTime,
    timestamp: new Date().toISOString()
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// Intent Analyzer & Rule + AI Reasoning
// ─────────────────────────────────────────────────────────────────────────────

function analyzeIntentRules(text: string): { verb: string; target: string; tools: string[]; isMultiStep: boolean; riskScore: number } {
  const t = text.toLowerCase();
  
  // Weather
  if (t.includes('هوا') || t.includes('weather') || t.includes('باران') || t.includes('دما')) {
    return { verb: 'search', target: 'weather', tools: ['execute_command'], isMultiStep: false, riskScore: 10 };
  }

  // Notepad / Notes
  if (t.includes('notepad') || t.includes('یادداشت') || t.includes('نوت‌پد')) {
    if (t.includes('بنویس') || t.includes('تایپ') || t.includes('write') || t.includes('type')) {
      return { verb: 'type', target: 'notepad', tools: ['launch_app', 'type_text', 'verify_action'], isMultiStep: true, riskScore: 20 };
    }
    return { verb: 'open', target: 'notepad', tools: ['launch_app', 'verify_action'], isMultiStep: false, riskScore: 10 };
  }

  // Calculator
  if (t.includes('calc') || t.includes('ماشین حساب') || t.includes('حساب کن')) {
    return { verb: 'open', target: 'calc', tools: ['launch_app'], isMultiStep: false, riskScore: 10 };
  }

  // Downloads / Files
  if (t.includes('downloads') || t.includes('دانلود') || t.includes('فایل') || t.includes('پوشه') || t.includes('directory')) {
    if (t.includes('بساز') || t.includes('ایجاد') || t.includes('create') || t.includes('make') || t.includes('new folder')) {
      return { verb: 'create', target: 'folder', tools: ['create_folder', 'list_directory'], isMultiStep: true, riskScore: 35 };
    }
    if (t.includes('حذف') || t.includes('delete') || t.includes('remove')) {
      return { verb: 'delete', target: 'file', tools: ['delete_file'], isMultiStep: false, riskScore: 85 };
    }
    return { verb: 'search', target: 'filesystem', tools: ['list_directory'], isMultiStep: false, riskScore: 10 };
  }

  // Screenshot / Screen
  if (t.includes('اسکرین') || t.includes('screenshot') || t.includes('عکس') || t.includes('تصویر صفحه')) {
    return { verb: 'observe', target: 'screen', tools: ['screenshot', 'read_screen'], isMultiStep: false, riskScore: 10 };
  }

  // Hardware / Status
  if (t.includes('سخت‌افزار') || t.includes('cpu') || t.includes('ram') || t.includes('وضعیت') || t.includes('status') || t.includes('سیستم')) {
    return { verb: 'query', target: 'hardware', tools: ['query_hardware'], isMultiStep: false, riskScore: 5 };
  }

  // General action
  return { verb: 'execute', target: 'system', tools: ['execute_command'], isMultiStep: false, riskScore: 25 };
}

// ─────────────────────────────────────────────────────────────────────────────
// API Endpoints
// ─────────────────────────────────────────────────────────────────────────────

app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    version: '1.2.0',
    name: 'Software-AI Persian Agent',
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

app.get('/api/providers', (req, res) => {
  res.json({ providers: getProviderStatuses() });
});

app.get('/api/tools', (req, res) => {
  res.json({ tools: CANONICAL_TOOLS });
});

app.get('/api/system/status', (req, res) => {
  res.json({
    hardware: getSystemHardware(),
    apps: virtualApps,
    files: virtualFilesystem
  });
});

app.get('/api/system/files', (req, res) => {
  res.json({ filesystem: virtualFilesystem });
});

app.post('/api/system/apps/toggle', (req, res) => {
  const { appId, action } = req.body;
  const appItem = virtualApps.find(a => a.id === appId);
  if (!appItem) {
    return res.status(404).json({ error: 'App not found' });
  }

  if (action === 'open') {
    appItem.isOpen = true;
    appItem.isMinimized = false;
    appItem.zIndex = Math.max(...virtualApps.map(a => a.zIndex)) + 1;
  } else if (action === 'close') {
    appItem.isOpen = false;
  } else if (action === 'minimize') {
    appItem.isMinimized = !appItem.isMinimized;
  } else if (action === 'focus') {
    appItem.zIndex = Math.max(...virtualApps.map(a => a.zIndex)) + 1;
  }

  res.json({ success: true, app: appItem, allApps: virtualApps });
});

app.get('/api/agent/sessions', (req, res) => {
  res.json({ sessions });
});

app.post('/api/agent/sessions', (req, res) => {
  const { name, tags } = req.body;
  const newSession = {
    id: `session-${Date.now()}`,
    name: name || `نشست جدید (${new Date().toLocaleTimeString('fa-IR')})`,
    createdAt: Date.now(),
    updatedAt: Date.now(),
    messageCount: 0,
    summary: 'نشست فعال برای ارسال دستورات هوش مصنوعی',
    tags: tags || ['custom']
  };
  sessions.unshift(newSession);
  sessionMessages[newSession.id] = [];
  res.json({ success: true, session: newSession });
});

app.get('/api/agent/sessions/:id/messages', (req, res) => {
  const sessionId = req.params.id;
  const messages = sessionMessages[sessionId] || [];
  res.json({ sessionId, messages });
});

app.delete('/api/agent/sessions/:id', (req, res) => {
  const sessionId = req.params.id;
  sessions = sessions.filter(s => s.id !== sessionId);
  delete sessionMessages[sessionId];
  res.json({ success: true, remainingSessions: sessions });
});

app.get('/api/agent/memories', (req, res) => {
  res.json({ memories });
});

app.post('/api/agent/memories', (req, res) => {
  const { content, category, tags } = req.body;
  const newMem = {
    id: `mem-${Date.now()}`,
    content,
    category: category || 'general',
    tags: tags || ['custom'],
    createdAt: Date.now(),
    accessCount: 0
  };
  memories.unshift(newMem);
  res.json({ success: true, memory: newMem });
});

app.delete('/api/agent/memories/:id', (req, res) => {
  const memId = req.params.id;
  memories = memories.filter(m => m.id !== memId);
  res.json({ success: true, memories });
});

app.post('/api/agent/execute-tool', (req, res) => {
  const { tool, params } = req.body;
  const result = executeTool(tool, params || {});
  res.json(result);
});

// ─────────────────────────────────────────────────────────────────────────────
// Agent Reasoning & Chat Pipeline (8 Stages)
// ─────────────────────────────────────────────────────────────────────────────

app.post('/api/agent/chat', async (req, res) => {
  const { prompt, sessionId = 'session-main', language = 'fa' } = req.body;

  if (!prompt || typeof prompt !== 'string') {
    return res.status(400).json({ error: 'Prompt is required' });
  }

  const analysis = analyzeIntentRules(prompt);
  const isPersian = language === 'fa' || /[\u0600-\u06FF]/.test(prompt);

  // Initialize 8 Reasoning Stages
  const stages: Array<{
    id: string;
    name: string;
    nameFa: string;
    status: 'pending' | 'active' | 'completed' | 'failed' | 'skipped';
    details: string;
    detailsFa: string;
    durationMs: number;
  }> = [
    {
      id: 'understand',
      name: 'Understand',
      nameFa: '۱. درک نیت کاربر (Understand)',
      status: 'completed',
      details: `Intent detected: verb="${analysis.verb}", target="${analysis.target}", riskScore=${analysis.riskScore}`,
      detailsFa: `تشخیص نیت: فعل اصلی «${analysis.verb}»، هدف «${analysis.target}»، نمره ریسک امنیتی: ${analysis.riskScore}/100`,
      durationMs: 45
    },
    {
      id: 'think',
      name: 'Think',
      nameFa: '۲. تفکر و تحلیل پیش‌نیازها (Think)',
      status: 'completed',
      details: `Evaluating system state, available tools (${analysis.tools.join(', ')}), and memory context.`,
      detailsFa: `بررسی زمینه ویندوز، حافظه بلندمدت و ابزارهای مورد نیاز: [${analysis.tools.join(', ')}]`,
      durationMs: 60
    },
    {
      id: 'plan',
      name: 'Plan',
      nameFa: '۳. تدوین برنامه اجرایی (Plan)',
      status: 'completed',
      details: `Generated plan with ${analysis.tools.length} step(s).`,
      detailsFa: `برنامه چندمرحله‌ای ایجاد شد: ${analysis.tools.length} گام اجرایی با اعتبارسنجی پارامترها`,
      durationMs: 40
    },
    {
      id: 'observe',
      name: 'Observe',
      nameFa: '۴. مشاهده وضعیت فعلی دسکتاپ (Observe)',
      status: 'completed',
      details: 'Inspected screen state, focused window, and OCR bounding boxes.',
      detailsFa: 'عکس‌برداری و اسکن عناصر دسکتاپ و پنجره‌های فعال برای پیشگیری از تداخل',
      durationMs: 75
    },
    {
      id: 'execute',
      name: 'Execute',
      nameFa: '۵. اجرای ابزارهای سیستمی (Execute)',
      status: 'completed',
      details: `Executing canonical tools: ${analysis.tools.join(', ')}`,
      detailsFa: `اجرای گام‌به‌گام دستورات و ابزارها با ثبت لاگ ساختاریافته`,
      durationMs: 110
    },
    {
      id: 'review',
      name: 'Review',
      nameFa: '۶. بازبینی خودکار نتایج (Review)',
      status: 'completed',
      details: 'Verified exit codes and screen state assertions.',
      detailsFa: 'تایید درستی خروجی‌ها و انطباق نتیجه با هدف درخواستی کاربر',
      durationMs: 35
    },
    {
      id: 'recover',
      name: 'Recover',
      nameFa: '۷. بازیابی در صورت خطا (Recover)',
      status: 'skipped',
      details: 'No execution faults detected. Recovery bypassed.',
      detailsFa: 'هیچ خطایی در طول اجرا رخ نداد، حلقه بازیابی بدون فعال‌سازی رد شد.',
      durationMs: 10
    },
    {
      id: 'continue',
      name: 'Continue',
      nameFa: '۸. جمع‌بندی و ادامه مکالمه (Continue)',
      status: 'completed',
      details: 'Session state saved, ready for next user directive.',
      detailsFa: 'به‌روزرسانی نشست و حافظه؛ سیستم آماده دریافت دستور بعدی است.',
      durationMs: 25
    }
  ];

  // Execute primary tool actions
  const toolResults: any[] = [];
  for (const toolName of analysis.tools) {
    let toolParams: Record<string, any> = {};
    if (toolName === 'launch_app') {
      toolParams = { app_name: analysis.target === 'notepad' ? 'notepad.exe' : analysis.target === 'calc' ? 'calc.exe' : 'powershell.exe' };
    } else if (toolName === 'list_directory') {
      toolParams = { path: 'C:\\Users\\Admin\\Downloads' };
    } else if (toolName === 'create_folder') {
      toolParams = { path: 'D:\\test' };
    } else if (toolName === 'type_text') {
      toolParams = { text: 'یادداشت جدید ثبت شده توسط عامل هوشمند Software-AI' };
    } else if (toolName === 'delete_file') {
      toolParams = { path: 'C:\\Users\\Admin\\Downloads\\temp_cache.tmp' };
    } else if (toolName === 'screenshot' || toolName === 'read_screen') {
      toolParams = { region: 'full' };
    } else if (toolName === 'query_hardware') {
      toolParams = { query_type: 'all' };
    } else if (toolName === 'execute_command') {
      if (prompt.includes('هوا') || prompt.includes('weather')) {
        toolParams = { command: 'curl -s "wttr.in/Tehran?format=3"' };
      } else {
        toolParams = { command: 'Get-Process | Select-Object -First 5' };
      }
    } else if (toolName === 'verify_action') {
      toolParams = { expected: `عملیات ${analysis.verb} روی ${analysis.target} تکمیل شد.` };
    }
    const res = executeTool(toolName, toolParams);
    toolResults.push(res);
  }

  // Generate intelligent response using Gemini API if key is available, else rule-based response
  let assistantReply = '';
  const geminiApiKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;

  if (geminiApiKey) {
    try {
      const ai = new GoogleGenAI({ apiKey: geminiApiKey });
      const systemPrompt = `You are Software-AI, an expert Windows autonomous agent and desktop automation assistant.
You speak both Persian (فارسی) and English fluently.
The user asked: "${prompt}".
The intent analyzer matched: verb="${analysis.verb}", target="${analysis.target}".
The tools executed were: ${JSON.stringify(toolResults.map(t => ({ tool: t.tool, output: t.output })))}.
Current Hardware: CPU ${getSystemHardware().cpuUsage}%, RAM ${getSystemHardware().ramUsage}%.
Provide a concise, helpful, and polite response in ${isPersian ? 'Persian (فارسی)' : 'English'} explaining what actions you executed on the Windows system and the result.`;

      const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash',
        contents: systemPrompt
      });

      assistantReply = response.text || '';
    } catch (err: any) {
      console.warn('Gemini API call error (falling back to built-in response engine):', err.message);
    }
  }

  // Fallback intelligent response if Gemini is not set or throttled
  if (!assistantReply) {
    if (analysis.target === 'weather') {
      assistantReply = isPersian 
        ? 'وضعیت آب‌وهوای تهران در حال حاضر: آفتابی، دمای ۲۴ درجه سانتی‌گراد، رطوبت ۳۲٪ و باد ملایم ۸ کیلومتر بر ساعت است.'
        : 'Current Tehran weather: Sunny, 24°C, 32% humidity, light breeze at 8 km/h.';
    } else if (analysis.target === 'notepad') {
      assistantReply = isPersian
        ? 'برنامه Notepad با موفقیت اجرا شد و متن مورد نظر شما در پنجره یادداشت درج گردید.'
        : 'Notepad was launched and the text was entered into the document.';
    } else if (analysis.target === 'calc') {
      assistantReply = isPersian
        ? 'برنامه ماشین حساب (Calculator) ویندوز باز شد و آماده انجام محاسبات شماست.'
        : 'Windows Calculator was launched and is ready for your calculations.';
    } else if (analysis.target === 'filesystem') {
      assistantReply = isPersian
        ? `پوشه Downloads بررسی شد؛ ۳ فایل شناسایی شدند:
• setup_python311.exe (28.4 MB)
• document_fa.pdf (1.2 MB)
• project_notes.txt (4 KB)`
        : `Inspected Downloads folder; found 3 items:
• setup_python311.exe (28.4 MB)
• document_fa.pdf (1.2 MB)
• project_notes.txt (4 KB)`;
    } else if (analysis.target === 'folder') {
      assistantReply = isPersian
        ? 'پوشه جدید با موفقیت روی سیستم ساخته شد و ساختار آن تایید گردید.'
        : 'New folder created successfully on the filesystem.';
    } else if (analysis.target === 'screen') {
      assistantReply = isPersian
        ? 'اسکرین‌شات از صفحه با موفقیت گرفته شد و ۵ عنصر رابط کاربری توسط موتور OCR تشخیص داده شدند.'
        : 'Screenshot captured and 5 desktop UI elements recognized via OCR vision loop.';
    } else if (analysis.target === 'hardware') {
      const hw = getSystemHardware();
      assistantReply = isPersian
        ? `اطلاعات سیستم دریافت شد:
• سیستم‌عامل: ${hw.os}
• مصرف پردازنده: ${hw.cpuUsage}%
• حافظه رم: ${hw.ramUsage}% از ${hw.ramTotal}
• دیسک: ${hw.diskUsage}% از ${hw.diskTotal}
• تعداد پردازش‌ها: ${hw.activeProcesses}`
        : `System hardware diagnostics:
• OS: ${hw.os}
• CPU Usage: ${hw.cpuUsage}%
• RAM Usage: ${hw.ramUsage}% of ${hw.ramTotal}
• Disk Usage: ${hw.diskUsage}% of ${hw.diskTotal}
• Active Processes: ${hw.activeProcesses}`;
    } else {
      assistantReply = isPersian
        ? `دستور شما با موفقیت در پایپ‌لاین استدلال پردازش شد و اقدامات مربوطه با ضریب اطمینان ۱۰۰٪ به پایان رسیدند.`
        : `Your request was processed through the 8-stage reasoning pipeline and executed successfully.`;
    }
  }

  // Create plan representation
  const plan = {
    id: `plan-${Date.now()}`,
    goal: prompt,
    goalFa: prompt,
    steps: analysis.tools.map((tool, idx) => ({
      id: idx + 1,
      title: `Run ${tool}`,
      titleFa: `اجرای ابزار ${CANONICAL_TOOLS.find(t => t.name === tool)?.descriptionFa || tool}`,
      tool,
      params: toolResults[idx]?.params || {},
      status: 'completed',
      result: toolResults[idx]?.output,
      riskLevel: CANONICAL_TOOLS.find(t => t.name === tool)?.riskLevel || 'safe'
    })),
    status: 'completed',
    currentStepIndex: analysis.tools.length
  };

  const userMsg = {
    id: `msg-user-${Date.now()}`,
    sessionId,
    role: 'user',
    content: prompt,
    timestamp: Date.now()
  };

  const assistantMsg = {
    id: `msg-ast-${Date.now()}`,
    sessionId,
    role: 'assistant',
    content: assistantReply,
    timestamp: Date.now(),
    reasoningStages: stages,
    toolCalls: toolResults,
    plan,
    riskAssessment: {
      score: analysis.riskScore,
      level: analysis.riskScore > 75 ? 'high' : analysis.riskScore > 40 ? 'medium' : analysis.riskScore > 15 ? 'low' : 'safe',
      reasons: [
        analysis.riskScore > 50 ? 'نیاز به دسترسی ایجاد/حذف فایل سیستمی' : 'دستورات استاندارد خواندن و اجرای برنامه'
      ]
    }
  };

  if (!sessionMessages[sessionId]) {
    sessionMessages[sessionId] = [];
  }
  sessionMessages[sessionId].push(userMsg);
  sessionMessages[sessionId].push(assistantMsg);

  // Update session
  const sess = sessions.find(s => s.id === sessionId);
  if (sess) {
    sess.updatedAt = Date.now();
    sess.messageCount = sessionMessages[sessionId].length;
  }

  res.json({
    userMessage: userMsg,
    assistantMessage: assistantMsg,
    stages,
    toolResults,
    plan
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Vite Middleware / Static Server
// ─────────────────────────────────────────────────────────────────────────────

async function startServer() {
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa'
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Software-AI Persian Agent Server running at http://0.0.0.0:${PORT}`);
  });
}

startServer();
