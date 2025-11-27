import streamlit as st
from pathlib import Path
from datetime import datetime
import base64
import os
import mimetypes

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="T-Six Ventures | Pitch Competition",
    page_icon="💡",
    layout="wide",
)

LOGO_PATH = Path("assets/t_six_logo.png")
BG_PATH = Path("assets/t_six_background.png")


# ---------------- HELPERS ----------------

def load_image_as_base64(path: Path) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def inject_global_css(bg_path: Path):
    css_bg = ""
    if bg_path.exists():
        encoded = load_image_as_base64(bg_path)
        css_bg = f"""
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        [data-testid="stHeader"] {{
            background: rgba(0, 0, 0, 0.85) !important;
        }}
        """

    css = f"""
    <style>
    {css_bg}

    /* ========= GLOBAL: make everything transparent by default ========= */
    * {{
        background-color: transparent !important;
        box-shadow: none !important;
    }}

    /* ========= TEXT ========= */
    html, body, [data-testid="stAppViewContainer"], [class*="block-container"] {{
        color: #ffffff !important;
    }}
    h1, h2, h3, h4, h5, h6, p, li, label, span {{
        color: #ffffff !important;
    }}

    /* ========= FORM ELEMENTS (inputs, textareas, selects) ========= */
    input, textarea, select {{
        background-color: transparent !important;
        color: #ffffff !important;
    }}

    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div,
    div[data-baseweb="select"] > div {{
        background-color: transparent !important;
        border-radius: 10px !important;
        border: 1px solid #f5c84288 !important;
    }}

    textarea, .stTextArea textarea {{
        background-color: transparent !important;
        border-radius: 10px !important;
        border: 1px solid #f5c84288 !important;
    }}

    /* ==== PLACEHOLDER COLOR (Short description + What makes your idea different?) ==== */
    textarea::placeholder,
    .stTextArea textarea::placeholder {{
        color: #e6e6e6 !important;   /* near white instead of dark grey */
    }}

    /* ========= SELECTBOX DROPDOWN ========= */

    div[data-baseweb="select"] > div {{
        background-color: transparent !important;
        color: #ffffff !important;
    }}

    div[data-baseweb="select"] span {{
        color: #ffffff !important;
    }}

    div[data-baseweb="select"] svg {{
        fill: #f5c842 !important;
    }}

    /* Dropdown menu container + options */
    div[data-baseweb="menu"],
    div[data-baseweb="menu"] * {{
        background-color: transparent !important;
        color: #ffffff !important;
    }}

    div[role="listbox"],
    div[role="listbox"] *,
    ul[role="listbox"],
    ul[role="listbox"] * {{
        background-color: transparent !important;
        color: #ffffff !important;
    }}

    div[role="option"],
    li[role="option"] {{
        background-color: transparent !important;
        color: #ffffff !important;
    }}

    div[role="option"]:hover,
    li[role="option"]:hover {{
        background-color: rgba(245, 200, 66, 0.18) !important;
        color: #ffffff !important;
    }}

    div[role="option"][aria-selected="true"],
    li[role="option"][aria-selected="true"] {{
        background-color: rgba(245, 200, 66, 0.25) !important;
        color: #ffffff !important;
    }}

    /* ========= FILE UPLOADER ========= */
    [data-testid="stFileUploaderDropzone"] {{
        background-color: transparent !important;
        border: 1px dashed #f5c84288 !important;
    }}
    [data-testid="stFileUploaderDropzone"] div {{
        background-color: transparent !important;
    }}

    /* ========= CHECKBOX & SLIDER ========= */

    /* Make the checkbox SQUARE white with a clear border */
    div[data-baseweb="checkbox"] label div:first-child,
    div[data-baseweb="checkbox"] label div:first-child > div,
    div[data-baseweb="checkbox"] label div:first-child > div > div {{
        background-color: #ffffff !important;      /* solid white box */
        border-radius: 4px !important;
        border: 2px solid #ffffff !important;      /* ✅ strong white border */
    }}

    /* Tick icon dark so it’s visible on white */
    div[data-baseweb="checkbox"] svg {{
        fill: #000000 !important;
    }}

    /* Keep slider transparent */
    div[data-baseweb="slider"] > div {{
        background-color: transparent !important;
    }}

    /* Focus outline */
    input:focus, textarea:focus, select:focus {{
        outline: none !important;
        border-color: #f5c842 !important;
    }}

    /* ========= BUTTONS ========= */
    .stButton > button {{
        background-color: transparent !important;
        color: #ffffff !important;
        border-radius: 999px;
        border: 1px solid #f5c842 !important;
        padding: 0.45rem 1.3rem;
        font-weight: 600;
    }}
    .stButton > button:hover {{
        background-color: rgba(245, 200, 66, 0.12) !important;
        border-color: #f5c842 !important;
    }}

    /* ========= MAIN APPLY CARD (dark glass) ========= */
    .tSix-card {{
        background: rgba(0, 0, 0, 0.75) !important;
        border-radius: 18px !important;
        padding: 1.8rem 2rem !important;
        border: 1px solid #f5c84233 !important;
    }}

    .st-expander, .st-expander > details, .st-expander summary {{
        background-color: transparent !important;
    }}

    [data-testid="stAlert"] > div {{
        border-radius: 8px !important;
        border: 1px solid #f5c84288 !important;
    }}

    a {{
        color: #f5c842 !important;
        text-decoration: none;
    }}
    a:hover {{
        text-decoration: underline;
    }}
    </style>
    """

    fa = """
    <link rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    """

    st.markdown(fa + css, unsafe_allow_html=True)




def send_application_email(form_data: dict, pitch_deck):
    """Send application to Mostafa by email (configure secrets.toml)."""
    import smtplib
    import ssl
    from email.message import EmailMessage

    try:
        email_user = st.secrets["email"]["user"]
        email_pass = st.secrets["email"]["password"]
        smtp_host = st.secrets["email"].get("host", "smtp.gmail.com")
        smtp_port = int(st.secrets["email"].get("port", 465))
    except Exception:
        # No secrets configured – just skip sending email
        st.warning(
            "Email credentials not configured in secrets.toml. "
            "Submission saved locally only."
        )
        return

    msg = EmailMessage()
    msg["Subject"] = f"New T-Six Ventures Application – {form_data.get('idea_title','')}"
    msg["From"] = email_user
    msg["To"] = "mostafa.walid@intercapcapital.com"

    body = f"""
New pitch submission for T-Six Ventures

Applicant:
  Name: {form_data.get('applicant_name','')}
  Email: {form_data.get('applicant_email','')}
  University: {form_data.get('university','')}

Team:
  Team / Startup name: {form_data.get('team_name','')}
  Team size: {form_data.get('team_size','')}
  Stage: {form_data.get('stage','')}

Idea:
  Title: {form_data.get('idea_title','')}
  Track: {form_data.get('track','')}
  Video link: {form_data.get('video_link','')}

Short description:
{form_data.get('short_desc','')}

What makes it different:
{form_data.get('diff','')}
"""
    msg.set_content(body)

    if pitch_deck is not None:
        mime_type, _ = mimetypes.guess_type(pitch_deck.name)
        if mime_type is None:
            maintype, subtype = "application", "octet-stream"
        else:
            maintype, subtype = mime_type.split("/", 1)

        msg.add_attachment(
            pitch_deck.getvalue(),
            maintype=maintype,
            subtype=subtype,
            filename=pitch_deck.name,
        )

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
            server.login(email_user, email_pass)
            server.send_message(msg)
        st.success("📧 Application email sent to T-Six Ventures.")
    except Exception as e:
        st.warning(f"Could not send email automatically: {e}")


# inject CSS
inject_global_css(BG_PATH)

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_login" not in st.session_state:
    st.session_state.show_login = False


# ---------------- HEADER / HERO ----------------

with st.container():
    col_logo, col_title, col_btn = st.columns([1, 3, 1])

    with col_logo:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), use_column_width="auto")
        else:
            st.markdown("### T-SIX VENTURES")

    with col_title:
        st.markdown(
            "<h1 style='color:white; margin-top:0.4rem;'>Turn your idea into impact.</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='color:#f5f5f5;font-size:1.05rem;'>"
            "A T-Six Ventures business pitch competition where bold student innovators "
            "shape the future of technology, business, and society."
            "</p>",
            unsafe_allow_html=True,
        )

    with col_btn:
        st.write("")
        st.write("")
        if st.button("🚀 Apply Now", use_container_width=True):
            st.session_state.show_login = True

st.markdown("---")

# ---------------- CONTENT SECTIONS ----------------

col_left, col_right = st.columns([1.6, 1.4])

with col_left:
    st.markdown("### How it works")
    st.markdown(
        """
- **Submit Your Pitch**  
  Share your idea in a short proposal (max **500 words**), or upload a **2-minute video**.
- **Get Shortlisted**  
  Selected teams advance to the next stage and refine their ideas with feedback from mentors.
- **Pitch to the CEO**  
  Shortlisted founders pitch directly to the **T-Six Ventures leadership** and investment team.
- **Win Funding**  
  The top ideas receive **seed investment** and **incubation support** from T-Six Ventures.
        """
    )

    st.markdown("### Who can participate")
    st.markdown(
        """
- Open to **all students registered on Excelerate**.  
- **Solo founders** or **teams up to 4 members**.  
- Ideas from **any industry or sector** are welcome: technology, AI, fintech, health, education, social impact, design, and more.
        """
    )

    st.markdown("### Why participate")
    st.markdown(
        """
- Get **expert feedback** from investors and operators.  
- Pitch to **real decision-makers** at T-Six Ventures.  
- Access **funding, mentorship, and a venture-building network** to help your idea grow.
        """
    )

with col_right:
    st.markdown("### T-Six Ventures")
    st.markdown(
        """
- 🌐 **Website:** [www.t-sixventures.com](https://www.t-sixventures.com/)  
- 📍 **Location:** [Google Maps](https://maps.app.goo.gl/nEB8dYkqFAq1rHBY7)  
- 📞 **Phone:** 01004921554  
        """
    )

    st.markdown("**Follow us**")
    SOCIAL_HTML = """
    <div style='display:flex; gap:1.2rem; font-size:1.8rem; margin-top:0.4rem;'>
      <a href='https://www.linkedin.com/company/t-six-ventures' target='_blank'
         aria-label='LinkedIn'>
         <i class="fa-brands fa-linkedin"></i>
      </a>
      <a href='https://www.facebook.com/share/17ixkPUD49' target='_blank'
         aria-label='Facebook'>
         <i class="fa-brands fa-facebook"></i>
      </a>
      <a href='https://www.instagram.com/t.sixventures/' target='_blank'
         aria-label='Instagram'>
         <i class="fa-brands fa-instagram"></i>
      </a>
    </div>
    """
    st.markdown(SOCIAL_HTML, unsafe_allow_html=True)

st.markdown("---")


# ---------------- LOGIN / APPLY ----------------

def login_block():
    st.markdown("## Apply to T-Six Ventures Pitch Competition")

    if not st.session_state.logged_in:
        with st.expander("Sign in to start your application", expanded=True):
            with st.form("login_form", clear_on_submit=False):
                name = st.text_input("Full name")
                email = st.text_input("Email")
                university = st.text_input("University / Institution")

                submitted = st.form_submit_button("Sign In")
                if submitted:
                    if not name or not email:
                        st.error("Please fill in at least your name and email.")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.applicant_name = name
                        st.session_state.applicant_email = email
                        st.session_state.university = university
                        st.success(
                            f"Welcome, {name}! Scroll down to complete your application."
                        )
    else:
        st.success(
            f"Signed in as {st.session_state.applicant_name} "
            f"({st.session_state.applicant_email})"
        )


def application_form():
    st.markdown("### Pitch Submission Form")

    os.makedirs("submissions", exist_ok=True)

    with st.form("application_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            team_name = st.text_input("Team / Startup name")
            idea_title = st.text_input("Idea title")
            track = st.selectbox(
                "Main track",
                [
                    "AI & Deep Tech",
                    "Fintech",
                    "HealthTech",
                    "EdTech",
                    "SaaS / B2B",
                    "Consumer / Marketplace",
                    "Social Impact",
                    "Other",
                ],
            )
        with col2:
            team_size = st.slider("Team size", 1, 4, 1)
            stage = st.selectbox(
                "Stage of your idea",
                ["Idea only", "Prototype / MVP", "Early users", "Revenue-generating"],
            )
            video_link = st.text_input("Optional pitch video link (YouTube, Loom, etc.)")

        short_desc = st.text_area(
            "Short description (max ~500 words)",
            height=180,
            placeholder="What problem are you solving, and what is your solution?",
        )

        diff = st.text_area(
            "What makes your idea different?",
            height=120,
            placeholder="Tell us about your edge: technology, model, team, or insight.",
        )

        pitch_deck = st.file_uploader(
            "Pitch deck (PDF / PPT / PPTX)",
            type=["pdf", "ppt", "pptx"],
        )

        agree = st.checkbox(
            "I confirm that the information provided is accurate and that I am "
            "authorized to submit on behalf of my team."
        )

        submitted = st.form_submit_button("Submit Application 🚀")

        if submitted:
            if not idea_title or not short_desc or not pitch_deck:
                st.error("Please fill in all required fields and upload your pitch deck.")
            elif not agree:
                st.error("You must confirm the accuracy of your information before submitting.")
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_name = pitch_deck.name.replace(" ", "_")
                out_path = Path("submissions") / f"{timestamp}_{safe_name}"
                with open(out_path, "wb") as f:
                    f.write(pitch_deck.getbuffer())

                log_line = (
                    f"{timestamp},"
                    f"{st.session_state.get('applicant_name','')},"
                    f"{st.session_state.get('applicant_email','')},"
                    f"{team_name},{idea_title},{track},{stage},{team_size},"
                    f"\"{video_link}\",\"{short_desc[:150].replace(',', ' ')}...\"\n"
                )
                with open("submissions/applications_log.csv", "a", encoding="utf-8") as log:
                    log.write(log_line)

                form_data = {
                    "applicant_name": st.session_state.get("applicant_name", ""),
                    "applicant_email": st.session_state.get("applicant_email", ""),
                    "university": st.session_state.get("university", ""),
                    "team_name": team_name,
                    "idea_title": idea_title,
                    "track": track,
                    "stage": stage,
                    "team_size": team_size,
                    "video_link": video_link,
                    "short_desc": short_desc,
                    "diff": diff,
                }

                send_application_email(form_data, pitch_deck)

                st.success(
                    "✅ Your application has been submitted! "
                    "The T-Six Ventures team will review your pitch and contact you by email."
                )


if st.session_state.show_login or st.session_state.logged_in:
    with st.container():
        st.markdown('<div class="tSix-card">', unsafe_allow_html=True)
        login_block()
        if st.session_state.logged_in:
            application_form()
        st.markdown("</div>", unsafe_allow_html=True)
