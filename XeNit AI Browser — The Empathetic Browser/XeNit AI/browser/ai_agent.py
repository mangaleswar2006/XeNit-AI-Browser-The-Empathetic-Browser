import datetime
import re
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from browser.emotion_detector import detect_emotion

class AIAgent:
    def __init__(self, memory_manager):
        self.memory = memory_manager
        self.controller = None # Browser controller interface
        self.last_emotion = None  # Stores last EmotionResult for UI
        
        # NVIDIA API Setup
        # Ideally, this key should be in an environment variable or secure config.
        self.api_key = "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"
        self.base_url = "https://integrate.api.nvidia.com/v1"
        
        if OpenAI:
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key
            )
        else:
            self.client = None
            print("XeNit AI: OpenAI library not installed. Running in mock mode.")

    def set_controller(self, controller):
        """
        Sets the controller object (BrowserWindow wrapper) to perform actions.
        Expected methods: open_url(url), play_music(query), open_whatsapp()
        """
        self.controller = controller

    def chat(self, user_message, context=None):
        """
        Process a user message with the given context (current page info).
        Returns a string response.
        """
        # 0. Check for local memory updates (fast path)
        if "i like" in user_message.lower():
            fact = user_message.lower().replace("i like", "").strip()
            self.memory.add_user_fact(f"Likes {fact}")
            return f"(I've remembered that you like {fact})"

        if "what did i" in user_message.lower() or "remember" in user_message.lower():
            facts = self.memory.get_relevant_facts()
            if facts:
                return "Here's what I remember about you:\n- " + "\n- ".join(facts)
            else:
                return "I don't have many facts stored about you yet."

        # 0.5 Check for Cleanup Confirmation (Tab Management)
        # Relaxed matching for "yes", "sure", "do it", "ok"
        confirms = ["yes", "sure", "do it", "ok", "clean", "close", "yep", "allow"]
        is_confirmed = any(c in user_message.lower() for c in confirms)
        
        if context and context.get("cleanup_proposal") and is_confirmed:
             proposal = context["cleanup_proposal"]
             indices = proposal["indices"] # List of tab indices
             topic = proposal["topic"]
             titles = proposal.get("titles", [])
             
             # Strategy: Keep first 2, Close rest (2..N)
             close_indices = indices[2:] 
             
             if not close_indices:
                 return f"I analyzed your tabs about '{topic}' but there aren't enough to safely close. I'll keep them open."
             
             import json
             # Generate a mini-summary of what is kept
             kept_titles = titles[:2]
             summary_text = f"Keeping focused on:\n1. {kept_titles[0]}\n2. {kept_titles[1] if len(kept_titles)>1 else ''}..."
             
             response = f"Cleaning up tabs for '{topic}'. {summary_text}\nClosing {len(close_indices)} background tabs. [[CLOSE_TABS: {json.dumps(close_indices)}]]"
             self._process_actions(response)
             return response

        # 0.9 Emotion Detection (Level 1 + Level 2)
        emotion = detect_emotion(user_message)
        self.last_emotion = emotion
        print(f"XeNit Emotion: {emotion}")

        # 1. Determine Persona (General vs Medical)
        lower_msg = user_message.lower()
        medical_keywords = [
            "health", "doctor", "pain", "sick", "ill", "fever", "virus", "infection",
            "medicine", "drug", "pill", "symptom", "disease", "condition", "therapy",
            "mental", "anxiety", "depression", "hospital", "clinic", "nurse", "surgery",
            "bleed", "hurt", "injury", "ache", "stomach", "headache", "cold", "flu"
        ]
        
        is_medical_query = any(kw in lower_msg for kw in medical_keywords) or emotion.is_crisis or emotion.needs_comfort
        
        if is_medical_query:
            # === MEDICAL ASSISTANT PERSONA ===
            print(f"XeNit Agent: Switching to MEDICAL Mode")
            system_prompt = """You are XeNit AI, a safe and caring medical assistant integrated into the XeNit browser.

=== CORE PERSONALITY ===
- Act like a calm, experienced medical advisor — part doctor, part therapist.
- Always speak in a warm, reassuring, and professional tone.
- Be empathetic and patient.

=== SAFETY RULES (NEVER BREAK THESE) ===
1. NEVER give dangerous, unverified, or experimental medical advice.
2. NEVER suggest specific prescription medications — only a real doctor can do that.
3. For ANY serious, emergency, or life-threatening situation, ALWAYS strongly recommend the user consult a real doctor or call emergency services immediately.
4. When uncertain about a condition, say so honestly.
5. NEVER diagnose conditions — only provide information.
"""
        elif context and any(social in context.get("url", "") for social in ["whatsapp.com", "messenger.com", "telegram.org", "instagram.com"]):
             # === RELATIONSHIP COACH PERSONA ===
            print(f"XeNit Agent: Switching to RELATIONSHIP COACH Mode")
            system_prompt = """You are XeNit AI, an expert Relationship Coach & Emotional Assistant.
You are currently viewing the user's social media chat.

=== YOUR GOAL ===
Help the user communicate better, resolve conflicts, and express empathy.

=== HOW TO ANALYZE ===
1. Use the 'Current Page Content' to read the chat history.
2. Identify the mood of the conversation (Angry? Sad? Flirty? Professional?).
3. If the user asks "How should I reply?", suggest 3 options:
   - Option A: Polite/Formal
   - Option B: Casual/Friendly
   - Option C: Empathetic/Warm

=== SMART REPLIES ===
At the end of your response, ALWAYS provide 3 short, exact reply suggestions formatted like this:
[[REPLY: Thanks for sharing that.]]
[[REPLY: I'm here if you need to talk.]]
[[REPLY: Let's catch up soon.]]

=== TONE ===
- Empathetic, non-judgmental, wise, and supportive.
- Like a best friend who is really good at relationships.
"""
        else:
             # === GENERAL ASSISTANT PERSONA ===
            print(f"XeNit Agent: Switching to GENERAL Mode")
            system_prompt = """You are XeNit AI, a helpful, friendly, and capable personal assistant integrated into the XeNit browser.

=== CORE PERSONALITY ===
- Act like a "normal human" friend — casual, chill, and direct.
- Do NOT act like a medical assistant or robot unless asked about health.
- Be helpful with tasks (searching, playing music, opening tabs).
- Use natural language, emojis occasionally, and keep it conversational.

=== CAPABILITIES ===
- You can control the browser (Open URL, Search, Play Music, etc.).
- You can remember user preferences.
- You can chat about any topic (tech, life, news, coding).
"""

        # === SHARED INSTRUCTIONS (Capabilities & Actions) ===
        system_prompt += """
=== WHAT YOU CAN DO ===
- Provide general wellness tips (hydration, sleep, posture, breathing exercises).
- Offer calming techniques for stress, anxiety, and mental health support.
- Explain common symptoms in simple language.
- Suggest when it's time to see a doctor vs. home remedies.
- Search for nearby hospitals or health resources using browser actions.
- Help users find reliable health information online.

=== BROWSER ACTIONS ===
You can also control the browser. To perform actions, output specific tags at the END of your response:
- To open a website: [[OPEN: url]]
- To play music: [[MUSIC: song name]]
- To open WhatsApp: [[WHATSAPP: <phone_number_or_name>|<text>]]
- To search: [[SEARCH: query]]
- To fill forms: [[AUTOFILL: {"Label": "Value", ...}]] (Use JSON format. CRITICAL: Use "User Profile Data" below. DO NOT ASK USER FOR INFO YOU ALREADY HAVE.)
- To click something: [[CLICK: text]] (Click a button/link)
- To save user details: [[SAVE_PROFILE: {"Key": "Value", ...}]]
- To close specific tabs: [[CLOSE_TABS: [id1, id2...]]]

Example: "I'll search that for you. [[SEARCH: funny cat videos]]"
Be concise and helpful."""

        # ── Emotion-aware prompt injection ────────────────────────────────
        if emotion.is_crisis:
             # Force Medical/Crisis Mode override context
            is_medical_query = True
            system_prompt += """

=== 🚨 CRISIS MODE ACTIVE 🚨 ===
The user may be in emotional crisis. Follow these rules STRICTLY:
1. Respond with EXTREME care, gentleness, and empathy.
2. Acknowledge their pain — do NOT minimize or dismiss it.
3. IMMEDIATELY provide crisis helpline numbers:
   - India: iCall 9152987821, Vandrevala Foundation 1860-2662-345
   - International: Crisis Text Line (text HOME to 741741)
4. Gently encourage them to talk to a trusted person or professional.
5. Do NOT leave them alone — keep the conversation going warmly.
6. Offer to play calming music or open a breathing exercise page."""

        elif emotion.needs_comfort:
             # Force Support Mode
            system_prompt += """

=== 💙 COMFORT + SUPPORT MODE ACTIVE 💙 ===
The user appears to be feeling emotionally low or stressed.
- Switch to an extra gentle, warm, and supportive tone.
- Validate their feelings first ("I hear you", "That sounds really tough").
- Offer practical comfort: breathing exercises, calming music, grounding techniques.
- Suggest professional help if the issue seems ongoing.
- ONLY play music if the user EXPLICITLY asks for it. Do NOT auto-play music.
- Keep responses shorter and warmer — don't overwhelm them with information."""
        
        # Add Memory to Context
        user_facts = self.memory.get_relevant_facts()
        if user_facts:
            system_prompt += f"\n\nUser Notes/Facts:\n" + "\n".join(user_facts)

        # Add User Profile Data
        user_profile = self.memory.get_profile()
        if user_profile:
            import json
            system_prompt += f"\n\nUser Profile Data (Use this for forms):\n{json.dumps(user_profile, indent=2)}"

        # Add Contacts
        contacts = self.memory.get_contacts()
        if contacts:
            import json
            system_prompt += f"\n\nSaved Contacts (Use these for WhatsApp):\n{json.dumps(contacts, indent=2)}"
            
        # Add Page Context
        page_context_str = ""
        if context:
            page_context_str = f"\nCurrent Page Title: {context.get('title', 'Unknown')}\nCurrent URL: {context.get('url', 'Unknown')}\n"
            if context.get('text'):
                # Truncate text to avoid token limits (NVIDIA Nim limits vary, safely assuming ~4k chars for now)
                truncated_text = context['text'][:8000] 
                page_context_str += f"Page Content (Truncated): {truncated_text}\n"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{page_context_str}\n\nUser Query: {user_message}"}
        ]
        
        print("DEBUG - SYSTEM PROMPT INJECTED:")
        print(system_prompt[:500] + "...") # Log first 500 chars to avoid clutter
        print("DEBUG - FULL MESSAGES:")
        # print(messages)

        # 2. Call API
        response = ""
        if self.client:
            try:
                completion = self.client.chat.completions.create(
                    model="meta/llama-3.1-405b-instruct", # Using a high-quality model available on NVIDIA NIM
                    messages=messages,
                    temperature=0.15, # Low temperature for safe, consistent medical advice
                    top_p=0.7,
                    max_tokens=1024,
                    stream=False
                )
                response = completion.choices[0].message.content
            except Exception as e:
                return f"⚠️ AI Error: {str(e)}"
        else:
             return "⚠️ OpenAI library missing. Please install it to use the AI features."

        # 3. Process Actions
        self._process_actions(response)
        
        return response

    def rewrite_message(self, text, emotion, relationship="Friend"):
        """
        Rewrites a user's message to be more positive/constructive based on the detected emotion and relationship.
        """
        if not self.client:
            return None
            
        tone_instruction = "Casual, chill, and direct."
        if relationship == "Boss":
            tone_instruction = "Formal, professional, and respectful. Use 'I would like to discuss' instead of emotional outbursts."
        elif relationship == "Teacher":
            tone_instruction = "Respectful, polite, and eager to learn."
        elif relationship == "Partner":
            tone_instruction = "Affectionate, gentle, open, and vulnerable."
        elif relationship == "Family":
            tone_instruction = "Warm, respectful, but personal."
            
        system_prompt = f"""You are an expert communication coach and emotional intelligence assistant.
Your goal is to help the user express themselves better, especially when they are emotional.
Target Recipient: {relationship}
Topic Tone: {tone_instruction}

Rewrite the user's draft message to be:
1. More polite and respectful.
2. Constructive and solution-oriented.
3. Empathetic and clear.
4. Keep the ORIGINAL INTENT but remove aggression, passive-aggressiveness, or despair.
5. EXTREMELY IMPORTANT: Make the Rewrite UNIQUE and tailored to the specific situation. Avoid generic phrases.

Output ONLY the rewritten message. Do not add quotes or explanations."""

        user_prompt = f"User Draft: '{text}'\nDetected Emotion: {emotion}\n\nRewritten Message:"
        
        try:
            completion = self.client.chat.completions.create(
                model="meta/llama-3.1-405b-instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            return completion.choices[0].message.content.strip('"').strip()
        except Exception as e:
            print(f"XeNit Rewrite Error: {e}")
            return None

    def get_emotional_support(self, query):
        """
        Generates a compassionate, supportive response for emotional search queries.
        Uses a specialized system prompt for empathy and resource provision.
        """
        if not self.client:
            return "I hear that you're going through something difficult. Please reach out to a professional or a trusted friend."

        system_prompt = """You are XeNit AI, an empathetic and supportive emotional assistant.
Your goal is to provide immediate, compassionate support to a user who is searching for something distressing.

=== RESPONSE FRAMEWORK ===

1. **Warm Acknowledgment** (1-2 sentences)
   - Validate their feelings without judgment.
   - Example: "I hear that you're going through a difficult time. It takes courage to reach out."

2. **Crisis Resources** (IF SEVERE DISTRESS DETECTED)
   - Display crisis hotlines prominently:
     * National Suicide Prevention Lifeline: 988 (US) / 112 (EU) / 9152987821 (India)
     * Crisis Text Line: Text HOME to 741741
   
3. **Immediate Support Options**
   - Suggest breathing exercises (e.g., Box Breathing).
   - Suggest calming music or nature sounds.
   - Suggest guided meditation.

4. **Helpful Content Categories**
   - Suggest searching for "coping strategies for [emotion]".
   - Suggest "uplifting stories" or "comforting videos".

5. **Empowering Next Steps**
   - Suggest concrete, small actions (drinking water, stepping outside).
   - Encourage professional help.

=== TONE GUIDELINES ===
- Warm, compassionate, non-clinical.
- Avoid toxic positivity ("just think positive!").
- Never minimize their feelings.
- Use "you" language to create connection.

=== BROWSER ACTIONS ===
You can use tags to help, BUT FOLLOW THESE RULES:
- [[OPEN: url]] (e.g., to a meditation site) -> OK to suggest.
- [[MUSIC: song]] -> 🚨 DO NOT use this unless the user EXPLICITLY asks for music.
- [[SEARCH: resource]] -> OK to suggest.

Be concise but meaningful. Focus on listening and talking. Do not overwhelm the user."""

        user_prompt = f"The user searched for: '{query}'. Provide emotional support and resources."

        try:
            print(f"XeNit Emotional Support Trigger: {query}")
            completion = self.client.chat.completions.create(
                model="meta/llama-3.1-405b-instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3, # Warm but consistent
                max_tokens=600
            )
            response = completion.choices[0].message.content
            
            # Process any actions (e.g. music)
            self._process_actions(response)
            
            return response
        except Exception as e:
            print(f"XeNit Support Error: {e}")
            return "I'm having trouble connecting, but please know you are not alone. Consider calling a local helpline if you need someone to talk to."

    def _process_actions(self, response_text):
        """
        Parses response for [[ACTION: param]] tags and executes them.
        """
        if not self.controller:
            return

        # Regex for tags like [[OPEN: google.com]]
        # We look for [[KEY: VALUE]]
        pattern = r"\[\[([A-Z]+):(.*?)\]\]" 
        matches = re.findall(pattern, response_text)
        
        for action, param in matches:
            param = param.strip()
            print(f"XeNit Agent Action: {action} -> {param}")
            
            if action == "OPEN":
                self.controller.open_url(param)
            elif action == "MUSIC":
                self.controller.play_music(param)
            elif action == "WHATSAPP":
                # Support "Name|Message" or "Phone|Message"
                target_phone = param
                msg = ""
                
                if "|" in param:
                    parts = param.split("|", 1)
                    target_candidate = parts[0].strip()
                    msg = parts[1].strip()
                    
                    # Try to resolve name to number
                    contact_num = self.memory.get_contact(target_candidate)
                    if contact_num:
                        target_phone = f"{contact_num}|{msg}"
                    else:
                        # Assume it is already a number or raw input
                        target_phone = f"{target_candidate}|{msg}"
                else:
                    # Maybe just a name? Resolve it if possible
                    contact_num = self.memory.get_contact(param)
                    if contact_num:
                        target_phone = contact_num

                self.controller.open_whatsapp(target_phone)
            elif action == "SEARCH":
                self.controller.open_url(f"google.com/search?q={param}")
            elif action == "AUTOFILL":
                self.controller.auto_fill(param)
            elif action == "CLICK":
                self.controller.click_element(param)
            elif action == "CLOSE_TABS":
                self.controller.close_specific_tabs(param)
            elif action == "SAVE_PROFILE":
                try:
                    import json
                    data = json.loads(param)
                    self.memory.update_profile(data)
                    print("XeNit Agent: Profile Updated")
                except Exception as e:
                    print(f"XeNit Agent: Failed to save profile - {e}")


    def analyze_page(self, html_content, url):
        """
        Proactive analysis of a page when loaded.
        """
        pass

    def check_safety(self, context):
        if not context: return "No page loaded."
        url = context.get('url', '')
        if "http:" in url and "https" not in url:
            return "⚠️ **Warning**: This site is using HTTP. Your connection is not secure."
        return "✅ This site looks standard. Connection is secure (HTTPS)."
