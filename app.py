import streamlit as st
import re
import zipfile
import xml.dom.minidom

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "when",
    "at", "by", "for", "with", "about", "against", "between", "into",
    "through", "during", "before", "after", "above", "below", "to", "from",
    "up", "down", "in", "out", "on", "off", "over", "under", "again",
    "further", "then", "once", "here", "there", "when", "where", "why",
    "how", "all", "any", "both", "each", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "s", "t", "can", "will", "just", "don",
    "should", "now", "i", "me", "my", "myself", "we", "our", "ours",
    "ourselves", "you", "your", "yours", "yourself", "yourselves", "he",
    "him", "his", "himself", "she", "her", "hers", "herself", "it", "its",
    "itself", "they", "them", "their", "theirs", "themselves", "what",
    "which", "who", "whom", "this", "that", "these", "those", "am", "is",
    "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "having", "do", "does", "did", "doing"
}

def extract_text_from_docx(file):
    
    try:
        with zipfile.ZipFile(file) as z:
            xml_content = z.read('word/document.xml')
        dom = xml.dom.minidom.parseString(xml_content)
        text_elements = dom.getElementsByTagName('w:t')
        return '\n'.join([t.firstChild.nodeValue for t in text_elements if t.firstChild])
    except Exception as e:
        return f"Error reading DOCX: {e}"

def extract_text_from_pdf(file):
    
    try:
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text
    except ImportError:
        return "Error: PyPDF2 library not installed. Please run 'pip install PyPDF2'."
    except Exception as e:
        return f"Error reading PDF: {e}"

def extract_text(uploaded_file):
    """Dispatcher for file extraction."""
    if uploaded_file.name.endswith('.docx'):
        return extract_text_from_docx(uploaded_file)
    elif uploaded_file.name.endswith('.pdf'):
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.name.endswith('.txt'):
        return str(uploaded_file.read(), "utf-8")
    else:
        return ""

def preprocess_text(text):
    text_lower = text.lower()
    text_clean = re.sub(r'[^a-z0-9\s]', ' ', text_lower)
    tokens = text_clean.split()
    cleaned_tokens = [t for t in tokens if t not in STOPWORDS]
    return set(cleaned_tokens), text_lower

def extract_years_experience(text):
    pattern = r'(\d+(?:\.\d+)?)\+?\s*-?\s*(?:\d+)?\s*(?:years?|yrs?)'
    matches = re.findall(pattern, text)
    years = []
    for match in matches:
        try:
            years.append(float(match))
        except ValueError:
            continue
            
    if not years:
        return 0
    
    return max(years)

def extract_contact_info(text):
    
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    
    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)
    
    return {
        "email": emails[0] if emails else "Not Found",
        "phone": phones[0] if phones else "Not Found"
    }

def evaluate_resume(text, required_skills, min_exp_years):
   
    tokens, clean_full_text = preprocess_text(text)
    
    
    req_skills_clean = {s.lower().strip() for s in required_skills if s.strip()}
    
    if not req_skills_clean:
        match_score = 0
        missing = []
        found = []
    else:
        
        found = []
        missing = []
        
        for skill in req_skills_clean:
           
            if ' ' not in skill:
                if skill in tokens:
                    found.append(skill)
                else:
                    missing.append(skill)
            else:
                if skill in clean_full_text:
                    found.append(skill)
                else:
                    missing.append(skill)
        
   
    detected_exp = extract_years_experience(clean_full_text)
    
    if req_skills_clean:
        skill_percent = len(found) / len(req_skills_clean)
    else:
        skill_percent = 1.0 
        
    exp_met = detected_exp >= min_exp_years
    
    
    exp_score_part = 1.0 if exp_met else (detected_exp / min_exp_years if min_exp_years > 0 else 1.0)
    exp_score_part = min(exp_score_part, 1.0)
    
    final_score = (skill_percent * 70) + (exp_score_part * 30)
    
    return {
        "score": round(final_score, 1),
        "found_skills": found,
        "missing_skills": missing,
        "detected_exp": detected_exp,
        "exp_met": exp_met,
        "contact": extract_contact_info(text)
    }

st.set_page_config(page_title="Rule-Based Resume Screener", layout="wide")

st.title(" Deterministic Resume Screener")

st.sidebar.header("1. Define Requirements")

default_skills = "Python, SQL,Communication,html,Css,Javascript,java,C,React,Git,C++,Lead,Leadership"
skills_input = st.sidebar.text_area("Required Skills (comma-separated)", value=default_skills, height=100)
required_skills_list = [s.strip() for s in skills_input.split(",") if s.strip()]

min_experience = st.sidebar.number_input("Minimum Years of Experience", min_value=0, value=1, step=1)

st.header("2. Upload Resume")

uploaded_file = st.file_uploader("Upload PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    with st.spinner("Extracting text and analyzing..."):
        
        raw_text = extract_text(uploaded_file)
        
        if len(raw_text) < 50:
            st.error("Could not extract enough text from the file. It might be an image-based PDF or empty.")
        else:
            result = evaluate_resume(raw_text, required_skills_list, min_experience)
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("Match Score")
                score = result['score']
                
                if score >= 80:
                    score_color = "green"
                elif score >= 50:
                    score_color = "orange"
                else:
                    score_color = "red"
                
                st.markdown(f"<h1 style='color:{score_color}; font-size: 72px;'>{score}%</h1>", unsafe_allow_html=True)

                st.write("---")
                st.caption("Contact Info:")
                st.write(f" {result['contact']['email']}")
                st.write(f" {result['contact']['phone']}")

            with col2:
                st.subheader("Detailed Analysis")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("###  Matched Skills")
                    if result['found_skills']:
                        for s in result['found_skills']:
                            st.markdown(f"- {s}")
                    else:
                        st.write("No matches found.")
                        
                with c2:
                    st.markdown("###  Missing Skills")
                    if result['missing_skills']:
                        for s in result['missing_skills']:
                            st.markdown(f"- {s}")
                    else:
                        st.write("All skills matched!")
                
                st.write("---")
                
                with st.expander("View Extracted Raw Text"):
                    st.text(raw_text[:2000] + "...")

else:

    st.info("Awaiting resume upload...")
