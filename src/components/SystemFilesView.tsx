import React, { useState } from 'react';
import { 
  Folder, 
  FileText, 
  FolderTree, 
  File, 
  HardDrive, 
  Trash2, 
  FolderPlus, 
  FilePlus, 
  Search, 
  Clock, 
  FileCode,
  CheckCircle2
} from 'lucide-react';
import { VirtualFile, Language } from '../types';

interface SystemFilesViewProps {
  filesystem: any;
  language: Language;
  onReadFile: (path: string) => Promise<string>;
  onCreateFolder: (path: string) => Promise<void>;
  onDeleteFile: (path: string) => Promise<void>;
}

export const SystemFilesView: React.FC<SystemFilesViewProps> = ({
  filesystem,
  language,
  onReadFile,
  onCreateFolder,
  onDeleteFile,
}) => {
  const isFa = language === 'fa';
  const [currentPath, setCurrentPath] = useState('C:\\Users\\Admin\\Downloads');
  const [selectedFile, setSelectedFile] = useState<any>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [isLoadingFile, setIsLoadingFile] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [isCreatingFolder, setIsCreatingFolder] = useState(false);

  // Files for current path
  const sampleDownloads = [
    { name: 'setup_python311.exe', path: 'C:\\Users\\Admin\\Downloads\\setup_python311.exe', type: 'file', size: '28.4 MB', modified: '2026-06-24 11:15:00' },
    { name: 'document_fa.pdf', path: 'C:\\Users\\Admin\\Downloads\\document_fa.pdf', type: 'file', size: '1.2 MB', modified: '2026-06-24 13:20:00' },
    { name: 'project_notes.txt', path: 'C:\\Users\\Admin\\Downloads\\project_notes.txt', type: 'file', size: '4 KB', modified: '2026-06-24 14:05:00', content: 'پروژه اتوماسیون هوش مصنوعی ویندوز به زبان فارسی و انگلیسی.\nتمامی قابلیت‌های پایپ‌لاین استدلال پیاده‌سازی شدند.' }
  ];

  const sampleDocuments = [
    { name: 'Report_2026.docx', path: 'C:\\Users\\Admin\\Documents\\Report_2026.docx', type: 'file', size: '420 KB', modified: '2026-06-22 09:10:00' },
    { name: 'config.json', path: 'C:\\Users\\Admin\\Documents\\config.json', type: 'file', size: '2 KB', modified: '2026-06-23 16:40:00', content: '{\n  "theme": "dark",\n  "safety_mode": "power",\n  "language": "fa"\n}' }
  ];

  const sampleDesktop = [
    { name: 'Software-AI.lnk', path: 'C:\\Users\\Admin\\Desktop\\Software-AI.lnk', type: 'file', size: '1 KB', modified: '2026-06-20 10:00:00' },
    { name: 'Notepad.lnk', path: 'C:\\Users\\Admin\\Desktop\\Notepad.lnk', type: 'file', size: '1 KB', modified: '2026-06-20 10:00:00' }
  ];

  const getCurrentFiles = () => {
    if (currentPath.includes('Documents')) return sampleDocuments;
    if (currentPath.includes('Desktop')) return sampleDesktop;
    return sampleDownloads;
  };

  const handleFileClick = async (file: any) => {
    setSelectedFile(file);
    if (file.content) {
      setFileContent(file.content);
    } else {
      setIsLoadingFile(true);
      try {
        const text = await onReadFile(file.path);
        setFileContent(text);
      } catch {
        setFileContent('Binary file or contents unavailable for preview.');
      } finally {
        setIsLoadingFile(false);
      }
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 h-[750px] bg-slate-950/60 p-4 rounded-2xl border border-slate-800">
      {/* Directory Navigation Tree */}
      <div className="lg:col-span-4 flex flex-col bg-slate-900/90 rounded-xl border border-slate-800 p-3.5 overflow-hidden">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <FolderTree className="w-4 h-4 text-cyan-400" />
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              {isFa ? 'مسیرهای سیستم (Windows Drives)' : 'Windows Drives'}
            </h3>
          </div>
        </div>

        <div className="space-y-1 text-xs">
          <div className="p-2 rounded-lg bg-slate-800/40 text-slate-300 font-mono flex items-center gap-2">
            <HardDrive className="w-4 h-4 text-cyan-400" />
            <span>Local Disk (C:)</span>
          </div>

          <div className="pl-4 rtl:pr-4 rtl:pl-0 space-y-1 mt-1">
            <button
              onClick={() => { setCurrentPath('C:\\Users\\Admin\\Downloads'); setSelectedFile(null); }}
              className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-left rtl:text-right ${
                currentPath.includes('Downloads')
                  ? 'bg-cyan-600/20 text-cyan-300 border border-cyan-500/30'
                  : 'hover:bg-slate-800 text-slate-400'
              }`}
            >
              <Folder className="w-3.5 h-3.5 text-indigo-400" />
              <span>Downloads (دانلودها)</span>
            </button>

            <button
              onClick={() => { setCurrentPath('C:\\Users\\Admin\\Documents'); setSelectedFile(null); }}
              className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-left rtl:text-right ${
                currentPath.includes('Documents')
                  ? 'bg-cyan-600/20 text-cyan-300 border border-cyan-500/30'
                  : 'hover:bg-slate-800 text-slate-400'
              }`}
            >
              <Folder className="w-3.5 h-3.5 text-amber-400" />
              <span>Documents (اسناد)</span>
            </button>

            <button
              onClick={() => { setCurrentPath('C:\\Users\\Admin\\Desktop'); setSelectedFile(null); }}
              className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-left rtl:text-right ${
                currentPath.includes('Desktop')
                  ? 'bg-cyan-600/20 text-cyan-300 border border-cyan-500/30'
                  : 'hover:bg-slate-800 text-slate-400'
              }`}
            >
              <Folder className="w-3.5 h-3.5 text-blue-400" />
              <span>Desktop (دسکتاپ)</span>
            </button>
          </div>

          <div className="pt-3 border-t border-slate-800 mt-3">
            <div className="p-2 rounded-lg bg-slate-800/40 text-slate-400 font-mono flex items-center gap-2">
              <HardDrive className="w-4 h-4 text-emerald-400" />
              <span>Data Disk (D:)</span>
            </div>
            <div className="pl-4 rtl:pr-4 rtl:pl-0 space-y-1 mt-1">
              <div className="px-3 py-1.5 rounded-lg text-slate-500 flex items-center gap-2">
                <Folder className="w-3.5 h-3.5 text-slate-500" />
                <span>Projects (پروژه‌ها)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Create Folder Box */}
        <div className="mt-auto pt-3 border-t border-slate-800">
          <div className="flex gap-1.5">
            <input
              type="text"
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
              placeholder={isFa ? 'نام پوشه جدید...' : 'New folder name...'}
              className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            />
            <button
              onClick={async () => {
                if (!newFolderName.trim()) return;
                await onCreateFolder(`${currentPath}\\${newFolderName}`);
                setNewFolderName('');
              }}
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400"
              title={isFa ? 'ایجاد پوشه' : 'Create folder'}
            >
              <FolderPlus className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Files Table & File Inspector */}
      <div className="lg:col-span-8 flex flex-col bg-slate-900/90 rounded-xl border border-slate-800 p-4 overflow-hidden">
        {/* Address Bar */}
        <div className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-cyan-300 flex items-center gap-2 mb-3">
          <Folder className="w-3.5 h-3.5 text-indigo-400" />
          <span>{currentPath}</span>
        </div>

        {/* Files Grid / List */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-4">
          {getCurrentFiles().map((file) => (
            <div
              key={file.name}
              onClick={() => handleFileClick(file)}
              className={`p-3 rounded-lg border cursor-pointer flex items-center justify-between transition-all ${
                selectedFile?.name === file.name
                  ? 'bg-cyan-950/40 border-cyan-500/60'
                  : 'bg-slate-950/50 border-slate-800 hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <FileText className="w-4 h-4 text-cyan-400 shrink-0" />
                <div>
                  <div className="text-xs font-medium text-slate-200">{file.name}</div>
                  <div className="text-[10px] text-slate-500 font-mono">{file.size}</div>
                </div>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteFile(file.path);
                }}
                className="p-1 text-slate-500 hover:text-rose-400 rounded transition-colors"
                title={isFa ? 'حذف فایل' : 'Delete file'}
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>

        {/* File Content Previewer */}
        <div className="flex-1 flex flex-col bg-slate-950 border border-slate-800 rounded-xl p-3.5 overflow-hidden">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800 mb-2">
            <div className="flex items-center gap-2">
              <FileCode className="w-4 h-4 text-cyan-400" />
              <span className="text-xs font-semibold text-slate-200">
                {selectedFile ? selectedFile.name : (isFa ? 'پیش‌نمایش محتوای فایل' : 'File Preview')}
              </span>
            </div>
            {selectedFile && (
              <span className="text-[10px] text-slate-500 font-mono">{selectedFile.modified}</span>
            )}
          </div>

          <pre className="flex-1 overflow-auto text-xs text-slate-300 font-mono leading-relaxed whitespace-pre-wrap">
            {selectedFile 
              ? (fileContent || (isFa ? 'فایل خالی است.' : 'File is empty.'))
              : (isFa ? 'یک فایل را برای مشاهده محتوا انتخاب نمایید.' : 'Select a file to inspect its content.')}
          </pre>
        </div>
      </div>
    </div>
  );
};
