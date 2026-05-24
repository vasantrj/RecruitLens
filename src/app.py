import streamlit as st
import pandas as pd
import joblib
import time
import sys
import os
 
sys.path.insert(0, os.path.dirname(__file__))
 
from preprocess import preprocess_dataframe, clean_text
from matcher import match_resumes
from visualize import score_bar_chart, category_pie, generate_wordcloud_img
from pdf_reader import extract_text_from_pdf
from skills import extract_skills
from llm_feedback import get_feedback
from resume_parser import parse_resume
from report import generate_report

 
st.set_page_config(
    page_title="RecruitLens · AI Screening",
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="collapsed"
)
 
# Load external CSS
# with open("src/styles.css") as css_file:
#     st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
 
# Load CSS only once
@st.cache_data

def load_css():
    with open("src/styles.css") as css_file:
        return css_file.read()

st.markdown(
    f"<style>{load_css()}</style>",
    unsafe_allow_html=True
)

@st.cache_resource
def load_model_files():
    model = joblib.load("src/model.pkl")
    vectorizer = joblib.load("src/vectorizer.pkl")
    return model, vectorizer
 
model, vectorizer = load_model_files()
 
# @st.cache_data
# def load_dataset(path):
#     df = pd.read_csv(path)
#     df = preprocess_dataframe(df)
#     return df

@st.cache_data(show_spinner="Loading dataset...")
def load_dataset(path):

    df = pd.read_csv(
        path,
        low_memory=False
    )

    df = preprocess_dataframe(df)

    # Reduce memory usage
    for col in df.select_dtypes(include="object"):
        df[col] = df[col].astype(str)

    return df

# Header
st.markdown("""
<div style="padding: 56px 0 40px; border-bottom: 1px solid var(--rule);">
  <div style="display:flex; align-items:center; gap:16px; margin-bottom:24px;">
    <svg width="48" height="48" viewBox="0 0 48 48" class="animated-logo">
      <circle cx="24" cy="24" r="20" fill="none" stroke="#16A34A" stroke-width="2" opacity="0.3"/>
      <circle cx="24" cy="24" r="14" fill="none" stroke="#16A34A" stroke-width="2" opacity="0.6"/>
      <circle cx="24" cy="24" r="8" fill="none" stroke="#16A34A" stroke-width="2.5"/>
      <circle cx="24" cy="24" r="3" fill="#16A34A"/>
    </svg>
    <div style="display:flex; align-items:center; gap:12px;">
      <span style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem;
        letter-spacing:0.22em; text-transform:uppercase; color:var(--ink-mute);">
        Resume Intelligence
      </span>
      <div style="flex:1; height:1px; background:var(--rule);"></div>
      <span style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem;
        letter-spacing:0.15em; color:var(--ink-mute);">v 2.0</span>
    </div>
  </div>
  <div style="display:flex; align-items:flex-end; gap:0; line-height:1;">
    <b><h1 style="font-family:'Cormorant Garamond',serif !important;
      font-size:4.8rem; font-weight:300; color:var(--ink) !important;
      letter-spacing:-0.03em; margin:0; padding:0;">Recruit</h1></b>
    <h1 style="font-family:'Cormorant Garamond',serif !important;
      font-size:4.8rem; font-weight:700; color:var(--green) !important;
      letter-spacing:-0.03em; margin:0; padding:0;">Lens</h1>
    <span style="font-family:'IBM Plex Mono',monospace; font-size:0.75rem;
      color:var(--ink-mute); margin-left:20px; margin-bottom:10px; letter-spacing:0.08em;">
      AI · Precision Hiring
    </span>
  </div>
  <p style="font-family:'Cormorant Garamond',serif; font-size:1.15rem;
    font-weight:300; font-style:italic; color:var(--ink-soft); margin-top:10px;
    letter-spacing:0.01em;">
    Match, screen &amp; evaluate candidates with machine intelligence.
  </p>
</div>
""", unsafe_allow_html=True)
 
st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["◎  Bulk Screening", "◈  Resume Analyzer", "◇  How It Works"])
 
with tab1:
    st.markdown("""
    <div style="font-family:'Cormorant Garamond',serif; font-size:1.5rem;
      font-weight:600; color:var(--ink); margin-bottom:4px;">Configuration</div>
    <div style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem;
      letter-spacing:0.12em; text-transform:uppercase; color:var(--ink-mute);
      margin-bottom:28px; padding-bottom:20px;
      border-bottom:1px solid var(--rule);">Data Source &amp; Settings</div>
    """, unsafe_allow_html=True)
    
    csv_path = st.text_input("Resume CSV Path", value="data/Resume.csv")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    
    if st.button("↻  Load Dataset"):
        try:
            st.session_state["df"] = load_dataset(csv_path)
            st.success(f"✓  {len(st.session_state['df'])} resumes loaded")
        except Exception as e:
            st.error(f"Error loading: {e}")
    
    st.markdown("""
    <div style="margin-top:48px; padding-top:20px; border-top:1px solid var(--rule);">
      <div style="font-family:'IBM Plex Mono',monospace; font-size:0.6rem;
        letter-spacing:0.1em; text-transform:uppercase; color:var(--ink-mute);
        line-height:2.2;">
        Stack<br>
        <span style="color:var(--ink-soft);">Sentence Transformers · Cosine Similarity</span><br>
        <span style="color:var(--ink-soft);">spaCy NER · Gemini LLM · sklearn</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    
    if "df" not in st.session_state:
        st.markdown("""
        <div style="display:flex; flex-direction:column; align-items:center;
          justify-content:center; padding:80px 40px; text-align:center;
          border:1.5px dashed var(--rule); border-radius:8px; background:var(--surface);
          margin:24px 0;">
          <div style="width:48px; height:48px; border:1.5px solid var(--rule);
            border-radius:50%; display:flex; align-items:center; justify-content:center;
            margin-bottom:20px; font-size:1.4rem;">◎</div>
          <div style="font-family:'Cormorant Garamond',serif; font-size:1.8rem;
            font-weight:600; color:var(--ink); margin-bottom:8px;">No Dataset Loaded</div>
          <div style="font-family:'IBM Plex Mono',monospace; font-size:0.75rem;
            color:var(--ink-mute); letter-spacing:0.06em; max-width:340px; line-height:1.7;">
            Load your resume CSV above to start screening candidates.
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        df = st.session_state["df"]
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:32px;
          padding:12px 20px; background:var(--green-bg);
          border-left:3px solid var(--green); border-radius:0 6px 6px 0;">
          <span style="font-family:'IBM Plex Mono',monospace; font-size:0.72rem;
            letter-spacing:0.1em; color:var(--green);">
            ✓ &nbsp; Dataset loaded — <strong>{len(df):,}</strong> resumes
          </span>
        </div>
        """, unsafe_allow_html=True)
 
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Resumes", f"{len(df):,}")
        c2.metric("Job Categories", df["Category"].nunique())
        c3.metric("Data Fields", len(df.columns))
        
        col_name = "clean_resume" if "clean_resume" in df.columns else "Resume_str"
        c4.metric(
            "Avg. Text Length",
            f"{int(df[col_name].astype(str).str.len().mean()):,}"
            )
         
        st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family:'Cormorant Garamond',serif; font-size:1.5rem;
          font-weight:600; color:var(--ink); margin-bottom:4px;">Category Distribution</div>
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.7rem;
          color:var(--ink-mute); letter-spacing:0.08em; margin-bottom:16px;">
          Resume pool breakdown by job function
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(category_pie(df), use_container_width=True)
 
        st.divider()
 
        st.markdown("""
        <div style="font-family:'Cormorant Garamond',serif; font-size:1.5rem;
          font-weight:600; color:var(--ink); margin-bottom:4px;">Screening Parameters</div>
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.7rem;
          color:var(--ink-mute); letter-spacing:0.08em; margin-bottom:20px;">
          Define the role to match candidates against
        </div>
        """, unsafe_allow_html=True)
 
        jd = st.text_area("Job Description", height=220, key="bulk_jd",
            placeholder="Paste the full job description here…")
 
        col_a, col_b = st.columns([2, 1])
        with col_a:
            top_n = st.slider("Top N Candidates", min_value=3, max_value=30, value=10)
        with col_b:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            run = st.button("◎  Run Matching Analysis")
 
        if run:
            if not jd.strip():
                st.warning("Please paste a job description before running.")
            else:
                with st.spinner("Analysing candidate pool…"):
                    start_time = time.time()
                    results = match_resumes(jd,df,top_n)
                    end_time = time.time()
 
                st.markdown(f"""
                <div style="display:grid; grid-template-columns:1fr 1fr;
                  gap:16px; margin:32px 0 24px; padding:28px 32px;
                  background:var(--surface); border:1px solid var(--rule); border-radius:8px;
                  box-shadow:var(--shadow);">
                  <div>
                    <div style="font-family:'IBM Plex Mono',monospace; font-size:0.62rem;
                      letter-spacing:0.18em; text-transform:uppercase; color:var(--ink-mute);
                      margin-bottom:4px;">Top Candidates Found</div>
                    <div style="font-family:'Cormorant Garamond',serif; font-size:3rem;
                      font-weight:600; color:var(--ink); line-height:1;">{len(results)}</div>
                  </div>
                  <div>
                    <div style="font-family:'IBM Plex Mono',monospace; font-size:0.62rem;
                      letter-spacing:0.18em; text-transform:uppercase; color:var(--ink-mute);
                      margin-bottom:4px;">Highest Match Score</div>
                    <div style="font-family:'Cormorant Garamond',serif; font-size:3rem;
                      font-weight:600; color:var(--green); line-height:1;">
                      {results['match_score'].max():.1f}%
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
 
                st.markdown("""
                <div style="font-family:'Cormorant Garamond',serif; font-size:1.5rem;
                  font-weight:600; color:var(--ink); margin-bottom:16px;">
                  Match Score Rankings
                </div>
                """, unsafe_allow_html=True)
                st.plotly_chart(score_bar_chart(results), use_container_width=True)
                st.success(
                    f"Analysis completed in {round(end_time - start_time, 2)} seconds"
                )
 
                col_t, col_w = st.columns([1, 1], gap="large")
 
                with col_t:
                    st.markdown("""
                    <div style="font-family:'Cormorant Garamond',serif; font-size:1.4rem;
                      font-weight:600; color:var(--ink); margin-bottom:12px;">
                      Candidate Shortlist
                    </div>
                    """, unsafe_allow_html=True)
                    display_df = results[["ID", "Category", "match_score"]].copy()
                    display_df.columns = ["ID", "Category", "Score (%)"]
                    display_df["Score (%)"] = display_df["Score (%)"].round(2)
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
 
                    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                    csv_out = results[["ID", "Category", "match_score"]].to_csv(index=False)
                    st.download_button("⬇  Export Shortlist as CSV", csv_out, "resume_matches.csv", "text/csv")
 
                with col_w:
                    st.markdown("""
                    <div style="font-family:'Cormorant Garamond',serif; font-size:1.4rem;
                      font-weight:600; color:var(--ink); margin-bottom:12px;">
                      Keyword Landscape
                    </div>
                    """, unsafe_allow_html=True)
                    combined_text = " ".join(results["clean_resume"].tolist())
                    st.plotly_chart(generate_wordcloud_img(combined_text), use_container_width=True)
 
with tab2:
    st.markdown("""
    <div style="font-family:'Cormorant Garamond',serif; font-size:1.5rem;
      font-weight:600; color:var(--ink); margin-bottom:6px;">Resume Deep Analysis</div>
    <div style="font-family:'IBM Plex Mono',monospace; font-size:0.7rem;
      color:var(--ink-mute); letter-spacing:0.06em; margin-bottom:32px;">
      Upload a single resume PDF for full candidate evaluation
    </div>
    """, unsafe_allow_html=True)
 
    col_up, col_jd = st.columns([1, 1], gap="large")
 
    with col_up:
        st.markdown("""
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem;
          letter-spacing:0.15em; text-transform:uppercase; color:var(--ink-soft);
          margin-bottom:8px;">01 · Upload Resume PDF</div>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Resume PDF", type=["pdf"], label_visibility="collapsed",
            help="PDF format only. Text-based PDFs recommended.")
 
        if not uploaded_file:
            st.markdown("""
            <div style="font-family:'IBM Plex Mono',monospace; font-size:0.7rem;
              color:var(--ink-mute); margin-top:8px; line-height:1.7;">
              PDF format only.<br>Text-based PDFs yield best results.
            </div>
            """, unsafe_allow_html=True)
 
    with col_jd:
        st.markdown("""
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem;
          letter-spacing:0.15em; text-transform:uppercase; color:var(--ink-soft);
          margin-bottom:8px;">02 · Job Description <em style="text-transform:none; font-style:italic;">(optional for AI Recruiter Assessment (CTRL+ENTER))</em></div>
        """, unsafe_allow_html=True)
        jd_single = st.text_area("JD", height=168, key="single_jd", label_visibility="collapsed",
            placeholder="Paste the job description for match scoring…")
 
    if uploaded_file:
        resume_text = extract_text_from_pdf(uploaded_file)
        # st.write(resume_text[:3000])
 
        if not resume_text.strip():
            st.error("Could not extract text from this PDF. Ensure it is not scanned/image-only.")
        else:
            cleaned_resume = clean_text(resume_text)
            resume_vec = vectorizer.transform([cleaned_resume])
            prediction = model.predict(resume_vec)[0]
 
            st.divider()
 
            st.markdown("""
            <div style="font-family:'IBM Plex Mono',monospace; font-size:0.62rem;
              letter-spacing:0.2em; text-transform:uppercase; color:var(--ink-mute);
              margin-bottom:16px;">03 · Candidate Profile</div>
            """, unsafe_allow_html=True)
 
            parsed = parse_resume(resume_text)
 
            col_prof, col_cat = st.columns([3, 2], gap="large")
 
            with col_prof:
                st.markdown(f"""
                <div style="background:var(--surface); border:1px solid var(--rule);
                  border-radius:8px; padding:28px 32px; box-shadow:var(--shadow);">
                  <div style="font-family:'Cormorant Garamond',serif; font-size:1.9rem;
                    font-weight:600; color:var(--ink); margin-bottom:20px; line-height:1.1;">
                    {parsed['name'] or 'Candidate'}
                  </div>
                  <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
                    <div>
                      <div style="font-family:'IBM Plex Mono',monospace; font-size:0.6rem;
                        letter-spacing:0.15em; text-transform:uppercase; color:var(--ink-mute);
                        margin-bottom:3px;">Email</div>
                      <div style="font-family:'IBM Plex Mono',monospace; font-size:0.78rem;
                        color:var(--ink);">{parsed['email'] or '—'}</div>
                    </div>
                    <div>
                      <div style="font-family:'IBM Plex Mono',monospace; font-size:0.6rem;
                        letter-spacing:0.15em; text-transform:uppercase; color:var(--ink-mute);
                        margin-bottom:3px;">Phone</div>
                      <div style="font-family:'IBM Plex Mono',monospace; font-size:0.78rem;
                        color:var(--ink);">{parsed['phone'] or '—'}</div>
                    </div>
                    <div style="grid-column:1/-1;">
                      <div style="font-family:'IBM Plex Mono',monospace; font-size:0.6rem;
                        letter-spacing:0.15em; text-transform:uppercase; color:var(--ink-mute);
                        margin-bottom:3px;">Experience</div>
                      <div style="font-family:'IBM Plex Mono',monospace; font-size:0.78rem;
                        color:var(--ink);">{parsed['experience'] or '—'}</div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
 
            with col_cat:
                st.markdown(f"""
                <div style="background:linear-gradient(135deg, var(--green) 0%, var(--green-lt) 100%);
                  border-radius:8px; padding:28px 32px; height:100%;
                  display:flex; flex-direction:column; justify-content:center;
                  box-shadow:0 4px 16px rgba(22,163,74,0.2);">
                  <div style="font-family:'IBM Plex Mono',monospace; font-size:0.6rem;
                    letter-spacing:0.2em; text-transform:uppercase; color:rgba(255,255,255,0.6);
                    margin-bottom:8px;">AI · Predicted Role</div>
                  <div style="font-family:'Cormorant Garamond',serif; font-size:2.2rem;
                    font-weight:600; color:white; line-height:1.2;">
                    {prediction}
                  </div>
                </div>
                """, unsafe_allow_html=True)
 
            st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
            st.markdown("""
            <div style="font-family:'IBM Plex Mono',monospace; font-size:0.62rem;
              letter-spacing:0.2em; text-transform:uppercase; color:var(--ink-mute);
              margin-bottom:16px;">04 · Extracted Skills</div>
            """, unsafe_allow_html=True)
 
            skills = extract_skills(cleaned_resume)
 
            if skills:
                skill_html = "".join([
                    f'<span style="display:inline-block; background:var(--green-bg);'
                    f'border:1px solid var(--green); color:var(--green);'
                    f'font-family:\'IBM Plex Mono\',monospace; font-size:0.72rem;'
                    f'padding:5px 14px; border-radius:100px; margin:4px 5px 4px 0;'
                    f'transition:all 0.15s;">{s}</span>'
                    for s in skills
                ])
                st.markdown(f'<div style="padding:4px 0 12px;">{skill_html}</div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="font-family:'IBM Plex Mono',monospace; font-size:0.78rem;
                  color:var(--ink-mute); padding:8px 0;">
                  No recognisable technical skills detected.
                </div>
                """, unsafe_allow_html=True)
 
            if jd_single.strip():
                from sklearn.metrics.pairwise import cosine_similarity as cos_sim
 
                cleaned_jd = clean_text(jd_single)
                jd_vec = vectorizer.transform([cleaned_jd])
                jd_skills = extract_skills(cleaned_jd)
                # Base cosine similarity
                base_score = cos_sim(resume_vec, jd_vec)[0][0] * 100
                # Skill overlap bonus
                matched_count = len(set(skills) & set(jd_skills))
                skill_bonus = matched_count * 4
                # Final score
                score = min(round(base_score + skill_bonus, 2), 95)


                st.divider()
                st.markdown("""
                <div style="font-family:'IBM Plex Mono',monospace; font-size:0.62rem;
                  letter-spacing:0.2em; text-transform:uppercase; color:var(--ink-mute);
                  margin-bottom:20px;">05 · Role Match Analysis</div>
                """, unsafe_allow_html=True)
 
                score_color = "var(--green)" if score >= 60 else ("#F59E0B" if score >= 35 else "#EF4444")
                score_label = "Strong Match" if score >= 70 else ("Partial Match" if score >= 45 else "Weak Match")
 
                st.markdown(f"""
                <div style="background:var(--surface); border:1px solid var(--rule); border-radius:8px;
                  padding:32px 36px; margin-bottom:24px; box-shadow:var(--shadow);">
                  <div style="display:flex; align-items:flex-end; gap:24px; margin-bottom:20px;">
                    <div>
                      <div style="font-family:'IBM Plex Mono',monospace; font-size:0.6rem;
                        letter-spacing:0.2em; text-transform:uppercase;
                        color:var(--ink-mute); margin-bottom:4px;">Match Score</div>
                      <div style="font-family:'Cormorant Garamond',serif; font-size:4rem;
                        font-weight:600; color:{score_color}; line-height:1;">
                        {score}<span style="font-size:2rem; opacity:0.6;">%</span>
                      </div>
                    </div>
                    <div style="padding-bottom:10px;">
                      <span style="font-family:'IBM Plex Mono',monospace; font-size:0.72rem;
                        letter-spacing:0.08em; background:{score_color}22;
                        color:{score_color}; border:1px solid {score_color}44;
                        padding:5px 14px; border-radius:100px;">
                        {score_label}
                      </span>
                    </div>
                  </div>
                  <div style="background:var(--bg-secondary); border-radius:2px; height:6px; overflow:hidden;">
                    <div style="background:{score_color}; height:100%; width:{score}%;
                      border-radius:2px; transition:width 0.8s ease;"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
 
                jd_skills = extract_skills(cleaned_jd)
                missing = list(set(jd_skills) - set(skills))
 
                col_have, col_miss = st.columns(2, gap="large")
 
                with col_have:
                    st.markdown(f"""
                    <div style="font-family:'IBM Plex Mono',monospace; font-size:0.62rem;
                      letter-spacing:0.15em; text-transform:uppercase; color:var(--green);
                      margin-bottom:10px;">✓ &nbsp; Skills Matched ({len(set(skills) & set(jd_skills))})</div>
                    """, unsafe_allow_html=True)
                    matched = list(set(skills) & set(jd_skills))
                    if matched:
                        mhtml = "".join([
                            f'<span style="display:inline-block; background:var(--green-bg);'
                            f'border:1px solid var(--green); color:var(--green);'
                            f'font-family:\'IBM Plex Mono\',monospace; font-size:0.7rem;'
                            f'padding:4px 12px; border-radius:100px; margin:3px 4px 3px 0;">'
                            f'{s}</span>'
                            for s in matched
                        ])
                        st.markdown(mhtml, unsafe_allow_html=True)
                    else:
                        st.markdown('<span style="font-family:\'IBM Plex Mono\',monospace;font-size:0.78rem;color:var(--ink-mute);">None detected.</span>', unsafe_allow_html=True)
 
                with col_miss:
                    st.markdown(f"""
                    <div style="font-family:'IBM Plex Mono',monospace; font-size:0.62rem;
                      letter-spacing:0.15em; text-transform:uppercase; color:#EF4444;
                      margin-bottom:10px;">✗ &nbsp; Skill Gaps ({len(missing)})</div>
                    """, unsafe_allow_html=True)
                    if missing:
                        ghtml = "".join([
                            f'<span style="display:inline-block; background:#FEE2E2;'
                            f'border:1px solid #FECACA; color:#EF4444;'
                            f'font-family:\'IBM Plex Mono\',monospace; font-size:0.7rem;'
                            f'padding:4px 12px; border-radius:100px; margin:3px 4px 3px 0;">'
                            f'{s}</span>'
                            for s in missing
                        ])
                        st.markdown(ghtml, unsafe_allow_html=True)
                    else:
                        st.markdown('<span style="font-family:\'IBM Plex Mono\',monospace;font-size:0.78rem;color:var(--green);">All required skills present.</span>', unsafe_allow_html=True)
 
                st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
                st.markdown("""
                <div style="font-family:'IBM Plex Mono',monospace; font-size:0.62rem;
                  letter-spacing:0.2em; text-transform:uppercase; color:var(--ink-mute);
                  margin-bottom:16px;">06 · AI Recruiter Assessment</div>
                """, unsafe_allow_html=True)
 
                with st.spinner("Generating expert assessment…"):
                    feedback = get_feedback(resume_text, jd_single, score)
 
                st.markdown(f"""
                <div style="background:var(--surface); border:1px solid var(--rule);
                  border-left:4px solid var(--green); border-radius:0 8px 8px 0;
                  padding:28px 32px; box-shadow:var(--shadow);">
                  <div style="display:flex; align-items:center; gap:10px; margin-bottom:16px;">
                    <div style="width:28px; height:28px; background:var(--green); border-radius:50%;
                      display:flex; align-items:center; justify-content:center;
                      font-size:0.7rem; color:white;">AI</div>
                    <div style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem;
                      letter-spacing:0.1em; text-transform:uppercase; color:var(--ink-soft);">
                      Gemini · Recruiter Intelligence
                    </div>
                  </div>
                  <div style="font-family:'IBM Plex Sans',sans-serif; font-size:0.88rem;
                    line-height:1.8; color:var(--ink-soft);">
                    {feedback}
                  </div>
                </div>
                """, unsafe_allow_html=True)
 
            st.divider()
            st.markdown("""
            <div style="font-family:'IBM Plex Mono',monospace; font-size:0.62rem;
              letter-spacing:0.2em; text-transform:uppercase; color:var(--ink-mute);
              margin-bottom:12px;">07 · Export</div>
            """, unsafe_allow_html=True)
 
            pdf_bytes = generate_report(parsed, prediction, skills, score if jd_single.strip() else 0, missing if jd_single.strip() else [], feedback if jd_single.strip() else "")
 
            col_dl, _ = st.columns([1, 3])
            with col_dl:
                st.download_button("⬇  Download Full PDF Report", pdf_bytes, "candidate_report.pdf", "application/pdf", use_container_width=True)
 
with tab3:
    st.markdown("""
    <div style="max-width:760px; margin:0 auto; padding:8px 0 60px;">
      <div style="font-family:'Cormorant Garamond',serif; font-size:2.4rem;
        font-weight:300; color:var(--ink); margin-bottom:8px; line-height:1.2;">
        The Intelligence Behind<br>
        <em style="font-weight:600;">RecruitLens</em>
      </div>
      <div style="font-family:'IBM Plex Mono',monospace; font-size:0.72rem;
        color:var(--ink-mute); letter-spacing:0.06em; margin-bottom:48px;">
        A brief overview of the technology stack and methodology
      </div>
    </div>
    """, unsafe_allow_html=True)
 
    steps = [
        ("01", "Text Extraction", "IBM Plex Mono",
         "PDFs are parsed using PyMuPDF to extract raw text. For scanned documents, OCR is applied as a fallback."),
        ("02", "NLP Preprocessing", "Tokenisation + Cleaning",
         "Text is cleaned, tokenised, stop-words removed, and lemmatised using spaCy. The resulting corpus is normalised."),
        ("03", "Semantic Embedding", "Sentence Transformers",
         "Both resumes and job descriptions are encoded into dense vector representations using Sentence Transformers."),
        ("04", "Similarity Ranking", "Cosine Similarity",
         "Candidate vectors are ranked against the job description vector using cosine similarity."),
        ("05", "Skill Extraction", "spaCy NER + Custom Taxonomy",
         "A NER pipeline enriched with a curated 500+ skill taxonomy identifies technical and soft skills."),
        ("06", "AI Assessment", "Google Gemini LLM",
         "The full resume text, job description, and computed match score are sent to Gemini for contextual evaluation."),
    ]
 
    for num, title, sub, desc in steps:
        st.markdown(f"""
        <div style="display:flex; gap:32px; padding:28px 0;
          border-bottom:1px solid var(--rule); max-width:760px;">
          <div style="flex-shrink:0; width:44px;">
            <div style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem;
              letter-spacing:0.12em; color:var(--ink-mute); margin-top:4px;">{num}</div>
          </div>
          <div style="flex:1;">
            <div style="font-family:'Cormorant Garamond',serif; font-size:1.3rem;
              font-weight:600; color:var(--ink); margin-bottom:2px;">{title}</div>
            <div style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem;
              letter-spacing:0.1em; text-transform:uppercase; color:var(--green);
              margin-bottom:10px;">{sub}</div>
            <div style="font-family:'IBM Plex Sans',sans-serif; font-size:0.86rem;
              line-height:1.75; color:var(--ink-soft);">{desc}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
 
    st.markdown("""
    <div style="max-width:760px; background:var(--green); border-radius:8px;
      padding:32px 40px; margin-top:40px;">
      <div style="font-family:'Cormorant Garamond',serif; font-size:1.6rem;
        font-weight:600; color:white; margin-bottom:8px;">
        Built for Recruiters, Powered by AI
      </div>
      <div style="font-family:'IBM Plex Sans',sans-serif; font-size:0.85rem;
        color:rgba(255,255,255,0.75); line-height:1.7;">
        RecruitLens is designed to augment — not replace — recruiter judgment.
        It surfaces signal in high-volume candidate pools.
      </div>
    </div>
    """, unsafe_allow_html=True)
 
st.markdown("""
<div style="border-top:1px solid var(--rule); margin-top:60px; padding:28px 0;
  display:flex; align-items:center; justify-content:space-between;">
  <div style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem;
    letter-spacing:0.1em; color:var(--ink-mute);">
    RecruitLens AI · v2.0 · Resume Intelligence Platform
  </div>
  <div style="font-family:'IBM Plex Mono',monospace; font-size:0.62rem;
    color:var(--ink-mute); letter-spacing:0.06em;">
    Sentence Transformers · spaCy · Gemini · sklearn
  </div>
</div>
""", unsafe_allow_html=True)
 


 # python -m streamlit run src/app.py




 