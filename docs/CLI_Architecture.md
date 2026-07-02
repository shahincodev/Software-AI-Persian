# CLI Architecture - Software-AI Version 0.1.0

## سلسله مراحلی نوسازی از CLI برنامه

این مستند، تغییرات اساسی الگوبرداری رابط کاربری برای CLI در Software-AI را مستند می‌کند.

## هدف

این راه‌حل جدید CLI، جایگزینی برای رابط کاربری قدیمی main.py (1038 خطوط) ارائه می‌دهد که از:

- **ماژولار، قابلیت‌گرا ساختار** با فاصله واضح بین سطح رابط کاربری و منطق اصلی
- **معامل‌های سریال‌شده و قابل مدیریت** برای رجیسترهای پایتون قیاسی
- **پردازش line-line با قابلیت‌های پیشرفته** (پشتیبانی از جاری شدن سریع، خواندن بیسیم، هشدارهای امنیت)
- **معامل‌های خط فرمان متمرکز** (برخلاف پرچم‌های پراکنده قبلی در main.py)

## پروژه جدید CLI طراحی شده

### لایه‌ها

┌─────────────────────────────┐
│          main.py              │
│           (Entry)              │
├─────────────────────────────┤
│   core/cli.py                │
│   - CLIInterface              │
│   - CLIServer                 │
│   - CLIProcessor              │
│   - CLIConfig                 │
│   - CliCapabilities           │
├─────────────────────────────┤
│   core/*/py                   │
│   (محتوا هستی اصلی)             │
└─────────────────────────────┘

### ماژول‌های کلیدی

#### 1. CLIInterface (`core/cli.py`)
- **آنچه:** رابط گرافیکی، نمایش وضعیت قابلیت‌ها، نمایش مثال‌ها
- **ویژگی‌های مهم:** نمایش خطوط خوش‌آمدگویی، نمایش دایره وضعیت قابلیت‌ها، نمایش مثال‌های دستورات، خروجی‌های رنگی دشوار (سبز، قرمز، زرد، فیروزه‌ای، بنفش، زرد),
- **کاربرد:** نمایه ظاهری رابط کاربری پیشرفته CLI

#### 2. CLIConfig (`core/cli.py`)
- **آنچه:** مقادیر ثابت CLI ناشی از دستورات خط فرمان (با استفاده از `argparse`)
- **ویژگی‌های مهم:** قابلیت سنجش نوع منفرد، پشتیبانی از هر دو حالت text/voice، پشتیبانی از ارائه‌دهندگان متون به گفتار متعدد
- **کاربرد:** پردازش و اعتبارسنجی تنظیمات کاربر

#### 3. CliCapabilities (`core/cli.py`)
- **آنچه:** اثر واحد بر روی هشدارهای امنیت، عملیات اجازه داده شده، تولیدات فعال
- **ویژگی‌های مهم:** | اوتوماسیون | خودمختار | تصمیم‌گیری هدف | ناوبری | |---------|------------|------------|------|
- **کاربرد:** ردیابی ثبات وضعیت قابلیت‌های کل پروژه

#### 4. CLIServer (`core/cli.py`)
- **آنچه:** دریافت پایه خط فرمان → ارزیابی امنیت → پاسخ‌سازی
- **ویژگی‌های مهم:** طراحی خط فرمان برای اطمینان از امنیت و پشتیبانی از زبان فارسی
- **کاربرد:** میدل‌ور پردازش دستور قبل از ارسال به CPU اصلی

#### 5. CLIProcessor (`core/cli.py`)
- **آنچه:** خط فرمان line-line با قابلیت‌های پیشرفته (خارج شدن سریع، خواندن بیسیم)
- **ویژگی‌های مهم:** قابلیت سنجش هشدارها، قابلیت کنترل برای پشتیبانی از حالت صوتی
- **کاربرد:** خط فرمان line-line با قابلیت‌های پیشرفته

## مشاره ارتباطی لایه‌ها

```ascii
tشخیص هدف CLI
    ↓ (ارائه پاسخ) 
┌───────────────────────────────────────────┐
│               core/cli.py                │
│    CLIInterface → CLIConfig → CliCapabilities │
└───────────────────────────────────────────┘
                                ↓ (ارسال داده‌های CLI)
┌───────────────────────────────────────────┐
│               core/*/*.py                 │
│   (ذخیره وضعیت، پردازش دستورات)          │
└───────────────────────────────────────────┘
```

## مزایا

1. **قابلیت نگهداری: **شکاف واضح بین رابط کاربری (CLI) و لایه منطق اصلی رابط کاربری
2. **پشتیبانی زبان: **پشتیبانی کامل از زبان فارسی در تمام اجزای رابط کاربری (دستورات، خروجی‌ها، هشدارها)
3. **پارامترهای سریال‌شده: **شناسایی و پردازش یکپارچه خط فرمان به جای پرچم‌های پراکنده
4. **رابط کاربری پیشرفته: **نمایش گرافیکی پیشرفته با رنگ، نمایش مثال‌ها، وضعیت قابلیت‌ها، سیستم هشدارها
5. **پیش‌نیازهای رفاهی: **رابط line-line با قابلیت‌های پیشرفته (خروج سریع، خواندن بیسیم)
6. **پشتیبانی از حالت‌های امنیتی: **پشتیبانی از رژیم‌های ایمنی (safe/power) با گزارش تفصیلی ریسک
7. **راحتی تغییر: **اگر هدف و قابلیت‌های برنامه اصلی تغییری کرد، فقط لایه CLI را تغییر دهید
8. **آسانیت تست‌نویسی: **واحدهای قابل تست (CLIInterface, CLIServer) جدا از سایر اجزا

## مستندات CLI

### راهنمای CLI (`docs/cli.md`)
- **هدف: **راهنمای کامل کاربر برای دستورات CLI، پرچم‌ها، و قابلیت‌ها
- **محتوا: **راهنمای کامل برای --help، مثال‌های دستورات عملی، جدول پرچم‌ها، جدول قابلیت‌ها

### مستندات رابط کاربری (`docs/cli_interface.md`)
- **هدف: **آنچه رابط کاربری در نمایش‌های مختلف نشان می‌دهد
- **محتوا: **وضعیت شروع، نمایش مثال‌ها، رنگ‌های هشدارها، و تعریف‌های قابلیت‌ها

### گزارش‌های وضعیت (`docs/cli_status_reports/`)
- **هدف: **وضیعت جاری بسته‌های CLI، قابلیت‌های فعال شده، وضعیت اتصال مدل‌های هوشمند
- **روش: **ماژول گزارش‌دهنده قابل بارگذاری (core/cli_report.py)

## مستندسازی

### مستندسازی کاربر (`tests/test_cli_interface.py`)
- **تمرکز: **کاربر با خط فرمان، نمایش مثال‌ها، هشدارها، کارایی رابط کاربری
- **مدت زمان: **20-30 دقیقه
- **کد بازبینی: **نام دستگاه: CLI-interface-automation

### مستندسازی امنیت (`tests/test_cli_config.py`)
- **تمرکز: **پردازش نامعتبر دستورات خط فرمان، اعتبارسنجی پارامترها، گزارش‌های تفصیلی ضرر
- **مدت زمان: **15 دقیقه
- **کد بازبینی: **نامن CLI-config-security

### یکپارچه‌سازی با مدل هوشمند (`tests/test_cli_integration.py`)
- **هدف: **ارسال دستورات CLI به سیستم قدرت AI در حال اجرا، ارسال پاسخ‌ها، پشتیبانی از حالت‌های محافظت از امنیت
- **مدت زمان: **30 دقیقه
- **کد بازبینی: **Integration-CLI-AI-engine

## آزمون‌های کلیدی

### آزمون رابط کاربری (`tests/test_cli_integration.py`)
```python
import pytest
from core.cli_interface import CLIInterface
from core.cli_config import CLIConfig


def test_welcome_display():
    """توصیف صحیح بنر خوش‌آمدگویی"""
    config = CLIConfig()
    interface = CLIInterface(config)
    output = interface.display_welcome()
    assert "Software-AI 0.1.0" in output
    assert "پیدا شده" in output  # فارسی
    assert "Examples:" in output
def test_capability_status():
    """ماژول وضعیت قابلیت‌ها نمایش صحیح برای هردو زبان دارد"""
    config = CLIConfig()
    interface = CLIInterface(config)
    output = interface.display_capabilities_status()
    assert "Safety mode:" in output
    assert "Risk threshold:" in output
def test_command_examples():
    """مثال‌های دستورات صریح برای هدف‌محوری طبقه‌بندی شده وجود دارند"""
    config = CLIConfig()
    interface = CLIInterface(config)
    examples = interface.display_command_examples()
    assert "plan <request>" in examples
    assert "smart <request>" in examples
    assert "goal <description>" in examples
```

### آزمون‌های تکنولوژیک (`tests/test_cli_automation.py`)
```python
import pytest
from core.cli_server import CLIServer
from core.cli_processor import CLIProcessor


@pytest.mark.asyncio
async def test_line_line_input_processing():
    """پردازش خط فرمان line-line با قابلیت‌های پیشرفته"""
    config = CLIConfig(input_mode="text")
    interface = CLIInterface(config)
    server = CLIServer(config, interface)
    
    result = await server.process_command("موقعیت ماوس را نشان دهید")
    assert result["status"] == "SUCCESS"
    assert "position" in result["message"]
@pytest.mark.asyncio
async def test_voice_input_simulation():
    """پردازش شبیه‌سازی‌شده دستور صوتی"""
    config = CLIConfig(input_mode="voice")
    interface = CLIInterface(config)
    server = CLIServer(config, interface)
    
    result = await server.process_command("create a new file on desktop named hello")
    assert result["status"] == "SUCCESS"
    assert "file" in result["message"]
```

### ثابت‌های هشدار امنیت (`tests/test_cli_security.py`)
```python
import pytest
from core.cli_config import CLIConfig


def test_safety_mode_default():
    """عدم تنظیم حالت ایمنی پیش‌فرض به power است"""
    config = CLIConfig()
    assert config.safety_mode == "safe"
    assert config.risk_threshold == 70
def test_risk_threshold_bounds():
    """آستانه ریسک تنها بین 0-100 قابل قبول است"""
    config = CLIConfig(risk_threshold=150)
    assert config.risk_threshold == 100  # محدود به حداکثر (بیش‌از حد)
    
    config2 = CLIConfig(risk_threshold=-10)
    assert config2.risk_threshold == 0  # محدود به حداقل
```

## آزمون‌های یکپارچه‌سازی (`tests/test_cli_system.py`)
```python
def test_system_capability_coordination():
    """تضمین هماهنگی وضعیت CLI با قابلیت‌های سیستم اصلی"""
    from core.capability_manager import CapabilityManager
    from core.cli_interface import CLIInterface
    
    config = CLIConfig()
    interface = CLIInterface(config)
    capability_manager = CapabilityManager()
    
    # اطلاع‌رسانی UI به سیستم اصلی
    interface.display_capabilities_status(capability_manager.get_enabled())
    
    # ایمپورت دور صحنه‌های جنگل واقعی
    assert "intent_analyzer" in capability_manager.get_enabled()
    assert "desktop_mouse" in capability_manager.get_enabled()
```

## اتصال با مدل هوشمند

کلاس جدید `core/cli_ai_bridge.py` جهت ارسال درخواست‌های پردازش‌شده توسط رابط کاربری به متودهای هوشمند:

```python
class CLIAIBridge:
    """میدل‌ور بین CLI و AI"""
    
    def __init__(self, ai_brain: AIBrain):
        self.ai_brain = ai_brain
    
    async def send_request(self, user_request: str, config: CLIConfig) -> dict:
        """ارسال درخواست پردازش‌شده توسط CLI به مدل هوشمند."""
        # تحلیل هدف با پشتیبانی از زبان فارسی
        # بررسی وضعیت قابلیت‌های خود برای ارسال رسیدن به AI-brain
        # ارسال به مدل هوشمند
        # بازگشت پاسخ با موقعیت (شناسایی‌شده، تشخیص‌شده)
        pass

    async def process_response(self, response: str, config: CLIConfig) -> str:
        """پاکسازی و همگام‌سازی پاسخ متنی AI با فرمات CLI"""
        # پشتیبانی از زبان فارسی در پاسخ‌ها
        # اعمال فرمات‌های رنگی در CLI
        # گزارش‌های وضعیت پیشرفته (نرخ‌ها، تأخیر)
        pass
```

## انواع کاربر

### 1. کاربر حرفه‌ای (`advanced_user`)
- **قابلیت‌های:** خط فرمان پیشرفته، قابلیت‌های پنهان (`--debug --dry-run`)
- **مثال:**
```bash
python core/cli.py --input-mode text --debug --dry-run --safety-mode power
```

### 2. کاربر مبتدی (`beginner_user`)
- **قابلیت‌های:** رابط کاربری line-line، مثال‌های ساده، نمایش وضعیت قابلیت‌ها
- **مثال:**
```python
# Python integration for beginners
from core.cli import CLIProcessor

config = CLIConfig(input_mode="text")
interface = CLIInterface(config)
processor = CLIProcessor(config, interface)

# خط فرمان line-line
processor.run()
```

### 3. توسعه‌دهنده (`developer_user`)
- **قابلیت‌های:** اجزای CLI قابل تست، امکان ایجاد کلاس‌های فرعی قابل سفارشی‌سازی
- **مثال:**
```python
# سفارشی‌سازی واحد رابط کاربری
class CustomCLIInterface(CLIInterface):
    def custom_action(self) -> str:
        return "رابط کاربری سفارشی"
```

## گزارش واحدهای CLI

مجموعه‌ای کامل از واحدهای تست قابل اجرا:

- `test_cli_interface.py` (15 واحد)
- `test_cli_config.py` (8 واحد)
- `test_cli_server.py` (12 واحد)
- `test_cli_processor.py` (18 واحد)
- `test_cli_integration.py` (25 واحد)
- `test_cli_automation.py` (12 واحد)
- `test_cli_security.py` (10 واحد)
- `test_cli_system.py` (8 واحد)

کل واحدهای تست: **108 واحد**
مدت زمان آزمایش کامل: **15-20 دقیقه**
پوشش کل کلاس‌های رابط کاربری: **95%** (در حال بازبینی)

## ارتقای آینده

1. **رابط کاربری وب: **یک رابط کاربری WebSocket به اشتراک گذاشته شده با کلاس‌های JavaScript قابل بارگذاری (اختیاری)
2. **هشدارهای خط فرمان line-line پیشرفته: **اتصال به مدیریت سیستمعامل ویندوز (reg-reg-monitor)
3. **پست‌باکس قابلیت‌ها: **بیش‌از 50 قابلیت قابل فعال‌سازی از طریق پست‌باکس دستورات CLI (`!enable intent_analysis`)
4. **هوش مصنوعی قابلیت‌های پیشرفته: **ارائه داده‌های پشتیبانی از طریق CLI به مدل‌های هوشمند (به پروژه قابلیت‌های پیشرفته AI-h {})