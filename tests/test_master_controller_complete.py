"""
🧪 تست جامع Master AI Controller
====================================

این فایل شامل تست‌های کامل برای تمام قابلیت‌های Master Controller است.

استفاده:
    python tests/test_master_controller_complete.py
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

# اضافه کردن مسیر پروژه به sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.master_controller import MasterAIController, ToolType
from core.intelligent_agent import IntelligentSystemAgent


class TestColors:
    """رنگ‌ها برای خروجی زیباتر"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class MasterControllerTester:
    """کلاس اصلی تست"""
    
    def __init__(self):
        self.master = None
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    async def setup(self):
        """مقداردهی اولیه Master Controller"""
        print(f"\n{TestColors.HEADER}{'='*60}{TestColors.ENDC}")
        print(f"{TestColors.HEADER}🧪 Master AI Controller - Complete Test Suite{TestColors.ENDC}")
        print(f"{TestColors.HEADER}{'='*60}{TestColors.ENDC}\n")
        
        print(f"{TestColors.OKCYAN}⚙️  در حال مقداردهی اولیه...{TestColors.ENDC}")
        
        try:
            system_agent = IntelligentSystemAgent()
            self.master = MasterAIController(system_agent=system_agent)
            print(f"{TestColors.OKGREEN}✅ Master Controller آماده است!{TestColors.ENDC}\n")
            return True
        except Exception as e:
            print(f"{TestColors.FAIL}❌ خطا در مقداردهی: {e}{TestColors.ENDC}\n")
            return False
    
    def print_test_header(self, category: str, test_num: int, total: int):
        """چاپ هدر هر دسته تست"""
        print(f"\n{TestColors.BOLD}{TestColors.OKBLUE}{'─'*60}{TestColors.ENDC}")
        print(f"{TestColors.BOLD}{TestColors.OKBLUE}📋 {category} ({test_num}/{total}){TestColors.ENDC}")
        print(f"{TestColors.BOLD}{TestColors.OKBLUE}{'─'*60}{TestColors.ENDC}\n")
    
    async def run_single_test(
        self, 
        test_name: str, 
        request: str, 
        expected_tool: ToolType,
        description: str = ""
    ) -> bool:
        """اجرای یک تست"""
        self.total_tests += 1
        
        print(f"{TestColors.OKCYAN}🔍 تست: {test_name}{TestColors.ENDC}")
        if description:
            print(f"   📝 {description}")
        print(f"   👤 درخواست: \"{request}\"")
        
        try:
            # اجرای درخواست
            start_time = datetime.now()
            result = await self.master.process_request(request)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # بررسی نتیجه
            is_correct = result.tool_used == expected_tool
            
            if is_correct:
                self.passed_tests += 1
                print(f"   {TestColors.OKGREEN}✅ موفق!{TestColors.ENDC}")
            else:
                self.failed_tests += 1
                print(f"   {TestColors.FAIL}❌ ناموفق!{TestColors.ENDC}")
                print(f"   {TestColors.WARNING}   انتظار: {expected_tool.value}{TestColors.ENDC}")
                print(f"   {TestColors.WARNING}   دریافت: {result.tool_used.value}{TestColors.ENDC}")
            
            # نمایش جزئیات
            print(f"   🔧 ابزار استفاده شده: {result.tool_used.value}")
            print(f"   ⏱️  زمان اجرا: {execution_time:.2f} ثانیه")
            print(f"   💬 پاسخ: {result.human_response[:100]}...")
            
            # ذخیره نتیجه
            self.results.append({
                'test_name': test_name,
                'request': request,
                'expected': expected_tool.value,
                'actual': result.tool_used.value,
                'passed': is_correct,
                'time': execution_time,
                'response': result.human_response
            })
            
            print()
            return is_correct
            
        except Exception as e:
            self.failed_tests += 1
            print(f"   {TestColors.FAIL}❌ خطا: {e}{TestColors.ENDC}\n")
            return False
    
    async def test_chat_category(self):
        """تست دسته CHAT"""
        self.print_test_header("دسته CHAT - گفتگوی عمومی", 1, 6)
        
        tests = [
            ("سلام ساده", "سلام، حالت چطوره؟", ToolType.CHAT, "تست سلام و احوالپرسی"),
            ("سوال عمومی", "هوش مصنوعی چیست؟", ToolType.CHAT, "سوال در مورد AI"),
            ("سوال برنامه‌نویسی", "تفاوت Python و JavaScript چیه؟", ToolType.CHAT, "سوال فنی"),
            ("توضیح مفهوم", "Machine Learning رو توضیح بده", ToolType.CHAT, "درخواست توضیح"),
            ("English Chat", "What is artificial intelligence?", ToolType.CHAT, "تست زبان انگلیسی"),
        ]
        
        for test_name, request, expected, desc in tests:
            await self.run_single_test(test_name, request, expected, desc)
    
    async def test_system_category(self):
        """تست دسته SYSTEM"""
        self.print_test_header("دسته SYSTEM - اطلاعات سیستم", 2, 6)
        
        tests = [
            ("CPU درصد", "CPU چقدره؟", ToolType.SYSTEM, "تست دریافت اطلاعات CPU"),
            ("RAM آزاد", "چقدر RAM آزاد دارم؟", ToolType.SYSTEM, "تست حافظه آزاد"),
            ("فضای دیسک", "فضای دیسک چقدر باقی مونده؟", ToolType.SYSTEM, "تست فضای ذخیره‌سازی"),
            ("اطلاعات کامل", "وضعیت سیستم من چطوره؟", ToolType.SYSTEM, "تست اطلاعات کامل"),
            ("Memory Usage", "How much memory am I using?", ToolType.SYSTEM, "تست انگلیسی"),
            ("تعداد هسته", "CPU من چند هسته داره؟", ToolType.SYSTEM, "تست تعداد هسته‌ها"),
        ]
        
        for test_name, request, expected, desc in tests:
            await self.run_single_test(test_name, request, expected, desc)
    
    async def test_desktop_category(self):
        """تست دسته DESKTOP"""
        self.print_test_header("دسته DESKTOP - کنترل دسکتاپ", 3, 6)
        
        tests = [
            ("باز کردن نوت‌پد", "باز کن notepad", ToolType.DESKTOP, "باز کردن Notepad"),
            ("اجرای Calculator", "اجرا کن Calculator", ToolType.DESKTOP, "باز کردن ماشین‌حساب"),
            ("باز کردن پوشه", "باز کن This PC", ToolType.DESKTOP, "باز کردن File Explorer"),
            ("English Launch", "open notepad", ToolType.DESKTOP, "تست انگلیسی"),
            ("باز کردن Chrome", "مرورگر کروم رو باز کن", ToolType.DESKTOP, "باز کردن مرورگر"),
        ]
        
        print(f"{TestColors.WARNING}⚠️  توجه: این تست‌ها برنامه‌ها را واقعاً باز می‌کنند!{TestColors.ENDC}\n")
        
        for test_name, request, expected, desc in tests:
            await self.run_single_test(test_name, request, expected, desc)
            # کمی صبر کنیم تا برنامه باز شود
            await asyncio.sleep(1)
    
    async def test_browser_category(self):
        """تست دسته BROWSER"""
        self.print_test_header("دسته BROWSER - جستجوی وب", 4, 6)
        
        tests = [
            ("هوای امروز", "هوا امروز چطوره؟", ToolType.BROWSER, "جستجوی وضعیت آب و هوا"),
            ("قیمت ارز", "قیمت دلار چقدره؟", ToolType.BROWSER, "جستجوی قیمت"),
            ("اخبار", "آخرین اخبار تهران", ToolType.BROWSER, "جستجوی اخبار"),
            ("Weather Check", "what's the weather today?", ToolType.BROWSER, "تست انگلیسی"),
        ]
        
        print(f"{TestColors.WARNING}⚠️  توجه: Browser integration هنوز در حال توسعه است{TestColors.ENDC}\n")
        
        for test_name, request, expected, desc in tests:
            await self.run_single_test(test_name, request, expected, desc)
    
    async def test_mixed_scenarios(self):
        """تست سناریوهای ترکیبی"""
        self.print_test_header("سناریوهای ترکیبی و پیچیده", 5, 6)
        
        tests = [
            ("درخواست مبهم", "نوت‌پد", ToolType.DESKTOP, "درخواست بدون فعل"),
            ("چند منظوره", "Chrome", ToolType.DESKTOP, "نام برنامه تنها"),
            ("سوال + عمل", "میشه نوت‌پد رو باز کنی؟", ToolType.DESKTOP, "سوال محترمانه"),
            ("فارسی + انگلیسی", "باز کن Calculator", ToolType.DESKTOP, "ترکیب دو زبان"),
        ]
        
        for test_name, request, expected, desc in tests:
            await self.run_single_test(test_name, request, expected, desc)
    
    async def test_edge_cases(self):
        """تست موارد خاص و لبه‌ای"""
        self.print_test_header("موارد خاص و Edge Cases", 6, 6)
        
        tests = [
            ("رشته خالی", "", ToolType.CHAT, "تست ورودی خالی"),
            ("فقط فاصله", "   ", ToolType.CHAT, "تست فاصله‌های خالی"),
            ("کاراکتر خاص", "!@#$%", ToolType.CHAT, "تست کاراکترهای خاص"),
            ("عدد", "12345", ToolType.CHAT, "تست عدد تنها"),
            ("رشته خیلی طولانی", "سلام " * 100, ToolType.CHAT, "تست ورودی طولانی"),
        ]
        
        for test_name, request, expected, desc in tests:
            await self.run_single_test(test_name, request, expected, desc)
    
    def print_summary(self):
        """چاپ خلاصه نتایج"""
        print(f"\n{TestColors.HEADER}{'='*60}{TestColors.ENDC}")
        print(f"{TestColors.HEADER}📊 خلاصه نتایج تست{TestColors.ENDC}")
        print(f"{TestColors.HEADER}{'='*60}{TestColors.ENDC}\n")
        
        # آمار کلی
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📝 تعداد کل تست‌ها: {TestColors.BOLD}{self.total_tests}{TestColors.ENDC}")
        print(f"✅ تست‌های موفق: {TestColors.OKGREEN}{self.passed_tests}{TestColors.ENDC}")
        print(f"❌ تست‌های ناموفق: {TestColors.FAIL}{self.failed_tests}{TestColors.ENDC}")
        print(f"📈 درصد موفقیت: {TestColors.BOLD}{success_rate:.1f}%{TestColors.ENDC}\n")
        
        # نمایش نمودار میله‌ای
        bar_length = 40
        filled = int(bar_length * success_rate / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        if success_rate >= 80:
            color = TestColors.OKGREEN
        elif success_rate >= 60:
            color = TestColors.WARNING
        else:
            color = TestColors.FAIL
        
        print(f"Progress: {color}[{bar}] {success_rate:.1f}%{TestColors.ENDC}\n")
        
        # تست‌های ناموفق
        if self.failed_tests > 0:
            print(f"{TestColors.FAIL}❌ تست‌های ناموفق:{TestColors.ENDC}\n")
            for result in self.results:
                if not result['passed']:
                    print(f"   • {result['test_name']}")
                    print(f"     درخواست: {result['request']}")
                    print(f"     انتظار: {result['expected']} | دریافت: {result['actual']}\n")
        
        # میانگین زمان اجرا
        if self.results:
            avg_time = sum(r['time'] for r in self.results) / len(self.results)
            print(f"⏱️  میانگین زمان اجرا: {avg_time:.2f} ثانیه\n")
        
        # نتیجه نهایی
        print(f"{TestColors.HEADER}{'='*60}{TestColors.ENDC}")
        if success_rate >= 80:
            print(f"{TestColors.OKGREEN}{TestColors.BOLD}🎉 تبریک! Master Controller عالی کار می‌کند!{TestColors.ENDC}")
        elif success_rate >= 60:
            print(f"{TestColors.WARNING}{TestColors.BOLD}⚠️  نیاز به بهبود دارد{TestColors.ENDC}")
        else:
            print(f"{TestColors.FAIL}{TestColors.BOLD}❌ مشکلات جدی وجود دارد{TestColors.ENDC}")
        print(f"{TestColors.HEADER}{'='*60}{TestColors.ENDC}\n")
    
    async def run_all_tests(self):
        """اجرای تمام تست‌ها"""
        if not await self.setup():
            return
        
        try:
            # اجرای دسته‌های مختلف تست
            await self.test_chat_category()
            await self.test_system_category()
            await self.test_desktop_category()
            await self.test_browser_category()
            await self.test_mixed_scenarios()
            await self.test_edge_cases()
            
        except KeyboardInterrupt:
            print(f"\n{TestColors.WARNING}⚠️  تست توسط کاربر متوقف شد{TestColors.ENDC}\n")
        except Exception as e:
            print(f"\n{TestColors.FAIL}❌ خطای غیرمنتظره: {e}{TestColors.ENDC}\n")
        finally:
            self.print_summary()


async def main():
    """تابع اصلی"""
    tester = MasterControllerTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    # اجرای تست‌ها
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"{TestColors.FAIL}❌ خطا در اجرای تست: {e}{TestColors.ENDC}")
        sys.exit(1)
