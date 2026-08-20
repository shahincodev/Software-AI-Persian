export type Language = 'fa' | 'en';

export interface ToolParam {
  name: string;
  type: string;
  required: boolean;
  default?: any;
  description: string;
  descriptionFa?: string;
}

export interface ToolDefinition {
  name: string;
  description: string;
  descriptionFa: string;
  category: 'system' | 'desktop_ui' | 'vision' | 'memory' | 'filesystem';
  riskLevel: 'safe' | 'low' | 'medium' | 'high';
  params: ToolParam[];
}

export interface ToolExecutionResult {
  tool: string;
  params: Record<string, any>;
  success: boolean;
  output?: any;
  error?: string;
  durationMs: number;
  timestamp: string;
  stage?: string;
}

export interface IntentAnalysis {
  rawPrompt: string;
  language: 'fa' | 'en';
  verb: string;
  target: string;
  parameters: Record<string, any>;
  confidence: number;
  isMultiStep: boolean;
  requiredTools: string[];
  riskScore: number;
  missingFields: string[];
}

export type ReasoningStageId = 
  | 'understand'  // 1. درک
  | 'think'       // 2. تفکر
  | 'plan'        // 3. برنامه‌ریزی
  | 'observe'     // 4. مشاهده
  | 'execute'     // 5. اجرا
  | 'review'      // 6. بازبینی
  | 'recover'     // 7. بازیابی
  | 'continue';   // 8. ادامه

export interface ReasoningStageLog {
  id: ReasoningStageId;
  name: string;
  nameFa: string;
  status: 'pending' | 'active' | 'completed' | 'failed' | 'skipped';
  details?: string;
  detailsFa?: string;
  data?: any;
  durationMs?: number;
}

export interface PlanStep {
  id: number;
  title: string;
  titleFa: string;
  tool: string;
  params: Record<string, any>;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  result?: any;
  error?: string;
  riskLevel: 'safe' | 'low' | 'medium' | 'high';
}

export interface MultiStepPlan {
  id: string;
  goal: string;
  goalFa: string;
  steps: PlanStep[];
  status: 'draft' | 'executing' | 'completed' | 'failed' | 'cancelled';
  currentStepIndex: number;
}

export interface SessionMessage {
  id: string;
  sessionId: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  reasoningStages?: ReasoningStageLog[];
  toolCalls?: ToolExecutionResult[];
  plan?: MultiStepPlan;
  riskAssessment?: {
    score: number;
    level: 'safe' | 'low' | 'medium' | 'high';
    reasons: string[];
  };
}

export interface Session {
  id: string;
  name: string;
  createdAt: number;
  updatedAt: number;
  messageCount: number;
  summary?: string;
  tags: string[];
}

export interface MemoryItem {
  id: string;
  content: string;
  category: 'preference' | 'fact' | 'instruction' | 'conversation' | 'general';
  tags: string[];
  createdAt: number;
  accessCount: number;
}

export interface VirtualFile {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: string;
  modified: string;
  content?: string;
  children?: VirtualFile[];
}

export interface VirtualApp {
  id: string;
  name: string;
  processName: string;
  title: string;
  icon: string;
  isOpen: boolean;
  isMinimized: boolean;
  zIndex: number;
  content?: any;
  position?: { x: number; y: number; w: number; h: number };
}

export interface DesktopElement {
  id: string;
  text: string;
  textFa?: string;
  type: 'button' | 'input' | 'window' | 'icon' | 'menu' | 'text';
  bounds: { x: number; y: number; w: number; h: number };
  confidence: number;
}

export interface SystemHardware {
  os: string;
  hostname: string;
  cpuUsage: number;
  ramUsage: number;
  ramTotal: string;
  diskUsage: number;
  diskTotal: string;
  activeProcesses: number;
  tesseractStatus: 'ready' | 'simulated' | 'not_found';
  uptimeSeconds: number;
}

export interface ProviderStatus {
  name: string;
  displayName: string;
  envVar: string;
  isConfigured: boolean;
  isAvailable: boolean;
  models: string[];
  latencyMs?: number;
}

export interface ConsentRequest {
  id: string;
  tool: string;
  params: Record<string, any>;
  riskScore: number;
  riskLevel: 'medium' | 'high';
  reason: string;
  reasonFa: string;
  status: 'pending' | 'approved' | 'rejected';
}
