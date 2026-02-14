"""
XeNit AI — Medical Safety Layer
Detects serious health symptom searches and classifies severity.
Only triggers warnings for MEDIUM and HIGH severity symptoms.
"""


# ── Symptom Database with Severity Levels ────────────────────────────────────
# Severity: "high" = go to doctor NOW, "medium" = consider seeing a doctor
# We intentionally skip "low" severity — no warning for minor things like colds

SYMPTOM_DATABASE = {
    # ── HIGH SEVERITY (Emergency / Life-threatening) ──────────────────────
    # Heart
    "chest pain": "high",
    "heart attack": "high",
    "heart pain": "high",
    "chest tightness": "high",
    "irregular heartbeat": "high",
    "heart palpitations": "high",
    "cardiac arrest": "high",
    
    # Brain / Stroke
    "stroke symptoms": "high",
    "sudden numbness": "high",
    "sudden confusion": "high",
    "difficulty speaking": "high",
    "severe headache": "high",
    "loss of consciousness": "high",
    "fainting": "high",
    "seizure": "high",
    "convulsions": "high",
    
    # Breathing
    "difficulty breathing": "high",
    "shortness of breath": "high",
    "can't breathe": "high",
    "breathing problem": "high",
    "choking": "high",
    
    # Bleeding / Trauma
    "severe bleeding": "high",
    "blood in stool": "high",
    "blood in urine": "high",
    "coughing blood": "high",
    "vomiting blood": "high",
    "internal bleeding": "high",
    "head injury": "high",
    
    # Allergic / Poisoning
    "allergic reaction": "high",
    "anaphylaxis": "high",
    "poisoning": "high",
    "drug overdose": "high",
    "overdose": "high",
    
    # Severe Pain
    "appendicitis": "high",
    "severe abdominal pain": "high",
    "kidney stone": "high",
    
    # Other Critical
    "suicidal thoughts": "high",
    "suicide": "high",
    "paralysis": "high",
    "tumor": "high",
    "cancer symptoms": "high",
    "blood clot": "high",
    "deep vein thrombosis": "high",
    "pulmonary embolism": "high",
    "meningitis": "high",

    # ── MEDIUM SEVERITY (Should see a doctor soon) ────────────────────────
    # Persistent Pain
    "persistent headache": "medium",
    "chronic pain": "medium",
    "back pain": "medium",
    "joint pain": "medium",
    "abdominal pain": "medium",
    "stomach pain": "medium",
    
    # Infection Signs
    "high fever": "medium",
    "persistent fever": "medium",
    "fever won't go down": "medium",
    "infected wound": "medium",
    "swollen lymph nodes": "medium",
    
    # Mental Health
    "depression symptoms": "medium",
    "severe anxiety": "medium",
    "panic attack": "medium",
    "mental health crisis": "medium",
    
    # Digestive
    "persistent vomiting": "medium",
    "blood in vomit": "high",
    "severe diarrhea": "medium",
    "difficulty swallowing": "medium",
    
    # Skin / Lumps
    "unusual lump": "medium",
    "sudden weight loss": "medium",
    "skin rash spreading": "medium",
    "mole changing": "medium",
    
    # Eyes / Ears
    "sudden vision loss": "high",
    "blurred vision": "medium",
    "eye pain": "medium",
    "sudden hearing loss": "medium",
    
    # Diabetes / Sugar
    "diabetic emergency": "high",
    "low blood sugar": "medium",
    "high blood sugar": "medium",
    
    # Women's Health
    "pregnancy bleeding": "high",
    "severe cramps": "medium",
    
    # General
    "persistent cough": "medium",
    "cough won't stop": "medium",
    "extreme fatigue": "medium",
    "unexplained bruising": "medium",
    "chest pressure": "high",
    "numbness in face": "high",
    "numbness in arm": "high",
}

# ── Warning Messages by Severity ────────────────────────────────────────────

WARNING_MESSAGES = {
    "high": {
        "title": "🚨 Health Safety Warning",
        "message": "This symptom may be serious or life-threatening. Please consult a doctor or visit an emergency room immediately.",
        "action": "Call emergency services or visit the nearest hospital.",
        "color": "#ff2a6d",
        "bg": "#3b1019",
    },
    "medium": {
        "title": "⚠️ Health Advisory",
        "message": "This symptom may require professional medical consultation. A doctor can provide proper diagnosis and treatment.",
        "action": "Consider scheduling a doctor's appointment soon.",
        "color": "#f59e0b",
        "bg": "#3b2f10",
    },
}


def check_health_search(search_text: str):
    """
    Check if a search query contains serious health symptoms.
    Returns (severity, symptom, warning_info) or None if no warning needed.
    Only triggers for MEDIUM and HIGH severity — not for minor symptoms.
    """
    lower = search_text.lower()
    
    # Skip very short queries
    if len(lower) < 4:
        return None
    
    # Check for matches (longest match first for accuracy)
    best_match = None
    best_length = 0
    
    for symptom, severity in SYMPTOM_DATABASE.items():
        if symptom in lower and len(symptom) > best_length:
            best_match = symptom
            best_length = len(symptom)
    
    if best_match:
        severity = SYMPTOM_DATABASE[best_match]
        warning = WARNING_MESSAGES[severity]
        return {
            "severity": severity,
            "symptom": best_match,
            "title": warning["title"],
            "message": warning["message"],
            "action": warning["action"],
            "color": warning["color"],
            "bg": warning["bg"],
        }
    
    return None


def get_safety_banner_js(warning_info: dict) -> str:
    """
    Returns JavaScript code that injects a health safety warning banner
    at the top of the page.
    """
    title = warning_info["title"]
    message = warning_info["message"]
    action = warning_info["action"]
    color = warning_info["color"]
    bg = warning_info["bg"]
    severity = warning_info["severity"]
    
    # Pulsing border for HIGH severity
    pulse_css = ""
    if severity == "high":
        pulse_css = """
            @keyframes xenitPulse {
                0%, 100% { border-color: """ + color + """; }
                50% { border-color: transparent; }
            }
            #xenit-health-warning { animation: xenitPulse 2s ease-in-out infinite; }
        """
    
    js = f"""
    (function() {{
        // Don't inject twice
        if (document.getElementById('xenit-health-warning')) return;
        
        const style = document.createElement('style');
        style.textContent = `
            #xenit-health-warning {{
                position: fixed;
                top: 10px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 999999;
                background: {bg};
                border: 2px solid {color};
                border-radius: 12px;
                padding: 16px 24px;
                max-width: 600px;
                width: 90%;
                font-family: 'Segoe UI', sans-serif;
                box-shadow: 0 8px 32px rgba(0,0,0,0.6);
                backdrop-filter: blur(10px);
            }}
            #xenit-health-warning .xenit-hw-title {{
                color: {color};
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 6px;
            }}
            #xenit-health-warning .xenit-hw-msg {{
                color: #e0e0e0;
                font-size: 13px;
                line-height: 1.5;
                margin-bottom: 8px;
            }}
            #xenit-health-warning .xenit-hw-action {{
                color: {color};
                font-size: 12px;
                font-weight: 600;
            }}
            #xenit-health-warning .xenit-hw-close {{
                position: absolute;
                top: 8px;
                right: 12px;
                background: none;
                border: none;
                color: #888;
                font-size: 18px;
                cursor: pointer;
            }}
            #xenit-health-warning .xenit-hw-close:hover {{
                color: #fff;
            }}
            #xenit-health-warning .xenit-hw-badge {{
                display: inline-block;
                background: {color};
                color: #000;
                font-size: 10px;
                font-weight: bold;
                padding: 2px 8px;
                border-radius: 4px;
                margin-left: 8px;
                text-transform: uppercase;
            }}
            {pulse_css}
        `;
        document.head.appendChild(style);
        
        const banner = document.createElement('div');
        banner.id = 'xenit-health-warning';
        banner.innerHTML = `
            <button class="xenit-hw-close" onclick="this.parentElement.remove()">✕</button>
            <div class="xenit-hw-title">{title}<span class="xenit-hw-badge">{severity}</span></div>
            <div class="xenit-hw-msg">{message}</div>
            <div class="xenit-hw-action">👨‍⚕️ {action}</div>
        `;
        document.body.appendChild(banner);
        
        // Auto-dismiss after 15 seconds
        setTimeout(() => {{
            const el = document.getElementById('xenit-health-warning');
            if (el) el.style.opacity = '0';
            setTimeout(() => {{
                const el2 = document.getElementById('xenit-health-warning');
                if (el2) el2.remove();
            }}, 500);
        }}, 15000);
    }})();
    """
    return js


# ══════════════════════════════════════════════════════════════════════════════
# TRUSTED MEDICAL SITE DETECTION
# ══════════════════════════════════════════════════════════════════════════════

TRUSTED_MEDICAL_DOMAINS = {
    # Government / Official
    "who.int",
    "cdc.gov",
    "nih.gov",
    "medlineplus.gov",
    "nhs.uk",
    "fda.gov",
    "health.gov",
    "pubmed.ncbi.nlm.nih.gov",

    # Major Medical Institutions
    "mayoclinic.org",
    "clevelandclinic.org",
    "hopkinsmedicine.org",
    "health.harvard.edu",
    "stanfordhealthcare.org",
    "ucsfhealth.org",
    "uclahealth.org",
    "mountsinai.org",

    # Health Organizations
    "heart.org",
    "cancer.org",
    "diabetes.org",
    "lung.org",
    "familydoctor.org",
    "healthychildren.org",
    "plannedparenthood.org",

    # Medical Journals / Research
    "cochrane.org",
    "thelancet.com",
    "nejm.org",
    "jamanetwork.com",
    "bmj.com",
    "nature.com",

    # Trusted Health Info Sites
    "merckmanuals.com",
    "uptodate.com",
    "webmd.com",
    "healthline.com",
    "drugs.com",
    "verywellhealth.com",
    "medicalnewstoday.com",
    "patient.info",
    "medscape.com",
    "emedicinehealth.com",
    "kidshealth.org",
}

# Keywords that suggest a page is health/medical related
HEALTH_URL_KEYWORDS = [
    "health", "medical", "medicine", "symptom", "disease", "treatment",
    "cure", "remedy", "diagnosis", "doctor", "hospital", "clinic",
    "pain", "fever", "infection", "cancer", "diabetes", "heart",
    "blood", "surgery", "therapy", "drug", "pill", "vitamin",
    "wellness", "mental-health", "anxiety", "depression", "stroke",
    "allergy", "asthma", "cholesterol", "pregnancy", "nutrition",
    "diet", "fitness", "pharma", "patient", "disorder", "syndrome",
    "chronic", "acute", "emergency", "first-aid",
]


def is_health_related_url(url: str) -> bool:
    """Check if a URL appears to be health/medical content."""
    lower = url.lower()
    # Check path and query for health keywords
    return any(kw in lower for kw in HEALTH_URL_KEYWORDS)


def is_trusted_medical_domain(url: str) -> bool:
    """Check if the domain of a URL is in our trusted list."""
    lower = url.lower()
    for domain in TRUSTED_MEDICAL_DOMAINS:
        if domain in lower:
            return True
    return False


def check_untrusted_medical_site(url: str):
    """
    Returns warning info if the URL is health-related but NOT from a trusted source.
    Returns None if the site is trusted, or the page isn't health-related.
    """
    # Skip search engine results pages (they contain health keywords in the query)
    skip_domains = ["google.com", "bing.com", "duckduckgo.com", "yahoo.com",
                    "youtube.com", "xenit://"]
    lower_url = url.lower()
    if any(sd in lower_url for sd in skip_domains):
        return None

    # Only check if it looks like a health page
    if not is_health_related_url(url):
        return None

    # If it IS health-related, check trust
    if is_trusted_medical_domain(url):
        return None  # Trusted — no warning

    # Untrusted health site — show warning
    return {
        "title": "⚠️ Unverified Medical Source",
        "message": "This website is not in our list of verified medical sources. "
                   "Information here may not be medically verified. "
                   "Cross-check with trusted sources like WHO, CDC, or Mayo Clinic.",
        "color": "#f59e0b",
        "bg": "#2d2510",
    }


def get_untrusted_site_banner_js(warning_info: dict) -> str:
    """
    Returns JS that injects a subtle bottom-corner banner warning about
    untrusted medical sources. Different from the search warning banner.
    """
    title = warning_info["title"]
    message = warning_info["message"]
    color = warning_info["color"]
    bg = warning_info["bg"]

    js = f"""
    (function() {{
        if (document.getElementById('xenit-trust-overlay')) return;

        const style = document.createElement('style');
        style.textContent = `
            #xenit-trust-overlay {{
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                z-index: 999998;
                background: rgba(0, 0, 0, 0.7);
                display: flex;
                align-items: center;
                justify-content: center;
                backdrop-filter: blur(4px);
            }}
            #xenit-trust-warning {{
                background: {bg};
                border: 2px solid {color};
                border-radius: 16px;
                padding: 28px 32px;
                max-width: 500px;
                width: 90%;
                font-family: 'Segoe UI', sans-serif;
                box-shadow: 0 8px 40px rgba(0,0,0,0.8);
                text-align: center;
            }}
            #xenit-trust-warning .xtw-icon {{
                font-size: 40px;
                margin-bottom: 10px;
            }}
            #xenit-trust-warning .xtw-title {{
                color: {color};
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            #xenit-trust-warning .xtw-msg {{
                color: #ddd;
                font-size: 14px;
                line-height: 1.6;
                margin-bottom: 20px;
            }}
            #xenit-trust-warning .xtw-btn {{
                background: {color};
                color: #000;
                border: none;
                border-radius: 8px;
                padding: 10px 28px;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
                font-family: 'Segoe UI', sans-serif;
                transition: opacity 0.2s;
            }}
            #xenit-trust-warning .xtw-btn:hover {{
                opacity: 0.85;
            }}
        `;
        document.head.appendChild(style);

        const overlay = document.createElement('div');
        overlay.id = 'xenit-trust-overlay';
        overlay.innerHTML = `
            <div id="xenit-trust-warning">
                <div class="xtw-icon">⚠️</div>
                <div class="xtw-title">{title}</div>
                <div class="xtw-msg">{message}</div>
                <button class="xtw-btn" onclick="document.getElementById('xenit-trust-overlay').remove()">✓ Continue Reading</button>
            </div>
        `;
        document.body.appendChild(overlay);
    }})();
    """
    return js
