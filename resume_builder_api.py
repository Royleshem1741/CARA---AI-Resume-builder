from fastapi import FastAPI, HTTPException, Body, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Dict, List, Optional, Any
import os
import subprocess
import json
import time
from main import EnhancedResumeBuilder  # Import existing EnhancedResumeBuilder class

#טיפול בהורדת קבצים בצד לקוח (בדפדפן)
from fastapi.responses import FileResponse
import io
import tempfile


app = FastAPI(title="CARA Resume Builder API", description="API for the CARA Resume Builder")

# Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development. In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class UserInfo(BaseModel):
    full_name: str
    job_role: str
    resume_level: str

class QuestionResponse(BaseModel):
    key: str
    answer: str

class ResumeGenerationRequest(BaseModel):
    format: str  # 'html' or 'text'
    style: str   # 'traditional', 'modern', or 'creative'
    confirmed_skills: Dict[str, List[str]]

class TranslationRequest(BaseModel):
    filename: str
    target_language: str

# Global variable to store the resume builder instance
resume_builder_instance = None

@app.post("/api/initialize")
async def initialize_session(user_info: UserInfo):
    """
    Initialize a new resume building session with user info
    """
    global resume_builder_instance
    
    try:
        # Create a new instance of your EnhancedResumeBuilder
        resume_builder_instance = EnhancedResumeBuilder()
        
        # Set initial properties
        resume_builder_instance.user_name = user_info.full_name
        resume_builder_instance.job_role = user_info.job_role
        resume_builder_instance.resume_level = user_info.resume_level
        
        # Save the name to user_data
        resume_builder_instance.user_data["full_name"] = user_info.full_name
        
        # Initialize questions based on user profile
        resume_builder_instance.questions = resume_builder_instance._initialize_questions()
        
        return {
            "status": "success",
            "message": "Resume builder session initialized",
            "total_questions": len(resume_builder_instance.questions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize: {str(e)}")

@app.post("/api/follow-up/linkedin_profiles")
async def linkedin_followup(data: dict):
    """
    Handle follow-up response for LinkedIn profiles
    """
    global resume_builder_instance
    
    if not resume_builder_instance:
        raise HTTPException(status_code=400, detail="Session not initialized")
    
    try:
        answer = data.get("answer", "").strip()
        if answer:
            # Update LinkedIn entry with additional profiles
            original_answer = resume_builder_instance.user_data.get("linkedin", "")
            resume_builder_instance.user_data["linkedin"] = f"{original_answer}\nOther profiles: {answer}"
            resume_builder_instance.user_data["linkedin_followup_asked"] = True
        
        return {
            "status": "success",
            "message": "LinkedIn follow-up response saved"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing follow-up: {str(e)}")

@app.post("/api/follow-up/location")
async def location_followup(data: dict):
    """
    Handle follow-up response for work arrangement preference
    """
    global resume_builder_instance
    
    if not resume_builder_instance:
        raise HTTPException(status_code=400, detail="Session not initialized")
    
    try:
        work_arrangement = data.get("answer", "").strip()
        if work_arrangement:
            # Update location with work arrangement preference
            location = resume_builder_instance.user_data.get("location", "")
            resume_builder_instance.user_data["location"] = f"Location: {location}\nWork Arrangement: {work_arrangement}"
        
        return {
            "status": "success",
            "message": "Work arrangement preference saved"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing follow-up: {str(e)}")

@app.post("/api/follow-up/job_details")
async def job_details_followup(data: dict):
    """
    Handle follow-up response for missing job details
    """
    global resume_builder_instance
    
    if not resume_builder_instance:
        raise HTTPException(status_code=400, detail="Session not initialized")
    
    try:
        additional_details = data.get("answer", "").strip()
        if additional_details:
            # Append additional details to job history
            job_history = resume_builder_instance.user_data.get("job_history", "")
            resume_builder_instance.user_data["job_history"] = f"{job_history}\n{additional_details}"
        
        return {
            "status": "success",
            "message": "Job details saved"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing follow-up: {str(e)}")

@app.post("/api/follow-up/work_arrangement")
async def work_arrangement_followup(data: dict):
    """
    Handle follow-up response for work arrangement preference
    """
    global resume_builder_instance
    
    if not resume_builder_instance:
        raise HTTPException(status_code=400, detail="Session not initialized")
    
    try:
        work_arrangement = data.get("answer", "").strip()
        if work_arrangement:
            # Update location with work arrangement preference
            location = resume_builder_instance.user_data.get("location", "")
            resume_builder_instance.user_data["location"] = f"Location: {location}\nWork Arrangement: {work_arrangement}"
        
        return {
            "status": "success",
            "message": "Work arrangement preference saved"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing follow-up: {str(e)}")
    
@app.get("/api/questions")
async def get_questions():
    """
    Get the list of questions based on the initialized profile
    """
    global resume_builder_instance
    
    if not resume_builder_instance:
        raise HTTPException(status_code=400, detail="Session not initialized. Call /api/initialize first")
    
    try:
        questions = resume_builder_instance.questions
        return {
            "questions": [
                {
                    "index": i,
                    "key": q["key"],
                    "question": q["question"],
                    "section": q["section"]
                }
                for i, q in enumerate(questions)
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving questions: {str(e)}")

@app.get("/api/question/{index}")
async def get_question(index: int):
    """
    Get a specific question by its index
    """
    global resume_builder_instance
    
    if not resume_builder_instance:
        raise HTTPException(status_code=400, detail="Session not initialized")
    
    try:
        questions = resume_builder_instance.questions
        if 0 <= index < len(questions):
            return {
                "index": index,
                "key": questions[index]["key"],
                "question": questions[index]["question"],
                "section": questions[index]["section"],
                "current_answer": resume_builder_instance.user_data.get(questions[index]["key"], "")
            }
        else:
            raise HTTPException(status_code=404, detail="Question index out of range")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving question: {str(e)}")

@app.post("/api/answer/{index}")
async def save_answer(index: int, response: QuestionResponse):
    """
    Save an answer for a specific question
    """
    global resume_builder_instance
    
    if not resume_builder_instance:
        raise HTTPException(status_code=400, detail="Session not initialized")
    
    try:
        questions = resume_builder_instance.questions
        if 0 <= index < len(questions):
            question = questions[index]
            key = question["key"]
            answer = response.answer.strip()
            
            # Validate email if that's the current question
            if key == 'email' and answer:
                from main import validate_email
                if not validate_email(answer):
                    raise HTTPException(status_code=400, detail="Invalid email format")
            
            # Save the answer
            resume_builder_instance.user_data[key] = answer
            
            # Add to conversation history (used by some methods in the original backend)
            resume_builder_instance.conversation_history.append({"role": "user", "content": answer})
            
            # Now we call the original follow-up methods
            followup_data = None
            try:
                # Call _check_for_follow_up method directly
                # This method in the original code doesn't return anything,
                # but updates the conversation and asks follow-up questions in-line
                
                # For LinkedIn follow-ups
                if key == 'linkedin':
                    if answer.lower() in ['no', 'n', 'none', '', 'dont have one', "don't have one", 'dont have', "don't have", 'i dont have one', 'i dont', 'skip']:
                        followup_data = {
                            "type": "linkedin_profiles",
                            "message": "Do you have any other professional social media profiles you'd like to include? (e.g., GitHub, portfolio website)"
                        }
                
                # For location follow-ups
                elif key == 'location':
                    followup_data = {
                        "type": "work_arrangement",
                        "message": "What is your preferred work arrangement? (Remote, Hybrid, On-site, or No preference)"
                    }
                
                # For job history follow-ups (check for missing dates, etc.)
                elif key == 'job_history':
                    # Run an analysis to check for missing details
                    if not any(word in answer.lower() for word in ['2025','2024','2023', '2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010', '2009', '2008', '2007', '2006', '2005', '2004', '2003', '2002', '2001', '2000', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'january', 'february', 'march', 'april', 'june', 'july', 'august', 'september', 'october', 'november', 'december']):
                        followup_data = {
                            "type": "job_details",
                            "message": "If you accidentally left out any of the details regarding the date range, job title, or company name, it's recommended to add them now for maximum clarity"
                        }
                
                # Generate additional context-based follow-up questions using the original method
                if not followup_data:  # Only for substantial answers
                    try:

                        # Use the original _analyze_professional_context method to generate follow-up questions
                        original_question = questions[index]["question"]  # Get the original question
                        question_key = questions[index]["key"]
                        question_section = questions[index]["section"]
                        professional_questions = resume_builder_instance._analyze_professional_context(answer, original_question, question_key, question_section)

                        if professional_questions and len(professional_questions) > 0:
                            followup_data = {
                                "type": "professional_context",
                                "message": professional_questions[0],  # Take the first question
                                "additional_questions": professional_questions[1:] if len(professional_questions) > 1 else []
                            }
                    except Exception as context_error:
                        # Silently fail if the context analysis doesn't work
                        pass
            except Exception as followup_error:
                # If follow-up detection fails, we continue without it
                pass
            
            # Get feedback for important sections
            feedback = None
            if key in ['summary', 'job_history', 'achievements', 'technical_skills']:
                try:
                    # Call the original feedback method
                    resume_builder_instance._provide_feedback(key, answer)
                    
                    # Since the original method doesn't return anything (it just prints to console),
                    # we'll simulate a similar feedback here for the frontend
                    if key == "summary":
                        prompt = f"Based on this professional summary for a {resume_builder_instance.job_role} position, give ONE brief, specific, encouraging suggestion for improvement or ONE positive point worth emphasizing. Keep it under 50 words and conversational: '{answer}'"
                    elif key == "job_history":
                        prompt = f"Based on this work experience for a {resume_builder_instance.job_role} resume, give ONE brief, specific tip for better highlighting achievements or impact. Keep it under 50 words and conversational: '{answer}'"
                    elif key == "achievements":
                        prompt = f"Based on these achievements for a {resume_builder_instance.job_role} position, suggest ONE way to quantify or strengthen the impact. Keep it under 50 words and conversational: '{answer}'"
                    elif key == "technical_skills":
                        prompt = f"Based on these technical skills for a {resume_builder_instance.job_role} position, give ONE brief suggestion for better organization or presentation. Keep it under 50 words and conversational: '{answer}'"
                    
                    # Use OpenAI API
                    import openai
                    feedback_response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful resume coach giving brief, friendly, specific advice."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=100,
                    )
                    
                    feedback_message = feedback_response.choices[0].message.content.strip()
                    feedback = {"message": f"💡 {feedback_message}"}
                except Exception as feedback_error:
                    # If feedback generation fails, continue without it
                    pass
            
            # Create a response that includes both the answer status and any follow-up info
            response_data = {
                "status": "success",
                "message": "Answer saved",
                "feedback": feedback
            }
            
            # Add follow-up info if available
            if followup_data:
                response_data["followup"] = followup_data
            
            return response_data
        else:
            raise HTTPException(status_code=404, detail="Question index out of range")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving answer: {str(e)}")
       
@app.post("/api/follow-up/professional_context")
async def professional_context_followup(data: dict):
    """
    Handle follow-up response for professional context questions
    """
    global resume_builder_instance
    
    if not resume_builder_instance:
        raise HTTPException(status_code=400, detail="Session not initialized")
    
    try:
        context_answer = data.get("answer", "").strip()
        original_key = data.get("original_key", "")
        
        if context_answer and original_key and original_key in resume_builder_instance.user_data:
            # Append the additional context to the original answer
            original_answer = resume_builder_instance.user_data[original_key]
            resume_builder_instance.user_data[original_key] = f"{original_answer}\n\nAdditional context: {context_answer}"
        
        return {
            "status": "success",
            "message": "Additional context saved",
            "next_question": data.get("next_question", None)  # Return the next follow-up question if available
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing follow-up: {str(e)}")
    
@app.get("/api/answers")
async def get_all_answers():
    """
    Get all answers provided so far
    """
    global resume_builder_instance
    
    if not resume_builder_instance:
        raise HTTPException(status_code=400, detail="Session not initialized")
    
    try:
        return {
            "answers": resume_builder_instance.user_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving answers: {str(e)}")

@app.post("/api/analyze-skills")
async def analyze_skills():
    """
    Analyze user responses to identify implied skills
    """
    global resume_builder_instance
    
    if not resume_builder_instance:
        raise HTTPException(status_code=400, detail="Session not initialized")
    
    try:
        # Call the actual _analyze_and_enhance_skills method
        implied_skills = resume_builder_instance._analyze_and_enhance_skills()
        
        if not implied_skills or not any(implied_skills.values()):
            # Return empty skills if analysis failed or found nothing
            return {
                "status": "success",
                "implied_skills": {
                    "technical_skills": [],
                    "soft_skills": [],
                    "domain_knowledge": [],
                    "tools_and_platforms": []
                }
            }
        
        return {
            "status": "success",
            "implied_skills": implied_skills
        }
    except Exception as e:
        # Instead of failing, return empty skills set
        return {
            "status": "warning",
            "message": f"Could not analyze skills: {str(e)}",
            "implied_skills": {
                "technical_skills": [],
                "soft_skills": [],
                "domain_knowledge": [],
                "tools_and_platforms": []
            }
        }

@app.post("/api/generate-resume")
async def generate_resume(request: ResumeGenerationRequest):
    """
    Generate the resume based on user answers and format preferences
    """
    global resume_builder_instance
    
    if not resume_builder_instance:
        raise HTTPException(status_code=400, detail="Session not initialized")
    
    try:
        # Store confirmed skills
        resume_builder_instance.confirmed_skills = request.confirmed_skills
        
        # Get format and style
        resume_format = request.format  # 'html' or 'text'
        resume_style = request.style    # 'traditional', 'modern', or 'creative'
        
        # Generate filename
        name_part = resume_builder_instance.user_data.get('full_name', 'resume').replace(' ', '_').lower()
        job_part = resume_builder_instance.job_role.replace(' ', '_').lower()
        file_extension = "html" if resume_format == 'html' else "txt"
        filename = f"{name_part}_{job_part}_resume.{file_extension}"
        
        # Build the system message for OpenAI
        system_message = f"""
        You are an expert resume writer specializing in creating {resume_style} resumes for {resume_builder_instance.resume_level} level {resume_builder_instance.job_role} positions.
        
        Create a highly professional, ATS-friendly resume that showcases the candidate's qualifications effectively.
        
        For a {resume_builder_instance.resume_level} level position:
        - {resume_builder_instance.resume_level} level priorities: {"leadership impact and strategic vision" if resume_builder_instance.resume_level == "executive" else "professional achievements and growth" if resume_builder_instance.resume_level == "mid-level" else "education, skills, and potential"}
        - Language style: {"authoritative and strategic" if resume_builder_instance.resume_level == "executive" else "confident and accomplished" if resume_builder_instance.resume_level == "mid-level" else "enthusiastic and promising"}
        - Focus areas: {"leadership, transformation, and business results" if resume_builder_instance.resume_level == "executive" else "achievements, expertise, and career progression" if resume_builder_instance.resume_level == "mid-level" else "education, skills, and relevant experience"}
        
        Content style for a {resume_style} resume:
        - {"Formal and structured content with traditional terminology" if resume_style == "traditional" else "Concise and impactful descriptions with modern industry terms" if resume_style == "modern" else "Engaging and distinctive content that showcases personality while remaining professional"}
        
        IMPORTANT FORMATTING GUIDELINES:
        - Create a coherent, polished, and error-free document
        - Use action verbs and quantifiable achievements
        - Ensure perfect spelling, grammar, and consistent formatting
        - Focus on results and accomplishments, not just responsibilities
        - Tailor content specifically to a {resume_builder_instance.job_role} position

        IMPORTANT - ENHANCE JOB DESCRIPTIONS:
        For each job or project in the candidate's experience:
        1. Identify key responsibilities that may be understated
        2. Add specific, relevant accomplishments that align with their described duties
        3. Use industry-standard terminology to elevate their descriptions
        4. Ensure quantifiable achievements where possible (%, numbers, metrics)
        5. Highlight leadership, initiative, and problem-solving when evident

        Do this naturally and authentically, staying true to their actual experience.

        IMPORTANT ABOUT SKILLS AND CAPABILITIES:
        In addition to explicitly mentioned skills, incorporate these implied skills that are evident from the candidate's experiences (but only if relevant and authentic to their background):

        Technical Skills: {', '.join(request.confirmed_skills.get('technical_skills', []))}
        Soft Skills: {', '.join(request.confirmed_skills.get('soft_skills', []))}
        Domain Knowledge: {', '.join(request.confirmed_skills.get('domain_knowledge', []))}
        Tools & Platforms: {', '.join(request.confirmed_skills.get('tools_and_platforms', []))}

        These should be integrated naturally into the resume where appropriate - either in a dedicated Skills section or incorporated into experience descriptions.
        Only use these if they genuinely fit with the candidate's background.

        IMPORTANT ABOUT LANGUAGES:
        If the candidate has provided information about languages they speak:
        1. Create a dedicated "Languages" section
        2. List each language with its proficiency level (e.g., "English - Native", "Spanish - Fluent")
        3. Format it consistently with other sections
        4. Place it after the Skills section and before any Additional Information
        """
        
        # Build the user message
        user_message = f"Please create a {resume_style} resume for a {resume_builder_instance.resume_level} level {resume_builder_instance.job_role} position based on the following information:\n\n"
        
        # Add the user information in a structured way
        user_message += f"NAME: {resume_builder_instance.user_data.get('full_name', '')}\n"
        user_message += f"TARGET POSITION: {resume_builder_instance.job_role}\n\n"
        
        # Add all other user data
        for question in resume_builder_instance.questions:
            key = question["key"]
            if key in resume_builder_instance.user_data and resume_builder_instance.user_data[key] and key != 'full_name':
                user_message += f"{question['section'].upper()} - {question['question']}\n{resume_builder_instance.user_data[key]}\n\n"
        
        # Output format instructions
        if resume_format == 'html':
            user_message += f"""
            Please create the resume in HTML format that reflects a {resume_style} style and suitable for a {resume_builder_instance.resume_level} level position.
            Do not include any CSS in the HTML style tags, Keep the empty style tags, the CSS it will be added by other enhancement function.

            fill in the following HTML template with the candidate's information.
            DO NOT modify the structure or class names, only fill in the content based on the information provided:

            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>[CANDIDATE_NAME] - Resume</title>
                <style>
                    /* CSS will be added by enhancement function */
                </style>
            </head>
            <body class="[RESUME_STYLE]">
                <div class="resume-container">
                    <!-- Header Section -->
                    <div class="resume-header">
                        <h1>[CANDIDATE_NAME]</h1>
                        <p class="job-title">[JOB_ROLE]</p>
                    </div>
                    
                    <!-- Contact Information -->
                    <div class="contact-info">
                        <p>[EMAIL] [PHONE] [LOCATION] - Use appropriate separators like | between items if multiple exist</p>
                        <p>[LINKEDIN] [PORTFOLIO] - Include only if provided</p>
                    </div>
                    
                    <!-- Summary Section - Include only if professional summary is provided -->
                    <div class="section" id="summary">
                        <h2>Professional Summary</h2>
                        <div class="summary">
                            <p>[PROFESSIONAL_SUMMARY]</p>
                        </div>
                    </div>
                    
                    <!-- Experience Section - Include only if work experience is provided -->
                    <div class="section" id="experience">
                        <h2>Professional Experience</h2>
                        
                        <!-- For each job position, create a separate experience-item div -->
                        <div class="experience-item">
                            <h3 class="job-position">[POSITION_TITLE] <span class="job-date">[EMPLOYMENT_DATES]</span></h3>
                            <p class="job-company">[COMPANY_NAME], <span class="job-location">[JOB_LOCATION]</span></p>
                            <ul>
                                <li>[RESPONSIBILITY/ACHIEVEMENT 1]</li>
                                <li>[RESPONSIBILITY/ACHIEVEMENT 2]</li>
                                <!-- Add more list items as needed based on the information provided -->
                            </ul>
                        </div>
                        <!-- Repeat experience-item div for each additional job -->
                    </div>
                    
                    <!-- Education Section - Include only if education information is provided -->
                    <div class="section" id="education">
                        <h2>Education</h2>
                        
                        <!-- For each educational qualification, create a separate education-item div -->
                        <div class="education-item">
                            <h3 class="education-degree">[DEGREE_NAME] <span class="education-date">[EDUCATION_DATES]</span></h3>
                            <p class="education-institution">[INSTITUTION_NAME], <span class="education-location">[EDUCATION_LOCATION]</span></p>
                            <!-- Include the following ul only if there are specific education details to mention -->
                            <ul>
                                <li>[EDUCATION_DETAIL_1]</li>
                                <li>[EDUCATION_DETAIL_2]</li>
                            </ul>
                        </div>
                        <!-- Repeat education-item div for each additional education entry -->
                    </div>
                    
                    <!-- Skills Section - Include only if skills are provided -->
                    <div class="section" id="skills">
                        <h2>Skills</h2>
                        <ul class="skills-list">
                            <li>[SKILL_1]</li>
                            <li>[SKILL_2]</li>
                            <!-- Add more skills as provided -->
                        </ul>
                    </div>
                    
                    <!-- Languages Section - Include only if language information is provided -->
                    <div class="section" id="languages">
                        <h2>Languages</h2>
                        <ul>
                            <li>[LANGUAGE_1] - [PROFICIENCY_LEVEL_1]</li>
                            <li>[LANGUAGE_2] - [PROFICIENCY_LEVEL_2]</li>
                            <!-- Add more languages as provided -->
                        </ul>
                    </div>
                    
                    <!-- Additional Information - Include only if additional information is provided -->
                    <div class="section" id="additional">
                        <h2>Additional Information</h2>
                        <p>[ADDITIONAL_INFO]</p>
                    </div>
                </div>
            </body>
            </html>

            ...
            IMPORTANT INSTRUCTIONS:
            1. Replace all placeholder text in [SQUARE_BRACKETS] with actual content from the candidate's information.
            2. COMPLETELY REMOVE any section (including its heading) if no information is provided for that section.
            3. COMPLETELY REMOVE any list items or paragraphs where no information is available.
            4. Do not include placeholder text or section headings for missing information.
            5. Ensure the HTML structure remains valid and properly nested after removing empty sections.
            6. Replace [RESUME_STYLE] with the actual style name: "{resume_style}".
            7. Output only the HTML code exactly as per the template provided. Do not include any additional commentary, explanations, or extra text outside of the HTML structure.
            ...
            
            DO NOT include any placeholders or lorem ipsum text - use only the information provided.
            """
        else:
            user_message += f"""
            Please create the resume in plain text format, formatted to be easily readable. 
            Use markdown-style formatting where helpful (bold, italics, etc.).
            Organize the content with clear section headings and consistent structure.
            """
        
        # Generate the resume with OpenAI
        import openai
        response = openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=4000,
        )
        
        # Get the resume text
        resume_text = response.choices[0].message.content

        # ניקוי תגיות markdown של html אם קיימות
        if resume_format == 'html':
            # הסרת ```html מתחילת הקובץ אם קיים
            if resume_text.strip().startswith("```html"):
                resume_text = resume_text.replace("```html", "", 1).strip()
            
            # הסרת ``` מסוף הקובץ אם קיים
            if resume_text.strip().endswith("```"):
                resume_text = resume_text[:resume_text.rfind("```")].strip()

        
        # במקום לשמור על הדסקטופ, נשמור בקובץ זמני
        temp_dir = tempfile.gettempdir()
        full_path = os.path.join(temp_dir, filename)
    
        # שמירת הקובץ
        with open(full_path, "w", encoding="utf-8") as file:
            file.write(resume_text)
        
        # Enhance HTML if needed
        if resume_format == 'html':
            # Import the required functions
            from main import EnhancedResumeBuilder
            # Create a temporary instance to access the enhancement methods
            temp_builder = EnhancedResumeBuilder()
            # Copy required attributes
            temp_builder.user_data = resume_builder_instance.user_data
            temp_builder.job_role = resume_builder_instance.job_role
            temp_builder.resume_level = resume_builder_instance.resume_level
            # Set the resume style
            temp_builder.resume_style = resume_style
            # Enhance the HTML file
            temp_builder._enhance_html_resume(full_path)

            # שמירת הקובץ לפונקצית התרגום
            with open(full_path, "r", encoding="utf-8") as file:
                resume_content = file.read()
                
            # שמירת התוכן במופע
            resume_builder_instance.resume_content = resume_content
            resume_builder_instance.resume_mime_type = "text/html" if resume_format == 'html' else "text/plain"


            # שמירת שם הקובץ לשימוש מאוחר יותר
            resume_builder_instance.resume_filename = filename
            resume_builder_instance.resume_path = full_path
            resume_builder_instance.resume_format = resume_format
            
            # כאן ישירות נחזיר קישור להורדה
            download_url = f"/download-resume?filename={filename}"
        
        # Generate career tips
        career_tips = [
            f"Tailor your resume for each job application by highlighting the most relevant skills for the position.",
            f"For {resume_builder_instance.job_role} roles, emphasize your measurable achievements with specific metrics and outcomes.",
            f"As a {resume_builder_instance.resume_level} candidate, focus on showcasing your {'leadership and vision' if resume_builder_instance.resume_level == 'executive' else 'growth and progression' if resume_builder_instance.resume_level == 'mid-level' else 'potential and learning ability'}."
        ]
        
        return {
            "status": "success",
            "message": "Resume generated successfully",
            "filename": filename,
            "download_url": download_url,  # הוספת URL להורדה
            "career_tips": career_tips
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating resume: {str(e)}")
    
    # 2. הוספת נקודת קצה חדשה להורדת הקובץ

@app.get("/api/download-resume")
async def download_resume(filename: str = None):
    """
    Download the generated resume file
    """
    global resume_builder_instance
    
    if not resume_builder_instance or not hasattr(resume_builder_instance, 'resume_path'):
        raise HTTPException(status_code=400, detail="No resume has been generated yet")
    
    # קבלת נתיב הקובץ
    resume_path = resume_builder_instance.resume_path
    
    # בדיקה שהקובץ קיים
    if not os.path.exists(resume_path):
        raise HTTPException(status_code=404, detail="Resume file not found")
    
    # קביעת סוג התוכן לפי סוג הקובץ
    content_type = "text/html" if resume_path.endswith('.html') else "text/plain"
    
    # שליחת הקובץ ללקוח כהורדה
    return FileResponse(
        path=resume_path,
        filename=resume_builder_instance.resume_filename,
        media_type=content_type,
        content_disposition_type="attachment"  # מבטיח שהקובץ יורד במקום להיפתח בדפדפן
    )
    

# באקאנד - עדכון הפונקציה translate_resume בקובץ resume_builder_api.py
@app.post("/api/translate-resume")  # בלי /api בתחילה
async def translate_resume(request: TranslationRequest):
    """
    Translate the resume to another language
    """
    global resume_builder_instance
    
    if not resume_builder_instance or not hasattr(resume_builder_instance, 'resume_content'):
        raise HTTPException(status_code=400, detail="No resume has been generated yet")
    
    try:
        # התוכן המקורי של קורות החיים
        original_content = resume_builder_instance.resume_content
        
        # ייצור שם הקובץ המתורגם
        base_filename = os.path.splitext(resume_builder_instance.resume_filename)[0]
        extension = os.path.splitext(resume_builder_instance.resume_filename)[1]
        language_suffix = request.target_language.lower().replace(' ', '')
        translated_filename = f"{base_filename}_{language_suffix}{extension}"
        
        # יצירת הוראות תרגום
        instructions = f"""
        Translate the following resume content to {request.target_language}.
        
        IMPORTANT TRANSLATION RULES:
        1. Maintain the exact same formatting and structure as the original
        2. Preserve all HTML tags exactly as they are (if present)
        3. DO NOT translate the following elements (keep them in their original form):
        - Email addresses and phone numbers
        - Website URLs and social media handles
        - Company names and product names
        - Programming languages, tools, and technical terms
        - Academic degrees (like BSc, BA, MBA, PhD) - only translate their descriptions
        - Personal names
        
        For technical terms in {request.target_language}, use the standard industry terminology.
        """
        
        # קריאה ל-OpenAI API לתרגום
        import openai
        translate_response = openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": original_content}
            ],
            temperature=0.3,
            max_tokens=4000,
        )
        
        # קבלת התוכן המתורגם
        translated_content = translate_response.choices[0].message.content
        
        # טיפול בשפות RTL אם צריך
        rtl_languages = ['hebrew', 'עברית', 'arabic', 'ערבית', 'farsi', 'פרסית', 'urdu', 'אורדו']
        if any(lang in request.target_language.lower() for lang in rtl_languages):
            if extension.lower() == '.html':
                # Add RTL attributes for HTML files
                if '<html' in translated_content:
                    translated_content = translated_content.replace('<html', '<html dir="rtl"', 1)
                
                if '<body' in translated_content:
                    translated_content = translated_content.replace('<body', '<body style="text-align: right; direction: rtl;"', 1)
                
                # If no HTML tags, wrap in RTL HTML
                if '<html' not in translated_content:
                    translated_content = f"""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            direction: rtl;
            text-align: right;
            font-family: 'Arial', 'David', sans-serif;
        }}
        p, div, table, ul, ol {{
            direction: rtl;
            text-align: right;
        }}
    </style>
</head>
<body>
{translated_content}
</body>
</html>"""
                
                # Add RTL CSS
                if '</head>' in translated_content:
                    rtl_css = """
    <style>
        /* RTL specific styles */
        body, p, div, table, ul, ol {
            direction: rtl;
            text-align: right;
        }
        /* Hebrew optimized fonts */
        body {
            font-family: 'Arial', 'David', 'Times New Roman', sans-serif;
        }
    </style>"""
                    translated_content = translated_content.replace('</head>', f'{rtl_css}\n</head>', 1)
            else:
                # For text files, add RTL note
                translated_content = f"<כיוון טקסט מימין לשמאל>\n\n{translated_content}"
        
        # שמירת הגרסה המתורגמת לשימוש מאוחר יותר
        resume_builder_instance.translated_content = translated_content
        resume_builder_instance.translated_filename = translated_filename
        resume_builder_instance.translated_mime_type = resume_builder_instance.resume_mime_type  # אותו סוג כמו המקורי
        
        # ייצור כתובת להורדת הקובץ המתורגם
        download_url = f"/download-translated-resume?filename={translated_filename}"
        
        return {
            "status": "success",
            "message": f"Resume translated to {request.target_language}",
            "translated_filename": translated_filename,
            "download_url": download_url  # הוספת כתובת URL להורדה
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error translating resume: {str(e)}")

# הוספת נקודת קצה להורדת הקובץ המתורגם
@app.get("/api/download-translated-resume")  # בלי /api בתחילה
async def download_translated_resume(filename: str = None):
    """
    Download the translated resume
    """
    global resume_builder_instance
    
    if not resume_builder_instance or not hasattr(resume_builder_instance, 'translated_content'):
        raise HTTPException(status_code=400, detail="No translated resume is available")
    
    try:
        # יצירת תגובה עם התוכן המתורגם
        content = resume_builder_instance.translated_content
        filename = resume_builder_instance.translated_filename
        mime_type = resume_builder_instance.translated_mime_type
        
        # יצירת קובץ זמני
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, filename)
        
        # שמירת התוכן לקובץ זמני
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # שליחת הקובץ להורדה
        return FileResponse(
            path=temp_path,
            filename=filename,
            media_type=mime_type,
            content_disposition_type="attachment"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading translated resume: {str(e)}")
    

@app.get("/")
async def root():
    """
    Root endpoint - just for API testing
    """
    return {"message": "Welcome to the Resume Builder API. The API is up and running!"}

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)