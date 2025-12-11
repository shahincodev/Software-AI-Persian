# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""ابزار تحلیل و نمایش لاگ‌ها.

این اسکریپت ابزاری برای:
- نمایش لاگ‌های اخیر
- جستجو در لاگ‌ها
- فیلتر کردن بر اساس نوع، زمان، و ...
- تولید گزارش‌های خلاصه
- صادرات لاگ‌ها
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import Counter


class LogAnalyzer:
    """تحلیل‌گر لاگ‌ها."""
    
    def __init__(self, log_dir: Path = Path("data/logs")):
        self.log_dir = log_dir
        self.logs = []
    
    def load_logs(self, log_file: str = "full_trace.jsonl", limit: Optional[int] = None):
        """بارگذاری لاگ‌ها از فایل."""
        file_path = self.log_dir / log_file
        
        if not file_path.exists():
            print(f"❌ Log file not found: {file_path}")
            return
        
        self.logs = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if limit and i >= limit:
                    break
                try:
                    self.logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        print(f"✅ Loaded {len(self.logs)} log entries from {log_file}")
    
    def filter_logs(
        self,
        category: Optional[str] = None,
        level: Optional[str] = None,
        search: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """فیلتر کردن لاگ‌ها."""
        filtered = self.logs
        
        if category:
            filtered = [log for log in filtered if log.get('category') == category]
        
        if level:
            filtered = [log for log in filtered if log.get('level') == level]
        
        if search:
            search_lower = search.lower()
            filtered = [
                log for log in filtered
                if search_lower in json.dumps(log, ensure_ascii=False).lower()
            ]
        
        if start_time:
            filtered = [
                log for log in filtered
                if datetime.fromisoformat(log.get('timestamp', '')) >= start_time
            ]
        
        if end_time:
            filtered = [
                log for log in filtered
                if datetime.fromisoformat(log.get('timestamp', '')) <= end_time
            ]
        
        return filtered
    
    def show_recent(self, count: int = 20, category: Optional[str] = None):
        """نمایش لاگ‌های اخیر."""
        logs = self.filter_logs(category=category)
        logs = logs[-count:]  # آخرین N تا
        
        print(f"\n📋 Last {len(logs)} logs" + (f" (category: {category})" if category else ""))
        print("=" * 100)
        
        for log in logs:
            timestamp = log.get('timestamp', 'Unknown')
            category = log.get('category', 'Unknown')
            level = log.get('level', 'INFO')
            
            # رنگ بر اساس level
            if level == 'ERROR' or level == 'CRITICAL':
                color = "🔴"
            elif level == 'WARNING':
                color = "🟡"
            else:
                color = "🟢"
            
            print(f"\n{color} [{timestamp}] {category} - {level}")
            
            # نمایش محتوا بر اساس نوع
            if 'message' in log:
                print(f"   Message: {log['message']}")
            
            if 'action' in log:
                print(f"   Action: {log['action']} (success: {log.get('success', 'N/A')})")
            
            if 'exception_message' in log:
                print(f"   Exception: {log['exception_type']}: {log['exception_message']}")
            
            if 'prompt' in log:
                print(f"   Prompt: {log['prompt'][:100]}...")
            
            if 'response' in log and log['response']:
                print(f"   Response: {log['response'][:100]}...")
    
    def show_errors(self, limit: int = 50):
        """نمایش همه خطاها."""
        errors = self.filter_logs(category='error')
        errors = errors[-limit:]
        
        print(f"\n🔴 Last {len(errors)} errors:")
        print("=" * 100)
        
        for i, error in enumerate(errors, 1):
            timestamp = error.get('timestamp', 'Unknown')
            exc_type = error.get('exception_type', error.get('error_type', 'Unknown'))
            exc_msg = error.get('exception_message', error.get('message', 'Unknown'))
            
            print(f"\n{i}. [{timestamp}] {exc_type}")
            print(f"   {exc_msg}")
            
            if 'context' in error:
                print(f"   Context: {error['context']}")
    
    def show_statistics(self):
        """نمایش آمار کلی."""
        print("\n📊 LOG STATISTICS")
        print("=" * 100)
        
        # تعداد کل
        print(f"Total logs: {len(self.logs)}")
        
        # دسته‌بندی
        categories = Counter(log.get('category', 'unknown') for log in self.logs)
        print("\nBy Category:")
        for category, count in categories.most_common():
            print(f"  {category}: {count}")
        
        # سطح
        levels = Counter(log.get('level', 'unknown') for log in self.logs)
        print("\nBy Level:")
        for level, count in levels.most_common():
            print(f"  {level}: {count}")
        
        # خطاها
        errors = self.filter_logs(category='error')
        print(f"\nTotal errors: {len(errors)}")
        
        if errors:
            error_types = Counter(
                log.get('exception_type', log.get('error_type', 'Unknown'))
                for log in errors
            )
            print("\nTop error types:")
            for error_type, count in error_types.most_common(10):
                print(f"  {error_type}: {count}")
        
        # اقدامات کاربر
        user_actions = self.filter_logs(category='user_action')
        print(f"\nTotal user actions: {len(user_actions)}")
        
        successful_actions = sum(1 for log in user_actions if log.get('success'))
        print(f"  Successful: {successful_actions}")
        print(f"  Failed: {len(user_actions) - successful_actions}")
        
        # درخواست‌های AI
        ai_requests = self.filter_logs(category='ai_request')
        ai_responses = self.filter_logs(category='ai_response')
        print(f"\nAI interactions:")
        print(f"  Requests: {len(ai_requests)}")
        print(f"  Responses: {len(ai_responses)}")
        
        successful_ai = sum(1 for log in ai_responses if log.get('success'))
        print(f"  Successful responses: {successful_ai}")
        print(f"  Failed responses: {len(ai_responses) - successful_ai}")
    
    def search(self, query: str, limit: int = 50):
        """جستجو در لاگ‌ها."""
        results = self.filter_logs(search=query)
        results = results[-limit:]
        
        print(f"\n🔍 Search results for '{query}': {len(results)} matches")
        print("=" * 100)
        
        for i, log in enumerate(results, 1):
            print(f"\n{i}. [{log.get('timestamp', 'Unknown')}] {log.get('category', 'Unknown')}")
            print(f"   {json.dumps(log, ensure_ascii=False, indent=2)[:300]}...")
    
    def export_errors(self, output_file: str = "errors_export.json"):
        """صادرات همه خطاها به فایل JSON."""
        errors = self.filter_logs(category='error')
        
        output_path = self.log_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(errors, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ Exported {len(errors)} errors to {output_path}")
    
    def list_sessions(self):
        """لیست تمام session ها."""
        session_files = sorted(self.log_dir.glob("session_*.jsonl"))
        
        print(f"\n📋 Found {len(session_files)} sessions:")
        print("=" * 100)
        
        for session_file in session_files:
            session_id = session_file.stem.replace("session_", "")
            
            # شمارش لاگ‌ها
            log_count = sum(1 for _ in open(session_file, encoding='utf-8'))
            
            # زمان ایجاد
            created = datetime.fromtimestamp(session_file.stat().st_ctime)
            
            print(f"\n📁 {session_id}")
            print(f"   Logs: {log_count}")
            print(f"   Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   File: {session_file.name}")


def main():
    """تابع اصلی."""
    parser = argparse.ArgumentParser(description="Software-AI Log Analyzer")
    parser.add_argument("--log-dir", default="data/logs", help="Log directory path")
    parser.add_argument("--log-file", default="full_trace.jsonl", help="Log file to analyze")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Command: recent
    recent_parser = subparsers.add_parser("recent", help="Show recent logs")
    recent_parser.add_argument("-n", "--count", type=int, default=20, help="Number of logs to show")
    recent_parser.add_argument("-c", "--category", help="Filter by category")
    
    # Command: errors
    errors_parser = subparsers.add_parser("errors", help="Show errors")
    errors_parser.add_argument("-n", "--limit", type=int, default=50, help="Number of errors to show")
    
    # Command: stats
    subparsers.add_parser("stats", help="Show statistics")
    
    # Command: search
    search_parser = subparsers.add_parser("search", help="Search in logs")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("-n", "--limit", type=int, default=50, help="Number of results")
    
    # Command: export
    export_parser = subparsers.add_parser("export", help="Export errors")
    export_parser.add_argument("-o", "--output", default="errors_export.json", help="Output file")
    
    # Command: sessions
    subparsers.add_parser("sessions", help="List all sessions")
    
    args = parser.parse_args()
    
    analyzer = LogAnalyzer(Path(args.log_dir))
    
    if args.command in ["recent", "errors", "stats", "search", "export"]:
        analyzer.load_logs(args.log_file)
    
    if args.command == "recent":
        analyzer.show_recent(args.count, args.category)
    
    elif args.command == "errors":
        analyzer.show_errors(args.limit)
    
    elif args.command == "stats":
        analyzer.show_statistics()
    
    elif args.command == "search":
        analyzer.search(args.query, args.limit)
    
    elif args.command == "export":
        analyzer.export_errors(args.output)
    
    elif args.command == "sessions":
        analyzer.list_sessions()
    
    else:
        # پیش‌فرض: نمایش آمار
        analyzer.load_logs(args.log_file)
        analyzer.show_statistics()
        print("\n" + "=" * 100)
        analyzer.show_recent(10)


if __name__ == "__main__":
    main()
