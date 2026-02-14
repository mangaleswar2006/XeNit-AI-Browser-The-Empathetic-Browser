# 🌐 XeNit AI Browser — The Empathetic Browser

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/PyQt-6-green&logo=qt&logoColor=white" alt="PyQt6">
  <img src="https://img.shields.io/badge/AI-Empathetic-purple" alt="AI powered">
  <img src="https://img.shields.io/badge/Status-Beta-orange" alt="Status Beta">
</p>

### A browser that doesn't just load pages—it cares about how you feel.

**XeNit AI** is a next-generation web browser designed to reduce digital burnout, prevent online conflicts, and provide immediate emotional support. By integrating advanced AI directly into the browsing experience, XeNit acts as a companion that watches out for your well-being.

---

## 🚀 Key Features

### 1. 🆘 Emotional Search Assistant
Feeling down? If you search for phrases like *"I feel lonely"* or *"I am stressed"*, XeNit detects your emotional state and immediately opens a supportive AI chat.
-   **Warm Acknowledgment:** Validates your feelings without judgment.
-   **Resource Finder:** Suggests breathing exercises, calming music, or helplines.
-   **Crisis Support:** Prioritizes safety for severe distress signals.

### 2. 🛡️ Toxicity Blocker & Fight Detection
Stop arguments before they destroy relationships.
-   **Toxicity Shield:** Detects hurtful words in your drafted messages and warns you: *"This could damage your relationship."*
-   **Fight Mode:** Notices rapid, angry typing patterns and suggests: *"Let's take a breath before hitting send."*
-   **Rewrite with Empathy:** One-click AI rewriting to turn aggressive text into constructive communication.

### 3. 💘 Relationship Coach (Social Mode)
Your personal communication expert on WhatsApp, Messenger, and Instagram.
-   **Context-Aware Advice:** Reads the chat vibe and suggests the best way to reply (Polite, Casual, or Empathetic).
-   **Smart Replies:** Generates 3 clickable reply suggestions tailored to the conversation.
-   **Conflict de-escalation:** Helps you navigate tricky social situations.

### 4. 🛑 Burnout Prevention AI
Working too hard? XeNit has your back.
-   **Work Timer:** Tracks continuous usage (default: 2 hours).
-   **Stress Detection:** Monitors search patterns (e.g., "exam stress", "deadline panic").
-   **Break Alerts:** Gently prompts you to take a break with a "Brain Overload" warning and offers a quick 1-minute breathing exercise.

### 5. 🚫 Mental Health Ad Blocker
Protects your peace of mind.
-   **Negative Ad Filtering:** Specifically targets and blocks fear-mongering or depressing ads that can trigger anxiety.
-   **Clean Reading Mode:** Focus on content, not distractions.

### 6. ✨ Smart Automation
-   **Natural Language Controls:** "Open WhatsApp and message Mom" -> Done.
-   **Auto-Fill:** Intelligently fills forms using your stored profile.

---

## 🛠️ Tech Stack

-   **Core Engine:** Python (PyQt6) + QtWebEngine (Chromium-based)
-   **AI Backend:** NVIDIA NIM / Meta Llama 3.1 405B (for nuanced emotional intelligence)
-   **Sentiment Analysis:** Local NLTK + VADER (fast, privacy-first analysis)
-   **UI:** Custom Modern Dark Mode with Glassmorphism effects

---

## 📦 Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/xenit-ai-browser.git
    cd xenit-ai-browser
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Keys**
    -   Get an NVIDIA NIM API Key (or OpenAI key).
    -   Set it in `browser/ai_agent.py` or `.env`.

4.  **Run the Browser**
    ```bash
    python main.py
    ```

---

## 🎮 How to Use

1.  **Launch:** Run `main.py`.
2.  **Browse:** Use it like Chrome (Search, Tabs, Bookmarks).
3.  **Test Emotion AI:**
    -   Type **"I feel lonely"** in the address bar.
    -   Watch the Sidebar open with support.
4.  **Test Toxicity:**
    -   Type a rude message in a text box (e.g., "You are stupid").
    -   See the **Red Warning Overlay** appear.
5.  **Smart Replies:**
    -   Open `web.whatsapp.com`.
    -   Open the Sidebar to see AI suggestions for your chat.

---

## 🔮 Future Roadmap

-   [ ] **Biometric Integration:** Connect with smartwatches to detect stress via heart rate.
-   [ ] **Voice Therapy Mode:** Have full spoken conversations with the AI for deeper support.
-   [ ] **Mobile App:** Bring the empathetic layer to iOS and Android.

---

**Made with ❤️ by XeNit AI Team**
*Building technology that understands humans.*
