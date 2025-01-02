import streamlit as st
import os
from dotenv import load_dotenv
import PyPDF2  # PyPDF2 to extract text from the PDF
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Generative AI API key
genai.configure(api_key=os.getenv("GOOGLE_KEY"))


# Function to extract text from uploaded PDF
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        # Extract text from PDF
        reader = PyPDF2.PdfReader(uploaded_file)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text()

        if not pdf_text.strip():
            raise ValueError("No text found in the PDF. Please upload a valid resume with text.")

        return pdf_text
    else:
        raise FileNotFoundError("No file uploaded")

# Function to get response from Google Generative AI with improved prompt handling
def get_gemini_response(input, pdf_text, prompt):
    # New prompt structure: Ask the model to stick to the data and provide a fallback if information is missing
    refined_prompt = f"""
    Here is the job description: {input}

    Below is the resume text:
    {pdf_text}

    {prompt}

    Please only use the information provided in the resume. If specific details (e.g., education, skills, experience) 
    are missing, mention that the information is not available, and do not infer or create data.
    """
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([refined_prompt])
    return response.text

# Define different prompts for each evaluation category
prompts = {
    "Contact Details": """
        Provide all the cotact details present in the resume along with full name, In a structure manner. If no contact details found, 
        state "No oontact details identified in the resume."
    """,

    "Education": """
        Assess the applicant's all educational background, In a structure manner. If no educational details are provided,
        state "No education information found in the resume."
    """,

    "Experience": """
        Analyze the relevance and depth of the candidate's work history for the role, In a structure manner. If no experience is mentioned,
        return "No work experience information provided."
    """,

    "Industry-specific Knowledge": """
        Assess how well the candidate's background aligns with the industry, In a structure manner. If no relevant industry experience is found, 
        state "No industry-specific knowledge identified in the resume."
    """,

    "Job Matching": """
        Calculate and display an overall percentage match between the resume and the job description. 
        Present this as "Overall Match: X%" and provide a brief explanation based strictly on resume content.In a structure manner.
        If no job description section is , state "Please enter the job description properly"
    """,

    "Potential Red Flags": """
        Note any concerns or potential issues that may need further investigation during the interview process based on the resume content.
        If nothing stands out, state "No potential red flags based on the available information."
    """,

    "Potential Red Flags": """
        Note any concerns or potential issues that may need further investigation during the interview process based on the resume content.
        If nothing stands out, state "No potential red flags based on the available information."
    """,

    "Strengths": """
        Identify and elaborate on the top 3-5 strengths of the candidate relevant to the role based solely on the resume, In a structure manner
        If not enough information is provided, state "Limited information available to identify strengths."
    """,

    "Soft Skills": """
        Evaluate any soft skills that are either mentioned or implied in the resume, In a structure manner. If none are found, state "No soft skills explicitly listed."
    """,

    "Summary": """
        Summarize the overall assessment of the resume, considering strengths, areas for improvement, and a final recommendation.
        Use only the information present in the resume, and indicate any missing sections clearly In a structure manner.
    """,

    "Technical Skills": """
        Evaluate the candidate's technical abilities in relation to the role, based only on the listed skills in the resume.In a structure manner.
        If the information is missing, state "No technical skills listed."
    """,
}

# Streamlit App Configuration
st.set_page_config(page_title="Resume Scanner Expert", layout="wide")
st.sidebar.title("Resume Evaluation Sections")

# Sidebar Buttons for Different Categories
input_text = st.text_area("Job Description: ", key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

if uploaded_file is not None:
    st.sidebar.success("PDF Uploaded Successfully")
    pdf_content = input_pdf_setup(uploaded_file)
else:
    st.sidebar.warning("Please upload a resume to proceed")

# Evaluation buttons in the sidebar
for section, prompt in prompts.items():
    if st.sidebar.button(section):
        if uploaded_file is not None:
            response = get_gemini_response(input_text, pdf_content, prompt)
            st.subheader(f"{section} Analysis")
            st.write(response)
        else:
            st.write("Please upload a resume")

# Enhancing the UI with a clean look
st.markdown("""
    <style>
        .css-12oz5g7 {padding: 20px 50px;} /* Adjust spacing for a more professional feel */
        .css-184tjsw p {font-size: 16px; line-height: 1.6;} /* Make text size and spacing more readable */
        .css-2trqyj {margin-bottom: 20px;} /* Increase button spacing */
        .css-1x8cf1d {color: #6c757d;} /* Muted sidebar text color */
        h2 {color: #2c3e50;}
        h3 {color: #2980b9;}
    </style>
""", unsafe_allow_html=True)
