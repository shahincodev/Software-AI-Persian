# SPDX-License-Identifier: Proprietary
# Copyright © 2025 Shahin - All Rights Reserved
# Software-AI: AI-Powered Windows Control System

"""
ماژول ورودی/خروجی صوتی برای Software-AI
این ماژول مسئول تبدیل گفتار به متن و متن به گفتار است.
"""

import os
import queue
import threading
import logging
import tempfile
import subprocess
from typing import Optional, Callable, Any, cast, Literal, Tuple
import speech_recognition as sr
from google.cloud import texttospeech
from gtts import gTTS
from elevenlabs.client import ElevenLabs
from langdetect import detect, LangDetectException
import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment
import io

logger = logging.getLogger(__name__)

class VoiceInput: 
    """کلاس مدیریت ورودی صوتی (تبدیل گفتار به متن)"""
    def __init__(self) -> None:
        """مقداردهی اولیه تشخیص گفتار"""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.stop_listening: Optional[Callable[[], None]] = None
        self.audio_queue = queue.Queue()
        self.listening_thread: Optional[threading.Thread] = None
        self.is_listening = False
        self._setup_recognition()

    def _setup_recognition(self) -> None:
        """تنظیم پارامترهای تشخیص صدا و حذف نویز محیط"""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            # تنظیم حساسیت تشخیص صدا
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True

    def listen_once(self, timeout: Optional[int] = None) -> Tuple[str, str]:
        """یک‌بار گوش دادن، تبدیل گفتار به متن و تشخیص زبان.
        
        Args:
            timeout: زمان انتظار به ثانیه (None برای نامحدود)
            
        Returns:
            تاپلی شامل (متن تشخیص داده شده, کد زبان) یا ('', '') در صورت خطا
        """
        try:
            with self.microphone as source:
                logger.info("Listening for voice input...")
                audio = self.recognizer.listen(source, timeout=timeout)

            text = cast(Any, self.recognizer).recognize_google(audio)
            logger.info(f"Recognized text: {text}")
            
            try:
                lang = detect(text)
                logger.info(f"Detected language: {lang}")
                return text, lang
            except LangDetectException:
                logger.warning("Could not detect language, defaulting to English.")
                return text, "en"

        except sr.WaitTimeoutError:
            logger.warning("Listening timed out.")
            return "", ""
        except sr.UnknownValueError:
            logger.error("Could not understand the audio.")
            return "", ""
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return "", ""
        except Exception as e:
            logger.error(f"An unexpected error occurred during listening: {e}")
            return "", ""
        
    def start_continuous(self, callback: Callable[[str], Any]) -> None:
        """شروع گوش دادن مداوم در یک thread جداگانه
        
        Args:
            callback: تابعی که با متن تشخیص داده شده فراخوانی می‌شود
        """
        def listener_thread():
            while self.is_listening:
                text, lang = self.listen_once()
                if text:
                    callback(text)

        self.is_listening = True
        threading.Thread(target=listener_thread, daemon=True).start()

    def stop_continuous(self) -> None:
        """توقف گوش دادن مداوم"""
        self.is_listening = False

class VoiceOutput:
    """کلاس مدیریت خروجی صوتی (تبدیل متن به گفتار)
    
    این کلاس از سه سرویس TTS پشتیبانی می‌کند:
    - ElevenLabs (elevenlabs): کیفیت بسیار بالا، نیازمند API Key
    - Google Cloud TTS (google-cloud): کیفیت بالا، پرداختی
    - gTTS (gtts): رایگان، کیفیت معقول
    """
    
    def __init__(self, tts_provider: Literal["elevenlabs", "google-cloud", "gtts"] = "elevenlabs") -> None:
        """مقداردهی اولیه موتور تبدیل متن به گفتار
        
        Args:
            tts_provider: انتخاب سرویس TTS
                - "elevenlabs": ElevenLabs TTS (niaz be API key)
                - "google-cloud": Google Cloud Text-to-Speech (niaz be etebarname)
                - "gtts": gTTS سرویس رایگان
        """
        self.tts_provider = tts_provider
        self.speaking_queue = queue.Queue()
        self.is_speaking = False
        self.temp_dir = tempfile.mkdtemp()
        
        if self.tts_provider == "elevenlabs":
            api_key = os.environ.get("ELEVENLABS_API_KEY")
            if not api_key:
                raise ValueError("ELEVENLABS_API_KEY dar mohit yaaft nashod.")
            self.elevenlabs_client = ElevenLabs(api_key=api_key)
            logger.info("TTS Provider: ElevenLabs")
        elif self.tts_provider == "google-cloud":
            self.client = texttospeech.TextToSpeechClient()
            self.voice = texttospeech.VoiceSelectionParams(
                language_code="fa-IR",
                name="fa-IR-Standard-A"
            )
            self.audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                speaking_rate=1.0,
                pitch=0.0,
                volume_gain_db=0.0
            )
            logger.info("TTS Provider: Google Cloud Text-to-Speech")
        else:
            logger.info("TTS Provider: gTTS (Free)")
        
        self._start_speaker_thread()

    def _synthesize_speech_google_cloud(self, text: str) -> bytes:
        """تبدیل متن به صدا با استفاده از Google Cloud TTS
        
        Args:
            text: متن برای تبدیل به گفتار
            
        Returns:
            داده‌های صوتی به صورت bytes
        """
        synthesis_input = texttospeech.SynthesisInput(text=text)
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=self.voice,
            audio_config=self.audio_config
        )
        return response.audio_content

    def _synthesize_speech_gtts(self, text: str, lang: str = 'en') -> bytes:
        """تبدیل متن به صدا با استفاده از gTTS با زبان مشخص.
        
        Args:
            text: متن برای تبدیل به گفتار
            lang: کد زبان (مثلاً 'en', 'fa')
            
        Returns:
            داده‌های صوتی به صورت bytes
        """
        temp_mp3 = os.path.join(self.temp_dir, "temp_gtts.mp3")
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(temp_mp3)
            with open(temp_mp3, 'rb') as f:
                return f.read()
        finally:
            if os.path.exists(temp_mp3):
                os.remove(temp_mp3)

    def _synthesize_speech_elevenlabs(self, text: str) -> bytes:
        """تبدیل متن به صدا با استفاده از ElevenLabs
        
        Args:
            text: متن برای تبدیل به گفتار
            
        Returns:
            داده‌های صوتی به صورت bytes
        """
        # انتخاب صدا و مدل - این مقادیر را می‌توانید تغییر دهید
        voice_id = "Rachel" 
        model_id = "eleven_multilingual_v2"
        
        audio_stream = self.elevenlabs_client.text_to_speech.convert(
            text=text,
            voice=voice_id,
            model=model_id,
        )
        
        # جمع‌آوری داده‌های استریم شده در یک متغیر bytes
        audio_bytes = b"".join(chunk for chunk in audio_stream)
        return audio_bytes

    def _synthesize_speech(self, text: str, lang: str = 'en') -> bytes:
        """تبدیل متن به صدا با استفاده از سرویس انتخاب‌شده و زبان مشخص.
        
        Args:
            text: متن برای تبدیل به گفتار
            lang: کد زبان
            
        Returns:
            داده‌های صوتی به صورت bytes
        """
        if self.tts_provider == "elevenlabs":
            # ElevenLabs multilingual v2 automatically detects language
            return self._synthesize_speech_elevenlabs(text)
        elif self.tts_provider == "google-cloud":
            # Google Cloud needs the language code
            return self._synthesize_speech_google_cloud(text) # Note: This function needs to be updated to accept lang
        else:
            return self._synthesize_speech_gtts(text, lang=lang)

    def _play_audio(self, audio_content: bytes, is_mp3: bool = False) -> None:
        """پخش صدا با استفاده از sounddevice و ffplay
        
        Args:
            audio_content: داده‌های صوتی به صورت bytes
            is_mp3: آیا فرمت صوتی MP3 است (برای gTTS و ElevenLabs)
        """
        if is_mp3:
            # برای gTTS و ElevenLabs که MP3 است
            temp_mp3 = os.path.join(self.temp_dir, "temp_audio.mp3")
            try:
                # ذخیره MP3
                with open(temp_mp3, 'wb') as f:
                    f.write(audio_content)
                
                # تلاش برای پخش MP3 با ffplay
                try:
                    import subprocess
                    subprocess.run(["ffplay", "-nodisp", "-autoexit", temp_mp3], 
                                 check=True, 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL,
                                 timeout=30)
                except Exception as play_error:
                    logger.warning(f"ffplay mojod nist ya kar nakard:\n{str(play_error)}")
                    logger.info("baraye pakhsh sahih ffmpeg ra nasb konid: choco install ffmpeg")
            finally:
                if os.path.exists(temp_mp3):
                    os.remove(temp_mp3)
        else:
            # برای Google Cloud که WAV است
            temp_wav = os.path.join(self.temp_dir, "temp_speech.wav")
            with open(temp_wav, "wb") as f:
                f.write(audio_content)
            
            try:
                data, samplerate = sf.read(temp_wav)
                sd.play(data, samplerate)
                sd.wait()
            finally:
                if os.path.exists(temp_wav):
                    os.remove(temp_wav)

    def _start_speaker_thread(self) -> None:
        """راه‌اندازی thread مدیریت صف گفتار"""
        def speaker_thread():
            while True:
                try:
                    item = self.speaking_queue.get()
                    if item is None:
                        break
                    
                    text, lang = item
                    self.is_speaking = True
                    audio_content = self._synthesize_speech(text, lang=lang)
                    
                    is_mp3 = self.tts_provider in ["gtts", "elevenlabs"]
                    self._play_audio(audio_content, is_mp3=is_mp3)
                except Exception as e:
                    logger.error(f"Error in speaker thread: {e}")
                finally:
                    self.is_speaking = False
                    self.speaking_queue.task_done()
        
        self.speaker_thread = threading.Thread(target=speaker_thread, daemon=True)
        self.speaker_thread.start()

    def speak(self, text: str, lang: str = 'en', block: bool = False) -> None:
        """تبدیل متن به گفتار با زبان مشخص.
        
        Args:
            text: متن برای تبدیل به گفتار
            lang: کد زبان
            block: اگر True باشد، منتظر اتمام گفتار می‌ماند
        """
        try:
            self.speaking_queue.put((text, lang))
            if block:
                self.speaking_queue.join()
        except Exception as e:
            logger.error(f"Error adding text to speaking queue: {e}")

    def stop_speaking(self) -> None:
        """توقف فوری گفتار فعلی و پاک‌سازی صف"""
        with self.speaking_queue.mutex:
            self.speaking_queue.queue.clear()

    def shutdown(self) -> None:
        """خاموش کردن موتور تبدیل متن به گفتار"""
        try:
            self.speaking_queue.put(None)  # ارسال سیگنال توقف
            self.speaker_thread.join()
            if os.path.exists(self.temp_dir):
                os.rmdir(self.temp_dir)
        except Exception as e:
            logger.error(f"khata dar khamosh kardan motor: {str(e)}")

class VoiceManager:
    """مدیریت یکپارچه ورودی و خروجی صوتی"""

    def __init__(self, tts_provider: Literal["elevenlabs", "google-cloud", "gtts"] = "elevenlabs") -> None:
        """مقداردهی اولیه مدیر صوتی
        
        Args:
            tts_provider: انتخاب سرویس TTS
                - "elevenlabs": ElevenLabs TTS
                - "google-cloud": Google Cloud Text-to-Speech
                - "gtts": gTTS رایگان
        """
        self.voice_input = VoiceInput()
        self.voice_output = VoiceOutput(tts_provider=tts_provider)

    def listen(self, timeout: Optional[int] = None) -> Tuple[str, str]:
        """گوش دادن یک‌باره و تشخیص زبان.
        
        Args:
            timeout: زمان انتظار به ثانیه
            
        Returns:
            تاپلی از (متن, زبان)
        """
        return self.voice_input.listen_once(timeout)
    
    def speak(self, text: str, lang: str = 'en', block: bool = False) -> None:
        """تبدیل متن به گفتار با زبان مشخص.
        
        Args:
            text: متن برای تبدیل به گفتار
            lang: کد زبان
            block: اگر True باشد، منتظر اتمام گفتار می‌ماند
        """
        self.voice_output.speak(text, lang=lang, block=block)

    def start_conversation(self, callback: Callable[[str], Any]) -> None:
        """شروع مکالمه دوطرفه
        
        Args:
            callback: تابعی که با متن تشخیص داده شده فراخوانی می‌شود
        """
        self.voice_input.start_continuous(callback)

    def stop_conversation(self) -> None:
        """توقف مکالمه دوطرفه"""
        self.voice_input.stop_continuous()
        self.voice_output.stop_speaking()

    def shutdown(self) -> None:
        """بستن تمیز سیستم صوتی"""
        self.stop_conversation()
        self.voice_output.shutdown()
