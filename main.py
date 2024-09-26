import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from streamlit_option_menu import option_menu


load_dotenv()


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_response(input_prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input_prompt)
    return response.text


def pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text


def create_pie_chart(match_percentage):
    labels = 'Match', 'Mismatch'
    sizes = [match_percentage, 100 - match_percentage]
    colors = ['#66b3ff', '#ff9999']
    explode = (0.1, 0)  # explode the first slice (Match)

    fig, ax = plt.subplots(figsize=(4,4))  # Create a smaller figure
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
           shadow=True, startangle=90)
    ax.axis('equal')

    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return f'<img src="data:image/png;base64,{img_base64}" style="width:150px;height:150px;"/>'


input1 = """
Hey, act like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of the tech field, software engineering, data science, data analysis,
and big data engineering. Your task is to evaluate the resume based on the given job description.
You must consider that the job market is very competitive and you should provide 
the best assistance for improving the resumes. Assign a percentage match based 
on the job description and list the missing keywords with high accuracy.
Resume: {text}
Description: {jd}

I want the response in a single string with the structure:
{{"JD Match":"%",<br><br>
"MissingKeywords":[] ,<br><br>
"Profile Summary":""}}
"""

input2 = """
You have experience in verifying resumes and ensuring that sections are parsed correctly.
You highlight the skills listed on the resume based on the job description. 
You identify any mistakes and missing keywords in the resume according to the description. 
You also provide suggestions for arranging the sections in the correct order.
"""

st.set_page_config(page_title="Genius Guage ^_^")

with st.sidebar:
    select = option_menu(
        menu_title="MAIN MENU",
        options=["HOME", 'ABOUT', "CONTACT"]
    )


if select == "HOME":
    st.markdown("<h1 style='color: red;'>Genius Guage</h1>", unsafe_allow_html=True)
    st.text("Check And Improve Your Resume ATS Score")
    jd = st.text_area("Paste the Job Description")
    uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the PDF file")

    if st.button("Submit"):
        if uploaded_file is not None:
            resume_text = pdf_text(uploaded_file)
            formatted_prompt = input1.format(text=resume_text, jd=jd)
            response = get_response(formatted_prompt)

            response_dict = json.loads(response.replace('<br><br>', ''))
            match_percentage = int(response_dict["JD Match"].replace('%', ''))

            pie_chart_html = create_pie_chart(match_percentage)

            response_with_chart = response.replace('JD Match":"{}%"'.format(match_percentage),
                                                   '{}<br> **JD Match":"{}%"**'.format(pie_chart_html,match_percentage))

            st.subheader("ATS Evaluation Result")
            st.markdown(response_with_chart, unsafe_allow_html=True)
        else:
            st.write("Please upload the PDF file.")

    if st.button("Parse Your Resume"):
        if uploaded_file is not None:
            resume_text = pdf_text(uploaded_file)
            formatted_prompt = input2.format(text=resume_text, jd=jd)
            response = get_response(formatted_prompt)
            st.subheader("Resume Parsing Result")
            st.markdown(response, unsafe_allow_html=True)
        else:
            st.write("Please upload the PDF file.")

elif select == "ABOUT":
    st.title("About Genius Guage")
    st.write("""**Genius Guage** is an advanced tool designed to enhance your resume's ATS (Applicant Tracking System) score, crucial for securing job interviews in a competitive job market. By comparing your resume against specific job descriptions, it provides a comprehensive evaluation to ensure your resume stands out.

**Key Features:**

- **Resume Analysis:** It meticulously scans your resume, highlighting strengths and areas needing improvement.
- **Keyword Matching:** Identifies and lists missing keywords that are critical for passing ATS filters.
- **ATS Score:** Assigns a percentage match to indicate how well your resume aligns with the job description.
- **Profile Summary:** Offers a summary of your profile, emphasizing key skills and experiences.
- **Section Arrangement:** Provides suggestions on organizing resume sections effectively.
- **Error Detection:** Spots mistakes and inconsistencies, ensuring a polished resume.
- **Field Expertise:** Tailored for tech fields, including software engineering, data science, and big data engineering.

**Benefits:**

- **Enhanced Visibility:** Improves chances of your resume being shortlisted by ATS.
- **Detailed Feedback:** Offers actionable insights for resume enhancement.
- **Competitiveness:** Helps you stay competitive in a crowded job market.
- **User-Friendly:** Easy-to-use interface for quick and efficient resume assessment.

By leveraging Genius Guage, you can optimize your resume to better match job descriptions, significantly increasing your chances of landing interviews and advancing your career.""")
elif select == "CONTACT":
    st.title("Contact Us")
    st.write("For inquiries, please contact us at **[support@geniusguage.com](mailto:pavanmandavilli485@gmail.com)**.")

    st.subheader("Send us a message")
    st.write("You can also send us an email directly by clicking the link above.")