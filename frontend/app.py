import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import gradio as gr
import json
import os
from datetime import datetime
from agent import chat as agent_chat, chat_with_image, chat_history

# ─────────────────────────────────────────
# SAVED CHATS
# ─────────────────────────────────────────
CHATS_FILE = os.path.join(os.path.dirname(__file__), '..', 'Data', 'saved_chats.json')

def load_saved_chats():
    if os.path.exists(CHATS_FILE):
        with open(CHATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_chats(chats):
    with open(CHATS_FILE, "w", encoding="utf-8") as f:
        json.dump(chats, f, ensure_ascii=False, indent=2)

def render_sidebar():
    chats = load_saved_chats()
    html = """
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <div class="sidebar-brand">
        <i class="bi bi-fire brand-icon"></i>
        <div class="brand-text">
            <span class="brand-name">Saffron</span>
            <span class="brand-sub">Recipe Agent</span>
        </div>
    </div>
    <div class="section-label">Recent Chats</div>
    <div class="chat-list">
    """
    if not chats:
        html += """
        <div class='empty-chats'>
            <i class='bi bi-chat-dots' style='font-size:2rem;color:#c9956a;display:block;margin-bottom:8px;'></i>
            <span>No chats yet.<br>Ask me a recipe!</span>
        </div>"""
    else:
        for chat_id, chat_data in sorted(chats.items(), reverse=True):
            title = chat_data.get("title", "New Chat")[:30]
            date = chat_data.get("date", "")
            html += f"""
            <div class="chat-item">
                <i class="bi bi-clock-history chat-icon"></i>
                <div class="chat-info">
                    <span class="chat-title">{title}</span>
                    <span class="chat-date">{date}</span>
                </div>
            </div>
            """
    html += "</div>"
    html += """
    <div class="sidebar-footer">
        <div class="stat-pill"><i class="bi bi-journal-bookmark"></i> 522K Recipes</div>
        <div class="stat-pill"><i class="bi bi-stars"></i> 3 AI Tools</div>
        <div class="stat-pill"><i class="bi bi-geo-alt"></i> 15 Tunisian</div>
    </div>
    """
    return html

# ─────────────────────────────────────────
# STATE
# ─────────────────────────────────────────
current_chat_id = None

def new_chat():
    global current_chat_id
    chat_history.clear()
    chat_history.append({
        "role": "system",
        "content": (
            "You are a helpful food recipe assistant specializing in Tunisian and international cuisine.\n"
            "- Always call RecipeSearch first when the user asks about a recipe.\n"
            "- Call IngredientSubstitute when the user asks for a substitute.\n"
            "- Call WebSearch only if RecipeSearch returns no results.\n"
            "- Be friendly, detailed, and format recipes clearly with ingredients and steps."
        )
    })
    current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    return [], gr.update(value=render_sidebar())

def respond(message, history):
    global current_chat_id
    if not message.strip():
        return "", history, gr.update()
    response = agent_chat(message)
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})
    if current_chat_id is None:
        current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    chats = load_saved_chats()
    chats[current_chat_id] = {
        "title": message[:40],
        "date": datetime.now().strftime("%b %d, %Y"),
        "messages": history
    }
    save_chats(chats)
    return "", history, gr.update(value=render_sidebar())

def handle_image(image_path, history):
    global current_chat_id
    if image_path is None:
        return history, gr.update()
    response = chat_with_image(image_path)
    history.append({"role": "user", "content": "📸 I uploaded a food photo — what dish is this?"})
    history.append({"role": "assistant", "content": response})
    if current_chat_id is None:
        current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    chats = load_saved_chats()
    chats[current_chat_id] = {
        "title": "📸 Photo identification",
        "date": datetime.now().strftime("%b %d, %Y"),
        "messages": history
    }
    save_chats(chats)
    return history, gr.update(value=render_sidebar())

# ─────────────────────────────────────────
# CSS — Warm & Earthy Food Theme
# ─────────────────────────────────────────
css = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=DM+Sans:wght@300;400;500;600&display=swap');
@import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css');

:root {
    --cream:       #fdf6ee;
    --cream2:      #f5ebe0;
    --cream3:      #ede0d4;
    --terracotta:  #c9704a;
    --terra-dark:  #a85535;
    --terra-light: #e8956d;
    --saffron:     #e8a838;
    --sage:        #7a8c6e;
    --bark:        #3b2a1a;
    --bark2:       #4e3824;
    --bark3:       #6b4f34;
    --text:        #2e1f10;
    --text-muted:  #6b4f34;
    --text-dim:    #9c7a5a;
    --border:      #dcc9b6;
    --shadow:      rgba(58, 32, 10, 0.08);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body, .gradio-container {
    background: var(--cream) !important;
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text) !important;
}

.gradio-container { max-width: 100% !important; padding: 0 !important; }
footer { display: none !important; }

/* ── LAYOUT ── */
.main-layout {
    display: flex !important;
    height: 100vh !important;
    overflow: hidden !important;
}

/* ── SIDEBAR ── */
.sidebar {
    width: 280px !important;
    min-width: 280px !important;
    background: var(--bark) !important;
    display: flex !important;
    flex-direction: column !important;
    height: 100vh !important;
    overflow: hidden !important;
    border-right: 3px solid var(--terracotta) !important;
}

.sidebar-brand {
    padding: 22px 20px 18px !important;
    display: flex !important;
    align-items: center !important;
    gap: 14px !important;
    border-bottom: 1px solid var(--bark2) !important;
}

.brand-icon {
    font-size: 2rem !important;
    color: var(--saffron) !important;
    line-height: 1 !important;
}

.brand-name {
    display: block !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    color: var(--cream) !important;
    line-height: 1.1 !important;
}

.brand-sub {
    display: block !important;
    font-size: 0.7rem !important;
    color: var(--terra-light) !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    font-weight: 500 !important;
}

.section-label {
    font-size: 0.65rem !important;
    color: var(--text-dim) !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    font-weight: 600 !important;
    padding: 16px 20px 8px !important;
    color: #9c7a5a !important;
}

.chat-list {
    flex: 1 !important;
    overflow-y: auto !important;
    padding: 6px 10px !important;
    scrollbar-width: thin !important;
    scrollbar-color: var(--bark3) transparent !important;
}

.empty-chats {
    text-align: center !important;
    padding: 30px 16px !important;
    color: #9c7a5a !important;
    font-size: 0.82rem !important;
    line-height: 1.7 !important;
}

.chat-item {
    display: flex !important;
    align-items: flex-start !important;
    gap: 10px !important;
    padding: 10px 12px !important;
    border-radius: 12px !important;
    cursor: pointer !important;
    transition: background 0.18s !important;
    margin-bottom: 3px !important;
}

.chat-item:hover { background: var(--bark2) !important; }

.chat-icon {
    font-size: 0.9rem !important;
    color: var(--terracotta) !important;
    margin-top: 2px !important;
    flex-shrink: 0 !important;
}

.chat-title {
    display: block !important;
    font-size: 0.82rem !important;
    color: var(--cream2) !important;
    font-weight: 500 !important;
    line-height: 1.4 !important;
}

.chat-date {
    display: block !important;
    font-size: 0.68rem !important;
    color: #7a6050 !important;
    margin-top: 2px !important;
}

.sidebar-footer {
    padding: 14px 14px 20px !important;
    border-top: 1px solid var(--bark2) !important;
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 7px !important;
}

.stat-pill {
    background: var(--bark2) !important;
    color: var(--cream3) !important;
    font-size: 0.68rem !important;
    padding: 5px 10px !important;
    border-radius: 20px !important;
    font-weight: 500 !important;
    display: flex !important;
    align-items: center !important;
    gap: 5px !important;
}

.stat-pill i { color: var(--saffron) !important; font-size: 0.8rem !important; }

/* ── NEW CHAT BUTTON ── */
.new-chat-btn {
    padding: 14px 14px 10px !important;
    border-bottom: 1px solid var(--bark2) !important;
}

.new-chat-btn button {
    width: 100% !important;
    background: linear-gradient(135deg, var(--terracotta), var(--terra-dark)) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 11px 16px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 7px !important;
    letter-spacing: 0.3px !important;
}

.new-chat-btn button:hover {
    background: var(--terra-dark) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(168,85,53,0.4) !important;
}

/* ── MAIN AREA ── */
.main-content {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    height: 100vh !important;
    overflow: hidden !important;
    background: var(--cream) !important;
}

/* ── TOP HEADER ── */
.top-header {
    padding: 18px 30px !important;
    background: var(--cream) !important;
    border-bottom: 2px solid var(--cream3) !important;
    display: flex !important;
    align-items: center !important;
    gap: 16px !important;
}

.header-icon {
    width: 46px !important;
    height: 46px !important;
    background: linear-gradient(135deg, var(--terracotta), var(--saffron)) !important;
    border-radius: 14px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 1.35rem !important;
    color: white !important;
    flex-shrink: 0 !important;
    box-shadow: 0 4px 12px rgba(200,112,74,0.35) !important;
}

.header-titles { flex: 1 !important; }

.main-title {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.45rem !important;
    font-weight: 700 !important;
    color: var(--bark) !important;
    line-height: 1.1 !important;
    margin: 0 !important;
}

.main-title span { color: var(--terracotta) !important; }

.main-subtitle {
    font-size: 0.78rem !important;
    color: var(--text-dim) !important;
    margin-top: 2px !important;
    font-weight: 400 !important;
}

.header-badges {
    display: flex !important;
    gap: 8px !important;
    flex-wrap: wrap !important;
}

.badge {
    font-size: 0.72rem !important;
    padding: 5px 12px !important;
    border-radius: 20px !important;
    font-weight: 600 !important;
    display: flex !important;
    align-items: center !important;
    gap: 5px !important;
}

.badge i { font-size: 0.8rem !important; }

.badge-warm {
    background: rgba(232, 168, 56, 0.15) !important;
    color: #8a5a00 !important;
    border: 1px solid rgba(232, 168, 56, 0.5) !important;
}

.badge-sage {
    background: rgba(122, 140, 110, 0.15) !important;
    color: var(--sage) !important;
    border: 1px solid rgba(122, 140, 110, 0.4) !important;
}

.badge-terra {
    background: rgba(201, 112, 74, 0.12) !important;
    color: var(--terra-dark) !important;
    border: 1px solid rgba(201, 112, 74, 0.35) !important;
}

/* ── CHAT AREA ── */
.chat-area {
    flex: 1 !important;
    overflow: hidden !important;
    background: var(--cream) !important;
    padding: 0 !important;
}

.chat-area .chatbot {
    background: transparent !important;
    border: none !important;
    height: 100% !important;
}

/* Style chatbot messages */
.chat-area .message.user {
    background: linear-gradient(135deg, var(--terracotta), var(--terra-dark)) !important;
    color: white !important;
    border-radius: 18px 18px 4px 18px !important;
}

.chat-area .message.bot {
    background: white !important;
    border: 1px solid var(--cream3) !important;
    border-radius: 18px 18px 18px 4px !important;
    box-shadow: 0 2px 8px var(--shadow) !important;
}

/* ── EXAMPLES BAR ── */
.examples-wrap {
    padding: 10px 24px 8px !important;
    background: var(--cream) !important;
    border-top: 1px solid var(--cream3) !important;
}

.examples-wrap label { display: none !important; }

.examples-wrap .examples { display: flex !important; flex-wrap: wrap !important; gap: 7px !important; }

.examples-wrap .examples button {
    background: white !important;
    color: var(--text-muted) !important;
    border: 1.5px solid var(--cream3) !important;
    border-radius: 20px !important;
    font-size: 0.78rem !important;
    padding: 5px 14px !important;
    cursor: pointer !important;
    transition: all 0.18s !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
}

.examples-wrap .examples button:hover {
    border-color: var(--terracotta) !important;
    color: var(--terracotta) !important;
    background: rgba(201,112,74,0.06) !important;
    transform: translateY(-1px) !important;
}

.ex-pill {
    background: white !important;
    color: var(--text-muted) !important;
    border: 1.5px solid var(--cream3) !important;
    border-radius: 20px !important;
    font-size: 0.78rem !important;
    padding: 5px 14px !important;
    cursor: pointer !important;
    transition: all 0.18s !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
}

.ex-pill:hover {
    border-color: var(--terracotta) !important;
    color: var(--terracotta) !important;
    background: rgba(201,112,74,0.06) !important;
    transform: translateY(-1px) !important;
}

/* ── INPUT SECTION ── */
.input-section {
    padding: 14px 24px 20px !important;
    background: var(--cream) !important;
    border-top: 1px solid var(--border) !important;
}

.input-row { display: flex !important; align-items: flex-end !important; gap: 10px !important; }

.input-section textarea {
    background: white !important;
    border: 2px solid var(--cream3) !important;
    border-radius: 16px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 13px 18px !important;
    resize: none !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    box-shadow: 0 2px 8px var(--shadow) !important;
}

.input-section textarea:focus {
    border-color: var(--terracotta) !important;
    outline: none !important;
    box-shadow: 0 0 0 4px rgba(201,112,74,0.12) !important;
}

.input-section textarea::placeholder { color: var(--text-dim) !important; }

/* Send button */
.send-btn button {
    background: linear-gradient(135deg, var(--terracotta), var(--terra-dark)) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 13px 24px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    white-space: nowrap !important;
    display: flex !important;
    align-items: center !important;
    gap: 7px !important;
    box-shadow: 0 3px 12px rgba(168,85,53,0.3) !important;
}

.send-btn button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(168,85,53,0.4) !important;
}

/* Identify button */
.identify-btn button {
    background: white !important;
    color: var(--bark3) !important;
    border: 2px solid var(--cream3) !important;
    border-radius: 14px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 11px 18px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    white-space: nowrap !important;
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
}

.identify-btn button:hover {
    border-color: var(--saffron) !important;
    color: #7a4d00 !important;
    background: rgba(232,168,56,0.08) !important;
}

/* Photo upload */
.photo-upload {
    border: 2px dashed var(--cream3) !important;
    border-radius: 14px !important;
    background: white !important;
    overflow: hidden !important;
    transition: border-color 0.2s !important;
    min-width: 54px !important;
    max-width: 54px !important;
    height: 54px !important;
}

.photo-upload:hover { border-color: var(--terracotta) !important; }

/* ── RESPONSIVE ── */
@media screen and (max-width: 1024px) {
    .sidebar { width: 240px !important; min-width: 240px !important; }
    .header-badges { display: none !important; }
    .top-header { padding: 14px 20px !important; }
}

@media screen and (max-width: 768px) {
    .main-layout { flex-direction: column !important; height: auto !important; }
    .sidebar { width: 100% !important; min-width: 100% !important; height: auto !important; border-right: none !important; border-bottom: 3px solid var(--terracotta) !important; }
    .chat-list { max-height: 160px !important; }
    .main-content { height: 100vh !important; }
    .top-header { padding: 12px 16px !important; gap: 10px !important; }
    .main-title { font-size: 1.2rem !important; }
    .input-section { padding: 12px 14px 16px !important; }
    .send-btn button { padding: 12px 16px !important; font-size: 0.85rem !important; }
    .examples-wrap { padding: 8px 14px !important; }
}

@media screen and (max-width: 480px) {
    .header-icon { width: 38px !important; height: 38px !important; font-size: 1.1rem !important; border-radius: 10px !important; }
    .main-title { font-size: 1.05rem !important; }
    .photo-upload { max-width: 46px !important; min-width: 46px !important; height: 46px !important; }
}
"""

# ─────────────────────────────────────────
# UI
# ─────────────────────────────────────────
with gr.Blocks(title="Saffron · Recipe Agent") as demo:

    with gr.Row(elem_classes="main-layout"):

        # ── SIDEBAR ──
        with gr.Column(elem_classes="sidebar", scale=0, min_width=280):
            sidebar_html = gr.HTML(value=render_sidebar())
            with gr.Row(elem_classes="new-chat-btn"):
                new_chat_btn = gr.Button("＋  New Conversation")

        # ── MAIN ──
        with gr.Column(elem_classes="main-content", scale=1):

            # Header
            gr.HTML("""
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
            <div class="top-header">
                <div class="header-icon">
                    <i class="bi bi-fire"></i>
                </div>
                <div class="header-titles">
                    <h1 class="main-title">Saffron <span>Recipe</span> Agent</h1>
                    <p class="main-subtitle">Tunisian & international cuisine · Powered by AI</p>
                </div>
                <div class="header-badges">
                    <span class="badge badge-warm"><i class="bi bi-stars"></i> 3 AI Tools</span>
                    <span class="badge badge-sage"><i class="bi bi-journal-bookmark"></i> 522K+ Recipes</span>
                    <span class="badge badge-terra"><i class="bi bi-geo-alt"></i> Tunisian Cuisine</span>
                </div>
            </div>
            """)

            # Chat
            with gr.Column(elem_classes="chat-area"):
                chatbot = gr.Chatbot(
                    height=390,
                    show_label=False,
                    render_markdown=True,
                    placeholder="""
                    <div style='text-align:center;padding:60px 24px 40px;font-family:DM Sans,sans-serif;'>
                        <div style='font-size:3rem;margin-bottom:16px;'>🫕</div>
                        <p style='font-family:Playfair Display,serif;font-size:1.2rem;color:#3b2a1a;font-weight:700;margin-bottom:8px;'>
                            What shall we cook today?
                        </p>
                        <p style='font-size:0.88rem;color:#9c7a5a;line-height:1.7;'>
                            Ask me for any recipe — Tunisian, Mediterranean, or international.<br>
                            Or upload a food photo and I'll tell you what it is!
                        </p>
                    </div>
                    """
                )

            # Examples — pure HTML buttons that fill the textbox via JS
            gr.HTML("""
            <div class="examples-wrap">
                <button class="ex-pill" onclick="setPrompt('How do I make Shakshuka?')">🥘 Shakshuka</button>
                <button class="ex-pill" onclick="setPrompt('Traditional Tunisian Couscous recipe')">🍲 Couscous</button>
                <button class="ex-pill" onclick="setPrompt('What can I substitute for harissa?')">🫙 Harissa substitute</button>
                <button class="ex-pill" onclick="setPrompt('Lemon chicken with olives recipe')">🍋 Lemon chicken</button>
                <button class="ex-pill" onclick="setPrompt('Quick Tunisian salad recipe')">🥗 Tunisian salad</button>
                <button class="ex-pill" onclick="setPrompt('How to make Brik à l\\'oeuf?')">🫔 Brik</button>
            </div>
            <script>
            function setPrompt(text) {
                const boxes = document.querySelectorAll('textarea');
                for (const b of boxes) {
                    if (b.placeholder && b.placeholder.includes('recipe')) {
                        b.value = text;
                        b.dispatchEvent(new Event('input', {bubbles: true}));
                        b.focus();
                        break;
                    }
                }
            }
            </script>
            """)

            # Input Row
            with gr.Row(elem_classes="input-section"):
                msg = gr.Textbox(
                    placeholder="Ask for a recipe, ingredient swap, or cooking tip...",
                    show_label=False,
                    lines=1,
                    scale=5,
                )
                image_input = gr.Image(
                    type="filepath",
                    show_label=False,
                    sources=["upload"],
                    height=54,
                    scale=0,
                    min_width=54,
                    elem_classes="photo-upload"
                )
                with gr.Column(scale=0, min_width=110, elem_classes="send-btn"):
                    send_btn = gr.Button("Send  →")
                with gr.Column(scale=0, min_width=120, elem_classes="identify-btn"):
                    identify_btn = gr.Button("🔍 Identify")

    # ── ACTIONS ──
    send_btn.click(respond, [msg, chatbot], [msg, chatbot, sidebar_html])
    msg.submit(respond, [msg, chatbot], [msg, chatbot, sidebar_html])
    new_chat_btn.click(new_chat, outputs=[chatbot, sidebar_html])
    identify_btn.click(handle_image, [image_input, chatbot], [chatbot, sidebar_html])

if __name__ == "__main__":
    demo.launch(share=False, css=css)