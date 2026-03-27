import tkinter as tk
from tkinter import scrolledtext, messagebox
import tkinter.ttk as ttk
import threading
import time
import json
import os
import sys
from datetime import datetime
import pystray
from PIL import Image, ImageDraw
from google import genai

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
WORDS_FILE = os.path.join(BASE_DIR, "words_cache.json")

API_PROVIDERS = [
    "Google Gemini",
    "MS Copilot",
    "ChatGPT",
    "MiniMax",
    "DeepSeek",
    "Qwen",
    "Groq",
    "Mistral",
    "Claude",
    "Cohere",
    "Ollama"
]

DIFFICULTY_LEVELS = [
    "CEFR A1 (入门级)",
    "CEFR A2 (基础级)", 
    "CEFR B1 (中级)",
    "CEFR B2 (中高级)",
    "CEFR C1 (高级)",
    "CEFR C2 (精通级)",
    "雅思词汇",
    "托福词汇",
    "托业词汇",
    "GRE词汇"
]

DEFAULT_WORDS = [
    {"word": "asynchronous", "definition": "异步的", "example": "We use asynchronous communication for remote teams.", "translation": "我们使用异步沟通来配合远程团队。"},
    {"word": "deliverable", "definition": "交付物", "example": "The main deliverable for this sprint is the new feature.", "translation": "本次迭代的主要交付物是新功能。"},
    {"word": "stakeholder", "definition": "利益相关者", "example": "We need to update all stakeholders about the project status.", "translation": "我们需要向所有利益相关者更新项目状态。"},
    {"word": "bandwidth", "definition": "带宽/能力", "example": "I don't have the bandwidth to take on more tasks right now.", "translation": "我现在没有多余的能力承担更多任务。"},
    {"word": "pivot", "definition": "转向/调整", "example": "The startup had to pivot its business model.", "translation": "这家初创公司不得不调整商业模式。"},
    {"word": "synergy", "definition": "协同作用", "example": "There should be more synergy between the two departments.", "translation": "两个部门之间应该有更多的协同作用。"},
    {"word": "leverage", "definition": "利用", "example": "We can leverage our existing resources to launch this campaign.", "example_zh": "我们可以利用现有资源来开展这个活动。"},
    {"word": "actionable", "definition": "可操作的", "example": "We need actionable insights from this data.", "translation": "我们需要从这些数据中获得可操作的见解。"},
    {"word": "workflow", "definition": "工作流程", "example": "Let's review the current workflow for approvals.", "translation": "让我们审核一下当前的审批工作流程。"},
    {"word": "scalable", "definition": "可扩展的", "example": "We need a scalable solution that can grow with demand.", "translation": "我们需要一个可扩展的解决方案来适应增长的需求。"}
]

class EnglishWordApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.load_config()
        self.load_cached_words()
        
        self.setup_tray()
        self.create_word_window()
        
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.start_hourly_timer()
        
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            self.config = {"api_provider": "Google Gemini", "api_key": "", "difficulty": "CEFR B1 (中级)"}
            
    def save_config(self):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
            
    def load_cached_words(self):
        if os.path.exists(WORDS_FILE):
            with open(WORDS_FILE, "r", encoding="utf-8") as f:
                self.cached_words = json.load(f)
        else:
            self.cached_words = DEFAULT_WORDS.copy()
            
    def save_cached_words(self, words):
        self.cached_words = words
        with open(WORDS_FILE, "w", encoding="utf-8") as f:
            json.dump(words, f, ensure_ascii=False, indent=2)
            
    def create_tray_icon(self):
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='#4A90D9')
        draw = ImageDraw.Draw(image)
        draw.ellipse([8, 8, 56, 56], fill='white', outline='#4A90D9', width=2)
        draw.text((20, 22), "E", fill='#4A90D9')
        return image
        
    def setup_tray(self):
        icon = self.create_tray_icon()
        self.tray = pystray.Icon(
            "english_word_reminder",
            icon,
            "英语单词提醒助手",
            menu=pystray.Menu(
                pystray.MenuItem("显示单词", self.show_words),
                pystray.MenuItem("设置API Key", self.show_settings),
                pystray.MenuItem("退出", self.exit_app)
            )
        )
        threading.Thread(target=self.tray.run, daemon=True).start()
        
    def create_word_window(self):
        self.word_window = tk.Toplevel()
        self.word_window.withdraw()
        self.word_window.title("英语单词提醒 - 每日单词")
        self.word_window.geometry("500x600")
        self.word_window.configure(bg='#FFFFFF')
        self.word_window.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        title_frame = tk.Frame(self.word_window, bg='#4A90D9', pady=10)
        title_frame.pack(fill='x')
        
        title_label = tk.Label(
            title_frame, 
            text="每日英语单词", 
            font=("Microsoft YaHei", 16, "bold"),
            bg='#4A90D9',
            fg='white'
        )
        title_label.pack()
        
        self.time_label = tk.Label(
            title_frame,
            text="",
            font=("Microsoft YaHei", 10),
            bg='#4A90D9',
            fg='white'
        )
        self.time_label.pack()
        
        self.word_text = scrolledtext.ScrolledText(
            self.word_window,
            font=("Microsoft YaHei", 11),
            bg='#F5F5F5',
            wrap='word',
            padx=15,
            pady=15
        )
        self.word_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        button_frame = tk.Frame(self.word_window, bg='#FFFFFF', pady=10)
        button_frame.pack(fill='x')
        
        hide_btn = tk.Button(
            button_frame,
            text="隐藏",
            font=("Microsoft YaHei", 12),
            bg='#FF6B6B',
            fg='white',
            padx=30,
            pady=5,
            command=self.hide_window,
            relief='flat'
        )
        hide_btn.pack(side='right', padx=20)
        
        refresh_btn = tk.Button(
            button_frame,
            text="刷新单词",
            font=("Microsoft YaHei", 12),
            bg='#4A90D9',
            fg='white',
            padx=20,
            pady=5,
            command=self.fetch_and_display_words,
            relief='flat'
        )
        refresh_btn.pack(side='left', padx=20)
        
    def fetch_words(self):
        provider = self.config.get("api_provider", "Google Gemini")
        if provider == "MS Copilot":
            return self.fetch_from_copilot()
        elif provider == "ChatGPT":
            return self.fetch_from_chatgpt()
        elif provider == "MiniMax":
            return self.fetch_from_minimax()
        elif provider == "DeepSeek":
            return self.fetch_from_deepseek()
        elif provider == "Qwen":
            return self.fetch_from_qwen()
        elif provider == "Groq":
            return self.fetch_from_groq()
        elif provider == "Mistral":
            return self.fetch_from_mistral()
        elif provider == "Claude":
            return self.fetch_from_claude()
        elif provider == "Cohere":
            return self.fetch_from_cohere()
        elif provider == "Ollama":
            return self.fetch_from_ollama()
        else:
            return self.fetch_from_gemini()

    def fetch_from_gemini(self):
        if not self.config.get("api_key"):
            return None
            
        try:
            client = genai.Client(api_key=self.config["api_key"])
            difficulty = self.config.get("difficulty", "CEFR B1 (中级)")
            
            prompt = f"""请提供10个{difficulty}级别的英语单词。请确保单词符合该难度等级。

请按以下JSON格式返回（只需要返回JSON，不需要其他内容）：
[
  {{"word": "单词", "definition": "中文解释", "example": "英文例句", "translation": "例句中文翻译"}},
  ...
]

要求：
1. 单词必须符合{difficulty}难度级别
2. 例句要自然、地道
3. 中文解释要准确、简洁
4. 返回有效的JSON数组"""

            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=prompt
            )
            text = response.text.strip()
            
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            words = json.loads(text.strip())
            return words
            
        except Exception as e:
            print(f"API Error: {e}")
            return None

    def fetch_from_copilot(self):
        try:
            import requests
            difficulty = self.config.get("difficulty", "CEFR B1 (中级)")
            
            prompt = f"""请提供10个{difficulty}级别的英语单词。请确保单词符合该难度等级。

请按以下JSON格式返回（只需要返回JSON，不需要其他内容）：
[
  {{"word": "单词", "definition": "中文解释", "example": "英文例句", "translation": "例句中文翻译"}},
  ...
]

要求：
1. 单词必须符合{difficulty}难度级别
2. 例句要自然、地道
3. 中文解释要准确、简洁
4. 返回有效的JSON数组"""

            endpoint = self.config.get("copilot_endpoint", "")
            if not endpoint:
                return None

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.get('api_key', '')}"
            }
            
            payload = {
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000
            }
            
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                text = text.strip()
                
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                    
                words = json.loads(text.strip())
                return words
            else:
                print(f"Copilot API Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"API Error: {e}")
            return None

    def fetch_from_chatgpt(self):
        try:
            import requests
            difficulty = self.config.get("difficulty", "CEFR B1 (中级)")
            
            prompt = f"""请提供10个{difficulty}级别的英语单词。请确保单词符合该难度等级。

请按以下JSON格式返回（只需要返回JSON，不需要其他内容）：
[
  {{"word": "单词", "definition": "中文解释", "example": "英文例句", "translation": "例句中文翻译"}},
  ...
]

要求：
1. 单词必须符合{difficulty}难度级别
2. 例句要自然、地道
3. 中文解释要准确、简洁
4. 返回有效的JSON数组"""

            endpoint = self.config.get("chatgpt_endpoint", "https://api.openai.com/v1/chat/completions")
            api_key = self.config.get("api_key", "")
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000
            }
            
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                text = text.strip()
                
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                    
                words = json.loads(text.strip())
                return words
            else:
                print(f"ChatGPT API Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"API Error: {e}")
            return None

    def fetch_from_minimax(self):
        try:
            import requests
            difficulty = self.config.get("difficulty", "CEFR B1 (中级)")
            
            prompt = f"""请提供10个{difficulty}级别的英语单词。请确保单词符合该难度等级。

请按以下JSON格式返回（只需要返回JSON，不需要其他内容）：
[
  {{"word": "单词", "definition": "中文解释", "example": "英文例句", "translation": "例句中文翻译"}},
  ...
]

要求：
1. 单词必须符合{difficulty}难度级别
2. 例句要自然、地道
3. 中文解释要准确、简洁
4. 返回有效的JSON数组"""

            endpoint = self.config.get("minimax_endpoint", "")
            api_key = self.config.get("api_key", "")
            model = self.config.get("minimax_model", "abab6.5s-chat")
            
            if not endpoint:
                return None

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000
            }
            
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                text = text.strip()
                
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                    
                words = json.loads(text.strip())
                return words
            else:
                print(f"MiniMax API Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"API Error: {e}")
            return None

    def fetch_from_deepseek(self):
        return self._fetch_generic("DeepSeek", "https://api.deepseek.com/v1/chat/completions", "deepseek-chat")

    def fetch_from_qwen(self):
        return self._fetch_generic("Qwen", None, "qwen-turbo")

    def fetch_from_groq(self):
        return self._fetch_generic("Groq", "https://api.groq.com/openai/v1/chat/completions", "mixtral-8x7b-32768")

    def fetch_from_mistral(self):
        return self._fetch_generic("Mistral", "https://api.mistral.ai/v1/chat/completions", "mistral-small")

    def fetch_from_claude(self):
        return self._fetch_generic("Claude", "https://api.anthropic.com/v1/messages", "claude-3-haiku-20240307")

    def fetch_from_cohere(self):
        return self._fetch_generic("Cohere", "https://api.cohere.ai/v1/chat", "command-r")

    def fetch_from_ollama(self):
        try:
            import requests
            difficulty = self.config.get("difficulty", "CEFR B1 (中级)")
            
            prompt = f"""请提供10个{difficulty}级别的英语单词。请确保单词符合该难度等级。

请按以下JSON格式返回（只需要返回JSON，不需要其他内容）：
[
  {{"word": "单词", "definition": "中文解释", "example": "英文例句", "translation": "例句中文翻译"}},
  ...
]

要求：
1. 单词必须符合{difficulty}难度级别
2. 例句要自然、地道
3. 中文解释要准确、简洁
4. 返回有效的JSON数组"""

            endpoint = self.config.get("ollama_endpoint", "http://localhost:11434/api/chat")
            model = self.config.get("ollama_model", "llama3")
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            }
            
            response = requests.post(endpoint, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                text = result.get("message", {}).get("content", "")
                text = text.strip()
                
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                    
                words = json.loads(text.strip())
                return words
            else:
                print(f"Ollama API Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"API Error: {e}")
            return None

    def _fetch_generic(self, name, default_endpoint, default_model):
        try:
            import requests
            difficulty = self.config.get("difficulty", "CEFR B1 (中级)")
            
            prompt = f"""请提供10个{difficulty}级别的英语单词。请确保单词符合该难度等级。

请按以下JSON格式返回（只需要返回JSON，不需要其他内容）：
[
  {{"word": "单词", "definition": "中文解释", "example": "英文例句", "translation": "例句中文翻译"}},
  ...
]

要求：
1. 单词必须符合{difficulty}难度级别
2. 例句要自然、地道
3. 中文解释要准确、简洁
4. 返回有效的JSON数组"""

            endpoint = self.config.get(f"{name.lower()}_endpoint", default_endpoint)
            api_key = self.config.get("api_key", "")
            model = self.config.get(f"{name.lower()}_model", default_model)
            
            if not endpoint:
                return None

            headers = {
                "Content-Type": "application/json"
            }
            if api_key:
                if name == "Claude":
                    headers["x-api-key"] = api_key
                    headers["anthropic-version"] = "2023-06-01"
                else:
                    headers["Authorization"] = f"Bearer {api_key}"
            
            if name == "Claude":
                payload = {
                    "model": model,
                    "max_tokens": 2000,
                    "messages": [{"role": "user", "content": prompt}]
                }
            else:
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2000
                }
            
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if name == "Claude":
                    text = result.get("content", [{}])[0].get("text", "")
                else:
                    text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                text = text.strip()
                
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                    
                words = json.loads(text.strip())
                return words
            else:
                print(f"{name} API Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"API Error: {e}")
            return None
            
    def display_words(self, words):
        self.word_text.delete('1.0', 'end')
        
        for i, item in enumerate(words, 1):
            word = item.get("word", "")
            definition = item.get("definition", "")
            example = item.get("example", "")
            translation = item.get("translation", "")
            
            self.word_text.insert('end', f"{i}. {word}\n", 'word')
            self.word_text.insert('end', f"   释义：{definition}\n\n", 'definition')
            self.word_text.insert('end', f"   例句：{example}\n", 'example')
            self.word_text.insert('end', f"   翻译：{translation}\n\n", 'translation')
            
        self.word_text.tag_config('word', font=("Microsoft YaHei", 12, "bold"), foreground='#4A90D9')
        self.word_text.tag_config('definition', font=("Microsoft YaHei", 11), foreground='#333333')
        self.word_text.tag_config('example', font=("Microsoft YaHei", 10, "italic"), foreground='#666666')
        self.word_text.tag_config('translation', font=("Microsoft YaHei", 10), foreground='#888888')
        
        now = datetime.now().strftime("%H:%M")
        self.time_label.config(text=f"更新时间: {now}")
        
    def fetch_and_display_words(self):
        words = self.fetch_words()
        
        if words:
            self.save_cached_words(words)
            self.display_words(words)
        else:
            self.display_words(self.cached_words)
            if not self.config.get("api_key"):
                messagebox.showwarning("提示", "请先设置API Key！")
                
    def show_words(self):
        self.fetch_and_display_words()
        
        self.word_window.update_idletasks()
        width = self.word_window.winfo_width()
        height = self.word_window.winfo_height()
        screen_width = self.word_window.winfo_screenwidth()
        screen_height = self.word_window.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.word_window.geometry(f"{width}x{height}+{x}+{y}")
        self.word_window.deiconify()
        self.word_window.lift()
        self.word_window.focus_force()
        
    def hide_window(self):
        self.word_window.withdraw()
        
    def show_settings(self):
        settings_window = tk.Toplevel()
        settings_window.title("设置")
        settings_window.geometry("500x500")
        settings_window.resizable(False, False)
        
        main_frame = tk.Frame(settings_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(main_frame, text="API Provider:", font=("Microsoft YaHei", 11)).grid(row=0, column=0, sticky='w', pady=5)
        
        provider_var = tk.StringVar(value=self.config.get("api_provider", "Google Gemini"))
        provider_combo = ttk.Combobox(
            main_frame, 
            textvariable=provider_var,
            values=API_PROVIDERS,
            width=25,
            state="readonly"
        )
        provider_combo.grid(row=0, column=1, pady=5)
        
        tk.Label(main_frame, text="API Key:", font=("Microsoft YaHei", 11)).grid(row=1, column=0, sticky='w', pady=5)
        
        api_key_var = tk.StringVar(value=self.config.get("api_key", ""))
        api_key_entry = tk.Entry(main_frame, textvariable=api_key_var, width=40, font=("Microsoft YaHei", 10))
        api_key_entry.grid(row=1, column=1, pady=5)
        
        tk.Label(main_frame, text="Endpoint:", font=("Microsoft YaHei", 11)).grid(row=2, column=0, sticky='w', pady=5)
        
        endpoint_var = tk.StringVar(value=self.config.get("copilot_endpoint", ""))
        endpoint_entry = tk.Entry(main_frame, textvariable=endpoint_var, width=40, font=("Microsoft YaHei", 10))
        endpoint_entry.grid(row=2, column=1, pady=5)
        
        tk.Label(main_frame, text="Model:", font=("Microsoft YaHei", 11)).grid(row=3, column=0, sticky='w', pady=5)
        
        model_var = tk.StringVar(value=self.config.get("minimax_model", ""))
        model_entry = tk.Entry(main_frame, textvariable=model_var, width=40, font=("Microsoft YaHei", 10))
        model_entry.grid(row=3, column=1, pady=5)
        
        tk.Label(main_frame, text="Ollama Model:", font=("Microsoft YaHei", 11)).grid(row=4, column=0, sticky='w', pady=5)
        
        ollama_model_var = tk.StringVar(value=self.config.get("ollama_model", "llama3"))
        ollama_model_entry = tk.Entry(main_frame, textvariable=ollama_model_var, width=40, font=("Microsoft YaHei", 10))
        ollama_model_entry.grid(row=4, column=1, pady=5)
        
        tk.Label(main_frame, text="单词难度:", font=("Microsoft YaHei", 11)).grid(row=5, column=0, sticky='w', pady=5)
        
        difficulty_var = tk.StringVar(value=self.config.get("difficulty", "CEFR B1 (中级)"))
        difficulty_combo = ttk.Combobox(
            main_frame, 
            textvariable=difficulty_var,
            values=DIFFICULTY_LEVELS,
            width=27,
            state="readonly"
        )
        difficulty_combo.grid(row=5, column=1, pady=5)
        
        def on_provider_change(*args):
            provider = provider_var.get()
            if provider in ["MS Copilot", "ChatGPT", "MiniMax", "DeepSeek", "Groq", "Mistral", "Claude", "Cohere"]:
                api_key_entry.config(show="*")
            elif provider == "Ollama":
                api_key_entry.config(show="")
                endpoint_var.set("http://localhost:11434/api/chat")
            else:
                api_key_entry.config(show="")
                
        provider_var.trace("w", on_provider_change)
        
        def save_settings():
            provider = provider_var.get()
            self.config["api_provider"] = provider
            self.config["api_key"] = api_key_var.get().strip()
            self.config["copilot_endpoint"] = endpoint_var.get().strip()
            self.config["chatgpt_endpoint"] = endpoint_var.get().strip()
            self.config["minimax_endpoint"] = endpoint_var.get().strip()
            self.config["minimax_model"] = model_var.get().strip()
            self.config["deepseek_endpoint"] = endpoint_var.get().strip()
            self.config["deepseek_model"] = model_var.get().strip()
            self.config["qwen_endpoint"] = endpoint_var.get().strip()
            self.config["qwen_model"] = model_var.get().strip()
            self.config["groq_endpoint"] = endpoint_var.get().strip()
            self.config["groq_model"] = model_var.get().strip()
            self.config["mistral_endpoint"] = endpoint_var.get().strip()
            self.config["mistral_model"] = model_var.get().strip()
            self.config["claude_endpoint"] = endpoint_var.get().strip()
            self.config["claude_model"] = model_var.get().strip()
            self.config["cohere_endpoint"] = endpoint_var.get().strip()
            self.config["cohere_model"] = model_var.get().strip()
            self.config["ollama_endpoint"] = endpoint_var.get().strip()
            self.config["ollama_model"] = ollama_model_var.get().strip()
            self.config["difficulty"] = difficulty_var.get()
            self.save_config()
            messagebox.showinfo("成功", "设置已保存！")
            settings_window.destroy()
            
        tk.Button(main_frame, text="保存", command=save_settings, bg='#4A90D9', fg='white', padx=20).grid(row=6, column=0, columnspan=2, pady=15)
        
    def exit_app(self):
        self.tray.stop()
        self.root.quit()
        
    def start_hourly_timer(self):
        def timer_loop():
            while True:
                time.sleep(3600)
                self.root.after(0, self.show_words)
                
        threading.Thread(target=timer_loop, daemon=True).start()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = EnglishWordApp()
    app.run()
