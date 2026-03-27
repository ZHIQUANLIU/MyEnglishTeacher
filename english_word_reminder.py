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
            self.config = {"api_key": "", "difficulty": "CEFR B1 (中级)"}
            
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
        
    def fetch_words_from_gemini(self):
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
        words = self.fetch_words_from_gemini()
        
        if words:
            self.save_cached_words(words)
            self.display_words(words)
        else:
            self.display_words(self.cached_words)
            if not self.config.get("api_key"):
                messagebox.showwarning("提示", "请先设置Gemini API Key以获取新单词！")
                
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
        settings_window.geometry("400x220")
        settings_window.resizable(False, False)
        
        tk.Label(settings_window, text="Gemini API Key:", font=("Microsoft YaHei", 11)).pack(pady=(15, 5))
        
        api_key_var = tk.StringVar(value=self.config.get("api_key", ""))
        api_key_entry = tk.Entry(settings_window, textvariable=api_key_var, width=50, font=("Microsoft YaHei", 10))
        api_key_entry.pack(pady=5)
        
        tk.Label(settings_window, text="单词难度:", font=("Microsoft YaHei", 11)).pack(pady=(15, 5))
        
        difficulty_var = tk.StringVar(value=self.config.get("difficulty", "CEFR B1 (中级)"))
        difficulty_combo = tk.ttk.Combobox(
            settings_window, 
            textvariable=difficulty_var,
            values=DIFFICULTY_LEVELS,
            width=30,
            state="readonly"
        )
        difficulty_combo.pack(pady=5)
        
        def save_settings():
            self.config["api_key"] = api_key_var.get().strip()
            self.config["difficulty"] = difficulty_var.get()
            self.save_config()
            messagebox.showinfo("成功", "设置已保存！")
            settings_window.destroy()
            
        tk.Button(settings_window, text="保存", command=save_settings, bg='#4A90D9', fg='white', padx=20).pack(pady=15)
        
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
