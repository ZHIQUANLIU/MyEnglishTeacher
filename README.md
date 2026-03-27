# 英语单词提醒助手

一个简洁的桌面小程序，每小时提醒你学习10个实用的英语单词。

## 功能特点

- 📌 系统托盘运行，不影响正常工作
- ⏰ 每小时自动弹出单词窗口
- 📚 包含中文解释和例句
- 🤖 支持 Google Gemini / MS Copilot API
- 🔒 配置保存在本地

## 支持的API

1. **Google Gemini** - 需要 API Key
2. **MS Copilot** - 需要公司 license + endpoint

## 安装

1. 安装 Python 3.7+
2. 安装依赖：

```bash
pip install pystray Pillow google-genai requests
```

## 使用方法

1. 运行程序：
```bash
python english_word_reminder.py
```

或双击 `start.bat`

2. 程序会最小化到系统托盘（右下角）

3. 首次使用需要设置API：
   - 右键点击托盘图标 → 设置
   - 选择 API Provider
   - 输入 API Key 或 Copilot Endpoint

4. 手动显示单词：
   - 双击托盘图标，或
   - 右键 → 显示单词

5. 隐藏窗口：
   - 点击"隐藏"按钮，或
   - 点击窗口右上角X

6. 退出程序：
   - 右键托盘 → 退出

## 注意事项

- 首次运行会使用内置的默认单词
- 设置 API Key 后才会获取新单词
- 单词会自动缓存到本地文件
