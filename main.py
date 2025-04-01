import os
import json
import time
import random
import openai #For AI Model and abilities
import sys
import textwrap
import re
from dotenv import load_dotenv #For API Secret Key *SECURE*
from fastapi import FastAPI

# Load environment variables and Openai API Key
load_dotenv()

# Get API Key from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY in your .env file")

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

#User - GUI / Interface Style 
class Color:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    PURPLE = '\033[38;5;99m'  # Subtle purple
    DARKCYAN = '\033[38;5;23m'  # Navy blue
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_colored(text, color, bold=False, wrap_width=100):
    """Print text with color and optional formatting"""
    prefix = Color.BOLD if bold else ""
    wrapped_text = textwrap.fill(text, width=wrap_width)
    print(f"{prefix}{color}{wrapped_text}{Color.END}")

def type_text(text, delay=0.01, color=None, bold=False, wrap_width=100):
    """Type out text with a typing effect"""
    if color:
        prefix = Color.BOLD if bold else ""
        prefix += color
        suffix = Color.END
    else:
        prefix = ""
        suffix = ""
    
    wrapped_lines = textwrap.wrap(text, width=wrap_width)
    
    for line in wrapped_lines:
        for char in line:
            print(f"{prefix}{char}{suffix}", end='', flush=True)
            time.sleep(delay)
        print()

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


#תהליך שאלון קורות החיים + יצירת תוצר סופי
class EnhancedResumeBuilder:
    def __init__(self):
        """Initialize the enhanced resume builder system"""
        self.user_data = {}
        self.conversation_history = [
            {"role": "system", "content": "You are a professional career coach and resume expert. Be conversational, supportive, and provide personalized advice."},
        ]
        self.assistant_name = "ResumeBot"
        self.user_name = ""
        self.job_role = ""
        self.resume_level = "junior"  # Default level
        self.questions = []
        self.current_question_index = 0
        self.resume_sections = [
            "Personal Information",
            "Professional Summary",
            "Work Experience",
            "Education",
            "Skills",
            "Languages",
            "Achievements",
            "Projects",
            "Volunteering"
        ]
        
        # Response variety for more human-like interactions
        self.acknowledgments = [
            "I've noted that down.", 
            "Great, thanks for sharing that.",
            "Excellent! I've got that.",
            "Perfect, I'll include that in your resume.",
            "Thanks for the details!",
            "That's really helpful information.",
            "Excellent background to work with.",
            "I've recorded that information.",
            "That will look great on your resume.",
            "Wonderful, that's exactly what I needed to know."
        ]
        
        # Introduction phrases
        self.intro_phrases = [
            "Next, I'd like to ask about",
            "Let's talk about",
            "Now, I'd love to learn about",
            "I'd like to explore",
            "Let's move on to discuss",
            "Could you tell me about",
            "I'm curious about",
            "Let's shift our focus to"
        ]

    def _initialize_questions(self):
        """Create personalized questions based on user's profile"""
        # 4 Basic questions everyone gets
        basic_questions = [
            {"section": "Personal", "key": "email", "question": f"What email address would you like to include on your resume?"},
            {"section": "Personal", "key": "phone", "question": f"What's the best phone number for employers to reach you?"},
            {"section": "Personal", "key": "location", "question": f"Where are you currently located? (City and Country)"},
            {"section": "Personal", "key": "linkedin", "question": f"Do you have a LinkedIn profile you'd like to include? (If so, please share the URL)"},
        ]
        
        # Professional summary approach varies by experience level
        if self.resume_level == "executive":
            summary_question = {"section": "Summary", "key": "summary", 
                               "question": f"As an executive, what would you say are your most significant leadership achievements and management philosophy?"}
        elif self.resume_level == "mid-level":
            summary_question = {"section": "Summary", "key": "summary", 
                               "question": f"What would you say are your key professional strengths and notable accomplishments in your career so far?"}
        else:  # junior
            summary_question = {"section": "Summary", "key": "summary", 
                               "question": f"How would you describe your professional interests and strengths as they relate to {self.job_role}?"}
        
        # Work experience questions - tailored by level and role
        if "developer" in self.job_role.lower() or "engineer" in self.job_role.lower():
            experience_questions = [
                {"section": "Experience", "key": "job_history", 
                "question": f"Could you walk me through your technical experience? For each role, please include:\n- Company name and your title\n- Dates of employment\n- Key technical responsibilities\n- Technologies and tools used\n- Any specific projects or systems you worked on"},
                {"section": "Experience", "key": "achievements", 
                "question": f"What are your most significant technical achievements? Consider:\n- Projects you led or contributed to\n- Performance improvements you implemented\n- Technical challenges you solved\n- Code quality or architecture improvements\n- Any patents or technical innovations"},
                {"section": "Experience", "key": "technical_impact", 
                "question": f"How have you made a technical impact in your roles? For example:\n- Scalability improvements\n- Cost reductions through technical solutions\n- Security enhancements\n- System architecture improvements\n- Team productivity increases"}
            ]
        elif "manager" in self.job_role.lower() or "director" in self.job_role.lower() or "lead" in self.job_role.lower():
            experience_questions = [
                {"section": "Experience", "key": "job_history", 
                "question": f"Could you walk me through your management experience? For each role, please include:\n- Company name and your title\n- Dates of employment\n- Team size and structure\n- Key responsibilities\n- Budget management (if applicable)"},
                {"section": "Experience", "key": "achievements", 
                "question": f"What are your most significant management achievements? Consider:\n- Team growth and development\n- Process improvements\n- Project successes\n- Budget management\n- Strategic initiatives"},
                {"section": "Experience", "key": "leadership_impact", 
                "question": f"How have you made an impact as a leader? For example:\n- Team performance improvements\n- Cultural changes\n- Strategic initiatives\n- Crisis management\n- Cross-functional collaboration"}
            ]
        elif "sales" in self.job_role.lower() or "marketing" in self.job_role.lower():
            experience_questions = [
                {"section": "Experience", "key": "job_history", 
                "question": f"Could you walk me through your sales/marketing experience? For each role, please include:\n- Company name and your title\n- Dates of employment\n- Products/services sold\n- Target market\n- Key responsibilities"},
                {"section": "Experience", "key": "achievements", 
                "question": f"What are your most significant sales/marketing achievements? Consider:\n- Sales targets met/exceeded\n- Campaign successes\n- Market share growth\n- Customer acquisition\n- Revenue impact"},
                {"section": "Experience", "key": "business_impact", 
                "question": f"How have you made a business impact? For example:\n- Revenue growth\n- Market expansion\n- Customer satisfaction\n- Brand development\n- Sales process improvements"}
            ]
        elif ("data" in self.job_role.lower() or "analyst" in self.job_role.lower() or ("data" in self.job_role.lower() and "scientist" in self.job_role.lower())):  
                experience_questions = [
                {"section": "Experience", "key": "job_history", 
                "question": f"Could you walk me through your data analysis experience? For each role, please include:\n- Company name and your title\n- Dates of employment\n- Types of data you analyzed\n- Tools and technologies used\n- Key projects and their scope"},
                {"section": "Experience", "key": "achievements", 
                "question": f"What are your most significant data analysis achievements? Consider:\n- Insights that drove business decisions\n- Models or algorithms you developed\n- Efficiency improvements in data processes\n- Cost savings from data-driven solutions\n- Visualization dashboards that improved understanding"},
                {"section": "Experience", "key": "analytical_impact", 
                "question": f"How have your analyses made an impact? For example:\n- Business strategy influenced by your findings\n- Revenue increase from predictive models\n- Process optimization through data insights\n- Risk mitigation through better analysis\n- Data democratization within the organization"}
            ]
        elif "hr" in self.job_role.lower() or "human resources" in self.job_role.lower():
            experience_questions = [
                {"section": "Experience", "key": "job_history", 
                "question": f"Could you walk me through your HR experience? For each role, please include:\n- Company name and your title\n- Dates of employment\n- Size of organization and workforce\n- HR specialties (recruitment, L&D, compensation, etc.)\n- Key responsibilities and programs managed"},
                {"section": "Experience", "key": "achievements", 
                "question": f"What are your most significant HR achievements? Consider:\n- Recruitment improvements or talent acquisition wins\n- Employee programs you implemented successfully\n- HR metrics improvements (turnover reduction, engagement, etc.)\n- Policy developments or improvements\n- Training or development programs created"},
                {"section": "Experience", "key": "people_impact", 
                "question": f"How have you made an impact on people and culture? For example:\n- Cultural transformations\n- Employee satisfaction improvements\n- Diversity and inclusion initiatives\n- Organizational development successes\n- Change management during transitions"}
            ]
        elif "finance" in self.job_role.lower() or "accountant" in self.job_role.lower() or "financial" in self.job_role.lower() or "accounting" in self.job_role.lower():
            experience_questions = [
                {"section": "Experience", "key": "job_history", 
                "question": f"Could you walk me through your finance experience? For each role, please include:\n- Company name and your title\n- Dates of employment\n- Financial scope (budget size, revenue, etc.)\n- Key financial responsibilities\n- Systems and tools used"},
                {"section": "Experience", "key": "achievements", 
                "question": f"What are your most significant financial achievements? Consider:\n- Cost savings initiatives\n- Financial process improvements\n- Audit outcomes\n- Budget management successes\n- Financial reporting enhancements"},
                {"section": "Experience", "key": "financial_impact", 
                "question": f"How have you made a financial impact? For example:\n- Improved profitability\n- Enhanced financial controls\n- Better financial decision-making processes\n- Risk mitigation strategies\n- Capital structure optimizations"}
            ]
        elif "product" in self.job_role.lower() and ("manager" in self.job_role.lower() or "owner" in self.job_role.lower()):
            experience_questions = [
                {"section": "Experience", "key": "job_history", 
                "question": f"Could you walk me through your product management experience? For each role, please include:\n- Company name and your title\n- Dates of employment\n- Products/services managed\n- Market size and customer base\n- Cross-functional teams you worked with"},
                {"section": "Experience", "key": "achievements", 
                "question": f"What are your most significant product achievements? Consider:\n- Product launches or major releases\n- User/customer growth metrics\n- Revenue impact of products you managed\n- Product improvements that solved user problems\n- Strategic product roadmaps you developed"},
                {"section": "Experience", "key": "product_impact", 
                "question": f"How have your product decisions made an impact? For example:\n- Market share growth\n- Customer satisfaction improvements\n- Platform innovations\n- Competitive advantages created\n- Business model transformations"}
            ]
        elif "ux" in self.job_role.lower() or "ui" in self.job_role.lower() or "designer" in self.job_role.lower():
            experience_questions = [
                {"section": "Experience", "key": "job_history", 
                "question": f"Could you walk me through your design experience? For each role, please include:\n- Company name and your title\n- Dates of employment\n- Products or services you designed for\n- Design tools and methodologies used\n- Team structure and your role within it"},
                {"section": "Experience", "key": "achievements", 
                "question": f"What are your most significant design achievements? Consider:\n- User experience improvements with measurable impact\n- Design systems or patterns you created\n- Usability testing outcomes\n- Product redesigns and their results\n- Design processes you improved or established"},
                {"section": "Experience", "key": "design_impact", 
                "question": f"How have your designs made an impact? For example:\n- Conversion rate improvements\n- User satisfaction or NPS increases\n- Accessibility enhancements\n- Brand perception improvements\n- Efficiency gains through better interfaces"}
            ]
        elif "project" in self.job_role.lower() and "manager" in self.job_role.lower():
            experience_questions = [
                {"section": "Experience", "key": "job_history", 
                "question": f"Could you walk me through your project management experience? For each role, please include:\n- Company name and your title\n- Dates of employment\n- Types and sizes of projects managed\n- Methodologies used (Agile, Waterfall, etc.)\n- Team sizes and budgets"},
                {"section": "Experience", "key": "achievements", 
                "question": f"What are your most significant project management achievements? Consider:\n- Projects delivered on time and under budget\n- Scope or resource challenges overcome\n- Process improvements implemented\n- Risk mitigation successes\n- Stakeholder management wins"},
                {"section": "Experience", "key": "project_impact", 
                "question": f"How have your projects made an impact? For example:\n- Business value delivered\n- Operational efficiency improvements\n- Cost savings or revenue generation\n- Quality improvements\n- Organizational capabilities enhanced"}
            ]
        elif "operations" in self.job_role.lower():
            experience_questions = [
                {"section": "Experience", "key": "job_history", 
                "question": f"Could you walk me through your operations experience? For each role, please include:\n- Company name and your title\n- Dates of employment\n- Operational scope and scale\n- Key processes or systems managed\n- Team size and structure"},
                {"section": "Experience", "key": "achievements", 
                "question": f"What are your most significant operational achievements? Consider:\n- Efficiency improvements\n- Cost reductions\n- Quality enhancements\n- Process standardizations\n- Operational scaling successes"},
                {"section": "Experience", "key": "operational_impact", 
                "question": f"How have your operational improvements made an impact? For example:\n- Improved customer satisfaction\n- Reduced operational risks\n- Enhanced scalability\n- Better resource utilization\n- Increased operational resilience"}
            ]
        elif "customer" in self.job_role.lower() and ("service" in self.job_role.lower() or "success" in self.job_role.lower() or "support" in self.job_role.lower()):
            experience_questions = [
                {"section": "Experience", "key": "job_history", 
                "question": f"Could you walk me through your customer service experience? For each role, please include:\n- Company name and your title\n- Dates of employment\n- Customer base and industries served\n- Support channels managed\n- Team structure and escalation processes"},
                {"section": "Experience", "key": "achievements", 
                "question": f"What are your most significant customer service achievements? Consider:\n- Customer satisfaction or NPS improvements\n- Response time or resolution time enhancements\n- Customer retention increases\n- Support process optimizations\n- Training programs developed"},
                {"section": "Experience", "key": "customer_impact", 
                "question": f"How have you improved customer experiences? For example:\n- Customer journey improvements\n- Self-service initiatives\n- Customer feedback implementation\n- Support channel optimization\n- Customer education programs"}
            ]
        elif "content" in self.job_role.lower() or "writer" in self.job_role.lower() or "copywriter" in self.job_role.lower():
            experience_questions = [
                {"section": "Experience", "key": "job_history", 
                "question": f"Could you walk me through your content creation experience? For each role, please include:\n- Company name and your title\n- Dates of employment\n- Content types and channels\n- Industries or subject areas\n- Audience size and engagement metrics"},
                {"section": "Experience", "key": "achievements", 
                "question": f"What are your most significant content achievements? Consider:\n- High-performing content you created\n- SEO improvements or traffic increases\n- Engagement metrics improvements\n- Brand voice developments\n- Editorial processes you improved"},
                {"section": "Experience", "key": "content_impact", 
                "question": f"How has your content made an impact? For example:\n- Conversion rate improvements\n- Audience growth\n- Brand awareness increases\n- Educational outcomes\n- Lead generation successes"}
            ]
        elif ("consultant" in self.job_role.lower() or "consulting" in self.job_role.lower()):
            experience_questions = [
                {"section": "Experience", "key": "job_history", 
                "question": f"Could you walk me through your consulting experience? For each role, please include:\n- Company name and your title\n- Dates of employment\n- Industries and client types\n- Typical project scope and duration\n- Methodologies or frameworks used"},
                {"section": "Experience", "key": "achievements", 
                "question": f"What are your most significant consulting achievements? Consider:\n- Client problems solved\n- Recommendations implemented successfully\n- ROI delivered to clients\n- Relationship expansions or renewals\n- Innovative solutions developed"},
                {"section": "Experience", "key": "consulting_impact", 
                "question": f"How have your consulting engagements made an impact? For example:\n- Client business outcomes improved\n- Transformational changes implemented\n- Efficiency or cost-saving measures\n- Strategic direction influenced\n- Client capabilities enhanced"}
            ]
        elif "cyber" in self.job_role.lower() or "security" in self.job_role.lower():
            experience_questions = [
                {"section": "Experience", "key": "job_history", 
                "question": f"Could you walk me through your cybersecurity experience? For each role, please include:\n- Company name and your title\n- Dates of employment\n- Security domains (network, application, cloud, etc.)\n- Tools and technologies used\n- Size and complexity of environments secured"},
                {"section": "Experience", "key": "achievements", 
                "question": f"What are your most significant security achievements? Consider:\n- Security incidents prevented or mitigated\n- Compliance achievements\n- Security posture improvements\n- Security awareness programs\n- Risk reduction initiatives"},
                {"section": "Experience", "key": "security_impact", 
                "question": f"How have your security initiatives made an impact? For example:\n- Risk profile improvements\n- Breach prevention metrics\n- Security maturity advancements\n- Cost-effective security solutions\n- Integration of security into business processes"}
            ]
        elif "legal" in self.job_role.lower() or "attorney" in self.job_role.lower() or "lawyer" in self.job_role.lower():
            experience_questions = [
                {"section": "Experience", "key": "job_history", 
                "question": f"Could you walk me through your legal experience? For each role, please include:\n- Organization name and your title\n- Dates of employment\n- Areas of law practiced\n- Types of clients or matters handled\n- Team structure and your reporting relationships"},
                {"section": "Experience", "key": "achievements", 
                "question": f"What are your most significant legal achievements? Consider:\n- Cases or transactions successfully handled\n- Legal risk mitigations\n- Policy or compliance improvements\n- Contract or process optimizations\n- Negotiation outcomes"},
                {"section": "Experience", "key": "legal_impact", 
                "question": f"How have your legal contributions made an impact? For example:\n- Cost savings from legal solutions\n- Business strategy support\n- Dispute resolution successes\n- Improved legal processes\n- Enhanced compliance frameworks"}
            ]
        elif "healthcare" in self.job_role.lower() or "medical" in self.job_role.lower() or "clinical" in self.job_role.lower():
            experience_questions = [
                {"section": "Experience", "key": "job_history", 
                "question": f"Could you walk me through your healthcare experience? For each role, please include:\n- Organization name and your title\n- Dates of employment\n- Clinical or healthcare setting\n- Patient populations served\n- Key responsibilities and specializations"},
                {"section": "Experience", "key": "achievements", 
                "question": f"What are your most significant healthcare achievements? Consider:\n- Patient outcome improvements\n- Healthcare process enhancements\n- Quality of care initiatives\n- Healthcare technology implementations\n- Team development or training programs"},
                {"section": "Experience", "key": "healthcare_impact", 
                "question": f"How have your contributions made an impact on healthcare? For example:\n- Patient satisfaction improvements\n- Care efficiency enhancements\n- Health outcome advancements\n- Cost-effective care solutions\n- Interdisciplinary collaboration successes"}
            ]
        elif "research" in self.job_role.lower() or "scientist" in self.job_role.lower():
            experience_questions = [
                {"section": "Experience", "key": "job_history", 
                "question": f"Could you walk me through your research experience? For each role, please include:\n- Organization name and your title\n- Dates of employment\n- Research areas and topics\n- Methodologies and equipment used\n- Funding sources and project scales"},
                {"section": "Experience", "key": "achievements", 
                "question": f"What are your most significant research achievements? Consider:\n- Key findings or discoveries\n- Publications and citations\n- Grants or funding secured\n- Patents or intellectual property\n- Research collaborations established"},
                {"section": "Experience", "key": "research_impact", 
                "question": f"How has your research made an impact? For example:\n- Industry applications of findings\n- Influence on subsequent research\n- Policy or practice changes\n- Commercial potential realized\n- Public understanding advanced"}
            ]
        elif "teacher" in self.job_role.lower() or "educator" in self.job_role.lower() or "instructor" in self.job_role.lower():
            experience_questions = [
                {"section": "Experience", "key": "job_history", 
                "question": f"Could you walk me through your teaching experience? For each role, please include:\n- Institution name and your title\n- Dates of employment\n- Subjects and grade levels taught\n- Class sizes and demographics\n- Teaching methodologies used"},
                {"section": "Experience", "key": "achievements", 
                "question": f"What are your most significant teaching achievements? Consider:\n- Student performance improvements\n- Curriculum developments or enhancements\n- Teaching innovations implemented\n- Recognition or awards received\n- Extracurricular programs developed"},
                {"section": "Experience", "key": "educational_impact", 
                "question": f"How have your teaching methods made an impact? For example:\n- Student engagement improvements\n- Learning outcome advancements\n- Educational technology implementations\n- Parent or community involvement\n- Student success stories"}
            ]
        else:
            experience_questions = [
                {"section": "Experience", "key": "job_history", 
                 "question": f"Could you tell me about your relevant work experience? For each position, please include:\n- Company name and your title\n- Dates of employment\n- Key responsibilities\n- Notable projects or initiatives"},
                {"section": "Experience", "key": "achievements", 
                 "question": f"What specific achievements or projects are you most proud of? Think about:\n- Times you solved problems\n- Process improvements\n- Team contributions\n- Customer impact\n- Business results"},
                {"section": "Experience", "key": "professional_impact", 
                 "question": f"How have you made an impact in your roles? For example:\n- Process improvements\n- Cost savings\n- Customer satisfaction\n- Team efficiency\n- Business growth"}
            ]
        
        # Education questions - tailored by level
        if self.resume_level == "executive":
            education_questions = [
                {"section": "Education", "key": "education", 
                 "question": f"What's your educational background? Please include:\n- Degrees earned\n- Institutions attended\n- Graduation dates\n- Relevant coursework\n- Academic achievements\n- Leadership roles in academic organizations"},
                {"section": "Education", "key": "certifications", 
                 "question": f"What professional certifications or advanced training do you have? Include:\n- Industry certifications\n- Executive education programs\n- Leadership training\n- Technical certifications\n- Board certifications"}
            ]
        elif self.resume_level == "mid-level":
            education_questions = [
                {"section": "Education", "key": "education", 
                 "question": f"What's your educational background? Please include:\n- Degrees earned\n- Institutions attended\n- Graduation dates\n- Relevant coursework\n- Academic achievements"},
                {"section": "Education", "key": "certifications", 
                 "question": f"What professional certifications or training do you have? Include:\n- Industry certifications\n- Professional development courses\n- Technical certifications\n- Management training"}
            ]
        else:  # junior
            education_questions = [
                {"section": "Education", "key": "education", 
                 "question": f"What's your educational background? Please include:\n- Degrees earned\n- Institutions attended\n- Graduation dates\n- Relevant coursework\n- Academic achievements\n- GPA (if above 3.5)"},
                {"section": "Education", "key": "certifications", 
                 "question": f"Do you have any relevant certifications or training? Include:\n- Industry certifications\n- Online courses\n- Technical certifications\n- Internship programs"}
            ]
        
        # Skills questions - tailored by role and level
        if "developer" in self.job_role.lower() or "engineer" in self.job_role.lower() or "proggramer" in self.job_role.lower():
            skills_questions = [
                {"section": "Skills", "key": "technical_skills", 
                "question": f"What technical skills do you have? Please include:\n- Programming languages\n- Frameworks and libraries\n- Databases and tools\n- Development methodologies\n- Cloud platforms\n- Version control systems\n- Testing frameworks"},
                {"section": "Skills", "key": "soft_skills", 
                "question": f"What professional skills do you have? Consider:\n- Problem-solving approaches\n- Team collaboration\n- Code review experience\n- Documentation skills\n- Agile methodologies\n- Technical communication"},
                {"section": "Skills", "key": "domain_knowledge", 
                "question": f"What domain knowledge do you have? Include:\n- Industry expertise\n- Domain-specific tools\n- Regulatory knowledge\n- Security practices\n- Performance optimization"}
            ]
        elif "manager" in self.job_role.lower() or "director" in self.job_role.lower() or "lead" in self.job_role.lower():
            skills_questions = [
                {"section": "Skills", "key": "leadership_skills", 
                "question": f"What leadership and management skills do you have? Include:\n- Team management\n- Strategic planning\n- Budget management\n- Change management\n- Conflict resolution\n- Performance management"},
                {"section": "Skills", "key": "technical_skills", 
                "question": f"What technical knowledge do you have? Include:\n- Industry expertise\n- Technical concepts\n- Tools and systems\n- Project management\n- Risk management"},
                {"section": "Skills", "key": "business_skills", 
                "question": f"What business skills do you have? Consider:\n- Strategic thinking\n- Business analysis\n- Financial management\n- Stakeholder management\n- Process improvement"}
            ]
        elif ("data" in self.job_role.lower() or "analyst" in self.job_role.lower() or ("data" in self.job_role.lower() and "scientist" in self.job_role.lower())):  
            skills_questions = [
                {"section": "Skills", "key": "technical_skills", 
                "question": f"What technical skills do you have? Please include:\n- Programming languages (Python, R, SQL, etc.)\n- Data visualization tools (Tableau, Power BI, etc.)\n- Statistical analysis methods\n- Machine learning libraries/frameworks\n- Database systems\n- Big data technologies\n- Data processing tools"},
                {"section": "Skills", "key": "analytical_skills", 
                "question": f"What analytical skills do you have? Consider:\n- Statistical analysis\n- Predictive modeling\n- Data mining techniques\n- A/B testing\n- Experiment design\n- Hypothesis testing\n- Pattern recognition"},
                {"section": "Skills", "key": "domain_knowledge", 
                "question": f"What domain knowledge do you have? Include:\n- Industry expertise\n- Business metrics understanding\n- Data governance knowledge\n- Privacy regulations\n- Ethics in data analysis\n- Industry-specific data challenges"}
            ]
        elif "marketing" in self.job_role.lower():
            skills_questions = [
                {"section": "Skills", "key": "marketing_skills", 
                "question": f"What marketing skills do you have? Please include:\n- Digital marketing channels\n- Campaign management\n- Content creation\n- Marketing automation tools\n- SEO/SEM expertise\n- Social media platforms\n- Email marketing"},
                {"section": "Skills", "key": "analytical_skills", 
                "question": f"What analytical skills do you have? Consider:\n- Marketing metrics tracking\n- Campaign performance analysis\n- Conversion optimization\n- A/B testing\n- Customer segmentation\n- ROI calculation\n- Google Analytics expertise"},
                {"section": "Skills", "key": "creative_skills", 
                "question": f"What creative and strategic skills do you have? Include:\n- Brand development\n- Storytelling\n- Market research\n- Customer journey mapping\n- Positioning strategy\n- Competitive analysis\n- Customer insight development"}
            ]
        elif "sales" in self.job_role.lower():
            skills_questions = [
                {"section": "Skills", "key": "sales_skills", 
                "question": f"What sales skills do you have? Please include:\n- Sales methodologies\n- Client relationship management\n- Negotiation techniques\n- Pipeline management\n- Sales tools (CRM, etc.)\n- Territory management\n- Closing strategies"},
                {"section": "Skills", "key": "business_skills", 
                "question": f"What business and analytical skills do you have? Consider:\n- Market analysis\n- Competitive intelligence\n- Sales forecasting\n- Performance metrics tracking\n- Strategic account planning\n- Pricing strategies\n- Value proposition development"},
                {"section": "Skills", "key": "communication_skills", 
                "question": f"What communication and interpersonal skills do you have? Include:\n- Presentation skills\n- Relationship building\n- Active listening\n- Objection handling\n- Customer needs assessment\n- Cross-functional collaboration\n- Team selling"}
            ]
        elif "hr" in self.job_role.lower() or "human resources" in self.job_role.lower():
            skills_questions = [
                {"section": "Skills", "key": "hr_skills", 
                "question": f"What HR skills do you have? Please include:\n- Recruitment and selection\n- Employee relations\n- Performance management\n- Policy development\n- Compensation and benefits\n- Training and development\n- HRIS systems"},
                {"section": "Skills", "key": "compliance_skills", 
                "question": f"What compliance and regulatory knowledge do you have? Consider:\n- Labor laws\n- Employment legislation\n- Health and safety regulations\n- Equal opportunity requirements\n- Benefits compliance\n- Records management\n- Risk mitigation strategies"},
                {"section": "Skills", "key": "people_skills", 
                "question": f"What people management and strategic skills do you have? Include:\n- Conflict resolution\n- Organizational development\n- Change management\n- Employee engagement\n- Talent management\n- Succession planning\n- Culture development"}
            ]
        elif "finance" in self.job_role.lower() or "accountant" in self.job_role.lower() or "financial" in self.job_role.lower():
            skills_questions = [
                {"section": "Skills", "key": "finance_skills", 
                "question": f"What finance and accounting skills do you have? Please include:\n- Financial reporting\n- Budgeting and forecasting\n- Financial analysis\n- Accounting principles\n- Taxation knowledge\n- Audit procedures\n- Financial software systems"},
                {"section": "Skills", "key": "technical_skills", 
                "question": f"What technical and regulatory knowledge do you have? Consider:\n- Accounting standards (GAAP, IFRS)\n- Regulatory compliance\n- Risk management\n- Internal controls\n- Financial modeling\n- ERP systems\n- Data analysis tools"},
                {"section": "Skills", "key": "business_skills", 
                "question": f"What business and strategic skills do you have? Include:\n- Business partnership\n- Strategic planning\n- Process improvement\n- Decision support\n- Performance metrics\n- Cost management\n- Investment analysis"}
            ]
        elif "product" in self.job_role.lower() and ("manager" in self.job_role.lower() or "owner" in self.job_role.lower()):
            skills_questions = [
                {"section": "Skills", "key": "product_skills", 
                "question": f"What product management skills do you have? Please include:\n- Product lifecycle management\n- Market research\n- User story development\n- Roadmap planning\n- Requirements gathering\n- Product strategy\n- Competitive analysis"},
                {"section": "Skills", "key": "technical_skills", 
                "question": f"What technical and analytical skills do you have? Consider:\n- Product metrics\n- A/B testing\n- User analytics\n- Agile methodologies\n- Product development tools\n- Data analysis\n- Technical documentation"},
                {"section": "Skills", "key": "business_skills", 
                "question": f"What business and leadership skills do you have? Include:\n- Cross-functional team leadership\n- Stakeholder management\n- Go-to-market strategy\n- Pricing strategy\n- Value proposition development\n- Customer journey mapping\n- Business case development"}
            ]
        elif "ux" in self.job_role.lower() or "ui" in self.job_role.lower() or "designer" in self.job_role.lower():
            skills_questions = [
                {"section": "Skills", "key": "design_skills", 
                "question": f"What design skills do you have? Please include:\n- UX/UI design tools\n- Design principles\n- Wireframing\n- Prototyping\n- Visual design\n- Information architecture\n- Interaction design"},
                {"section": "Skills", "key": "research_skills", 
                "question": f"What research and analytical skills do you have? Consider:\n- User research methods\n- Usability testing\n- Heuristic evaluation\n- Persona development\n- Journey mapping\n- A/B testing\n- Accessibility evaluation"},
                {"section": "Skills", "key": "technical_skills", 
                "question": f"What technical and collaboration skills do you have? Include:\n- Design systems\n- Developer collaboration\n- Front-end knowledge (HTML/CSS)\n- Design documentation\n- Stakeholder presentation\n- Design thinking\n- Product strategy"}
            ]
        elif "project" in self.job_role.lower() and "manager" in self.job_role.lower():
            skills_questions = [
                {"section": "Skills", "key": "pm_skills", 
                "question": f"What project management skills do you have? Please include:\n- Project methodologies (Agile, Waterfall, etc.)\n- Project scheduling\n- Resource management\n- Risk management\n- Budget planning\n- Stakeholder management\n- Project documentation"},
                {"section": "Skills", "key": "technical_skills", 
                "question": f"What technical and tool-based skills do you have? Consider:\n- PM software (JIRA, MS Project, etc.)\n- Reporting tools\n- Documentation systems\n- Collaboration platforms\n- Process mapping\n- Technical understanding\n- Quality assurance methods"},
                {"section": "Skills", "key": "leadership_skills", 
                "question": f"What leadership and communication skills do you have? Include:\n- Team leadership\n- Conflict resolution\n- Executive communication\n- Client management\n- Change management\n- Decision-making\n- Meeting facilitation"}
            ]
        elif "operations" in self.job_role.lower():
            skills_questions = [
                {"section": "Skills", "key": "operations_skills", 
                "question": f"What operations management skills do you have? Please include:\n- Process optimization\n- Quality management\n- Supply chain knowledge\n- Resource allocation\n- Logistics management\n- Inventory control\n- Operational metrics"},
                {"section": "Skills", "key": "technical_skills", 
                "question": f"What technical and analytical skills do you have? Consider:\n- Operations software\n- Data analysis\n- KPI development\n- ERP systems\n- Forecasting\n- Capacity planning\n- Cost analysis"},
                {"section": "Skills", "key": "leadership_skills", 
                "question": f"What leadership and strategic skills do you have? Include:\n- Cross-functional collaboration\n- Vendor management\n- Continuous improvement\n- Strategic planning\n- Team development\n- Crisis management\n- Change implementation"}
            ]
        elif "customer" in self.job_role.lower() and ("service" in self.job_role.lower() or "success" in self.job_role.lower() or "support" in self.job_role.lower()):
            skills_questions = [
                {"section": "Skills", "key": "customer_skills", 
                "question": f"What customer service skills do you have? Please include:\n- Client communication\n- Problem resolution\n- Customer needs assessment\n- Service recovery\n- Account management\n- Product knowledge\n- Customer experience enhancement"},
                {"section": "Skills", "key": "technical_skills", 
                "question": f"What technical and systems skills do you have? Consider:\n- CRM systems\n- Ticketing systems\n- Knowledge bases\n- Communication tools\n- Analysis and reporting\n- Service metrics tracking\n- Process documentation"},
                {"section": "Skills", "key": "business_skills", 
                "question": f"What business and strategic skills do you have? Include:\n- Customer retention strategies\n- Upselling/cross-selling\n- Voice of customer programs\n- Service level management\n- Quality assurance\n- Team collaboration\n- Process improvement"}
            ]
        elif "content" in self.job_role.lower() or "writer" in self.job_role.lower() or "copywriter" in self.job_role.lower():
            skills_questions = [
                {"section": "Skills", "key": "writing_skills", 
                "question": f"What writing and content creation skills do you have? Please include:\n- Content types (blogs, whitepapers, etc.)\n- Copywriting\n- Editing and proofreading\n- SEO writing\n- Storytelling\n- Research methods\n- Style guide adaptation"},
                {"section": "Skills", "key": "technical_skills", 
                "question": f"What technical and tool-based skills do you have? Consider:\n- CMS platforms\n- SEO tools\n- Content planning software\n- Analytics tools\n- Design software\n- Collaboration platforms\n- Social media management"},
                {"section": "Skills", "key": "strategic_skills", 
                "question": f"What strategic and planning skills do you have? Include:\n- Content strategy\n- Editorial calendar management\n- Audience analysis\n- Brand voice development\n- Content performance analysis\n- Stakeholder management\n- Project management"}
            ]
        elif ("consultant" in self.job_role.lower() or "consulting" in self.job_role.lower()):
            skills_questions = [
                {"section": "Skills", "key": "consulting_skills", 
                "question": f"What consulting and advisory skills do you have? Please include:\n- Problem identification\n- Solution development\n- Client management\n- Project methodology\n- Industry expertise\n- Workshop facilitation\n- Change management"},
                {"section": "Skills", "key": "analytical_skills", 
                "question": f"What analytical and research skills do you have? Consider:\n- Business analysis\n- Market research\n- Data analysis\n- Needs assessment\n- ROI calculation\n- Process mapping\n- Competitive analysis"},
                {"section": "Skills", "key": "communication_skills", 
                "question": f"What communication and presentation skills do you have? Include:\n- Executive presentations\n- Report writing\n- Proposal development\n- Stakeholder management\n- Negotiation\n- Complex concept explanation\n- Client relationship building"}
            ]
        elif "cyber" in self.job_role.lower() or "security" in self.job_role.lower():
            skills_questions = [
                {"section": "Skills", "key": "security_skills", 
                "question": f"What cybersecurity skills do you have? Please include:\n- Security frameworks\n- Threat detection\n- Vulnerability assessment\n- Security tools\n- Incident response\n- Penetration testing\n- Security architecture"},
                {"section": "Skills", "key": "technical_skills", 
                "question": f"What technical skills do you have? Consider:\n- Network security\n- Cloud security\n- Security coding practices\n- Operating systems\n- Security automation\n- Forensic analysis\n- Cryptography"},
                {"section": "Skills", "key": "compliance_skills", 
                "question": f"What governance and compliance skills do you have? Include:\n- Security policies\n- Regulatory compliance\n- Risk assessment\n- Security awareness training\n- Audit management\n- Documentation\n- Security operations"}
            ]
        elif "legal" in self.job_role.lower() or "attorney" in self.job_role.lower() or "lawyer" in self.job_role.lower():
            skills_questions = [
                {"section": "Skills", "key": "legal_skills", 
                "question": f"What legal skills do you have? Please include:\n- Practice areas\n- Case management\n- Legal research\n- Document drafting\n- Negotiation\n- Client counseling\n- Regulatory knowledge"},
                {"section": "Skills", "key": "technical_skills", 
                "question": f"What technical and analytical skills do you have? Consider:\n- Legal software\n- eDiscovery tools\n- Legal databases\n- Compliance management\n- Contract analysis\n- Risk assessment\n- Legal writing"},
                {"section": "Skills", "key": "business_skills", 
                "question": f"What business and professional skills do you have? Include:\n- Client development\n- Case strategy\n- Project management\n- Cross-functional collaboration\n- Business acumen\n- Ethics compliance\n- Professional networking"}
            ]
        elif "healthcare" in self.job_role.lower() or "medical" in self.job_role.lower() or "clinical" in self.job_role.lower():
            skills_questions = [
                {"section": "Skills", "key": "clinical_skills", 
                "question": f"What clinical or healthcare skills do you have? Please include:\n- Clinical procedures\n- Patient care\n- Medical specialties\n- Health assessments\n- Treatment planning\n- Medical technology\n- Clinical documentation"},
                {"section": "Skills", "key": "technical_skills", 
                "question": f"What technical and administrative skills do you have? Consider:\n- Healthcare systems\n- Electronic health records\n- Medical coding\n- Regulatory compliance\n- Quality assurance\n- Healthcare analytics\n- Privacy protocols"},
                {"section": "Skills", "key": "professional_skills", 
                "question": f"What professional and interpersonal skills do you have? Include:\n- Patient communication\n- Interdisciplinary collaboration\n- Healthcare education\n- Ethical decision-making\n- Crisis management\n- Continuous learning\n- Compassionate care"}
            ]
        elif "research" in self.job_role.lower() or "scientist" in self.job_role.lower():
            skills_questions = [
                {"section": "Skills", "key": "research_skills", 
                "question": f"What research skills do you have? Please include:\n- Research methodologies\n- Experimental design\n- Data collection\n- Statistical analysis\n- Literature review\n- Research tools\n- Publication experience"},
                {"section": "Skills", "key": "technical_skills", 
                "question": f"What technical and analytical skills do you have? Consider:\n- Laboratory techniques\n- Specialized equipment\n- Data analysis software\n- Programming languages\n- Visualization tools\n- Documentation systems\n- Research protocols"},
                {"section": "Skills", "key": "professional_skills", 
                "question": f"What professional and collaboration skills do you have? Include:\n- Grant writing\n- Research presentation\n- Peer review\n- Team collaboration\n- Project management\n- Ethical research practices\n- Interdisciplinary communication"}
            ]
        elif "teacher" in self.job_role.lower() or "educator" in self.job_role.lower() or "instructor" in self.job_role.lower():
            skills_questions = [
                {"section": "Skills", "key": "teaching_skills", 
                "question": f"What teaching and instructional skills do you have? Please include:\n- Teaching methodologies\n- Curriculum development\n- Lesson planning\n- Student assessment\n- Classroom management\n- Educational technology\n- Differentiated instruction"},
                {"section": "Skills", "key": "subject_skills", 
                "question": f"What subject matter expertise do you have? Consider:\n- Subject areas\n- Specialized knowledge\n- Curriculum standards\n- Resource development\n- Interdisciplinary connections\n- Current research\n- Industry applications"},
                {"section": "Skills", "key": "professional_skills", 
                "question": f"What professional and interpersonal skills do you have? Include:\n- Student engagement\n- Parent communication\n- Collaborative teaching\n- Professional development\n- Educational leadership\n- Cultural competence\n- Special needs accommodation"}
            ]
        else:
            skills_questions = [
                {"section": "Skills", "key": "technical_skills", 
                "question": f"What specific skills do you have that are relevant to {self.job_role}? Include:\n- Technical skills\n- Industry knowledge\n- Tools and systems\n- Methodologies\n- Best practices"},
                {"section": "Skills", "key": "soft_skills", 
                "question": f"What professional skills do you have? Consider:\n- Communication\n- Problem-solving\n- Teamwork\n- Organization\n- Adaptability\n- Customer service"}
            ]

            
        # Languages skills - tailored by role
        if "international" in self.job_role.lower() or "global" in self.job_role.lower():
            languages_question = {"section": "Skills", "key": "languages", 
                                "question": f"What languages do you speak? For each language, please include:\n- Language name\n- Proficiency level (Native, Fluent, Advanced, Intermediate, Basic)\n- Any relevant certifications\n- Experience using the language in a professional context"}
        else:
            languages_question = {"section": "Skills", "key": "languages", 
                                "question": f"What languages do you speak, and at what proficiency level?"}
        
        # Additional questions - tailored by level and role
        if self.resume_level == "executive":
            additional_questions = [
                {"section": "Additional", "key": "board_positions", 
                 "question": f"Have you served on any boards or in advisory roles? Include:\n- Organization name\n- Role and duration\n- Key contributions\n- Strategic initiatives\n- Industry impact"},
                {"section": "Additional", "key": "speaking", 
                 "question": f"Have you done any speaking engagements or published work? Include:\n- Conferences and events\n- Publications\n- Media appearances\n- Industry panels\n- Thought leadership content"},
                {"section": "Additional", "key": "industry_leadership", 
                 "question": f"How have you demonstrated industry leadership? Consider:\n- Industry associations\n- Professional organizations\n- Mentoring programs\n- Industry initiatives\n- Thought leadership"}
            ]
        elif self.resume_level == "mid-level":
            additional_questions = [
                {"section": "Additional", "key": "projects", 
                 "question": f"Have you worked on any noteworthy projects? Include:\n- Project scope\n- Your role\n- Key achievements\n- Technical challenges\n- Business impact"},
                {"section": "Additional", "key": "professional_activities", 
                 "question": f"Have you participated in any professional activities? Include:\n- Professional organizations\n- Industry events\n- Training programs\n- Mentoring\n- Community involvement"},
                {"section": "Additional", "key": "industry_contributions", 
                 "question": f"How have you contributed to your industry? Consider:\n- Knowledge sharing\n- Process improvements\n- Best practices\n- Team development\n- Industry initiatives"}
            ]
        else:  # junior
            additional_questions = [
                {"section": "Additional", "key": "projects", 
                 "question": f"Have you worked on any academic or personal projects? Include:\n- Project description\n- Your role\n- Technologies used\n- Key achievements\n- Learning outcomes"},
                {"section": "Additional", "key": "activities", 
                 "question": f"What extracurricular activities have you participated in? Include:\n- Student organizations\n- Volunteer work\n- Internships\n- Academic clubs\n- Community involvement"},
                {"section": "Additional", "key": "achievements", 
                 "question": f"What other achievements would you like to highlight? Consider:\n- Academic awards\n- Competition wins\n- Personal projects\n- Community service\n- Leadership roles"}
            ]
            
        # Final catch-all question
        final_question = {"section": "Additional", "key": "additional_info", 
                         "question": f"Is there anything else you'd like to include on your resume that we haven't covered yet? Consider:\n- Unique experiences\n- Special achievements\n- Relevant hobbies\n- Industry-specific certifications\n- Notable accomplishments"}
        
        # Combine all questions in a logical order
        combined_questions = basic_questions + [summary_question] + experience_questions + education_questions + skills_questions + [languages_question] + additional_questions + [final_question]
        
        return combined_questions

    def welcome(self):
        """Display a welcome message and start the conversation"""
        clear_screen()
        print_colored("\n" + "=" * 80, Color.BLUE)
        print_colored(f"{' ' * 25}INTERACTIVE RESUME BUILDER", Color.BLUE, bold=True)
        print_colored("=" * 80 + "\n", Color.BLUE)
        
        time.sleep(0.5)
        type_text("Hi there! I'm your personal resume assistant. I'll help you create a professional, tailored resume through a friendly conversation.", delay=0.01, color=Color.GREEN)
        time.sleep(0.5)
        
        print()
        type_text("First, I'd like to get to know you a bit better.", delay=0.01, color=Color.CYAN)
        time.sleep(0.3)
        
        self.user_name = input(f"\n{Color.YELLOW}What's your name? {Color.END}")
        self.user_data["full_name"] = self.user_name
        print()
        
        type_text(f"Great to meet you, {self.user_name}! I'm excited to help you create an impressive resume.", delay=0.01, color=Color.GREEN)
        
        print()
        self.job_role = input(f"{Color.YELLOW}What job role are you targeting with this resume? {Color.END}")
        print()

        type_text(f"Perfect! A resume for a {self.job_role} position. Let's make it stand out.", delay=0.01, color=Color.GREEN)
        
        # Determine experience level
        print()
        experience_response = input(f"{Color.YELLOW}How would you describe your career stage? (Entry-level/Junior, Mid-level, or Executive/Senior) {Color.END}")
        print()
        
        if "entry" in experience_response.lower() or "junior" in experience_response.lower() or "start" in experience_response.lower():
            self.resume_level = "junior"
            type_text("Got it! I'll focus on highlighting your potential, education, and relevant skills for an entry-level position.", delay=0.01, color=Color.GREEN)
        elif "mid" in experience_response.lower() or "intermediate" in experience_response.lower():
            self.resume_level = "mid-level"
            type_text("Great! For mid-level positions, we'll emphasize your achievements, growth, and the impact you've made in previous roles.", delay=0.01, color=Color.GREEN)
        elif "exec" in experience_response.lower() or "senior" in experience_response.lower() or "lead" in experience_response.lower():
            self.resume_level = "executive"
            type_text("Excellent! For executive positions, we'll focus on your leadership accomplishments, strategic vision, and business impact.", delay=0.01, color=Color.GREEN)
        else:
            self.resume_level = "mid-level"  # Default to mid-level if unclear
            type_text("I'll prepare a resume that highlights your experience and skills for this position.", delay=0.01, color=Color.GREEN)
        
        # Initialize questions based on the user's profile
        self.questions = self._initialize_questions()
        
        # Transition to the main interview
        print()
        print()
        type_text(f"Now, let's gather all the information needed for your {self.job_role} resume. I'll guide you through a series of questions.", delay=0.01, color=Color.CYAN)
        print()
        type_text("Feel free to provide as much detail as you'd like. You can also type 'skip' to move past any question, or 'done' when you're ready to finish and generate your resume.", delay=0.01, color=Color.CYAN)
        time.sleep(1)
        print("\n")
        self._interview_process()

    def _interview_process(self):
        """Conduct an interactive interview to gather resume information"""
        total_questions = len(self.questions)
        while self.current_question_index < total_questions:
            question_data = self.questions[self.current_question_index]
            question = question_data["question"]
            key = question_data["key"]
            
            # Create a personalized introduction for the question
            intro = random.choice(self.intro_phrases)
            
            # Display the question with numbering
            print_colored(f"Question {self.current_question_index + 1} of {total_questions}:", Color.BLUE, bold=True)
            print_colored(f"{intro} {question.lower()}", Color.CYAN)
            
            # Get user input
            print()
            answer = input(f"{Color.YELLOW}> {Color.END}")
            print()
            
            # Validate email if that's the current question
            if key == 'email' and answer.strip():
                if not validate_email(answer.strip()):
                    type_text("I notice that's not a valid email address. Please try again with a valid email format.", delay=0.01, color=Color.RED)
                    continue
            
            # Check for exit command
            if answer.lower() in ['done', 'exit', 'finish', 'quit']:
                type_text("Great! I think we have enough information to create your resume now.", delay=0.01, color=Color.GREEN)
                break
            
            # Check for skip command
            if answer.lower() in ['skip', 's', 'pass']:
                type_text(random.choice([
                    "No problem, we can move on.",
                    "Sure, let's skip that one.",
                    "That's fine, we'll continue with the next question."
                ]), delay=0.01, color=Color.GREEN)
                self.current_question_index += 1
                print()
                continue
            
            # Process the answer
            if answer.strip():
                # Save the answer
                self.user_data[key] = answer.strip()
                
                # Add to conversation history
                self.conversation_history.append({"role": "user", "content": answer.strip()})
                
                # Provide a varied acknowledgment
                type_text(random.choice(self.acknowledgments), delay=0.01, color=Color.GREEN)
                print()
                
                # Special handling for LinkedIn question
                if key == 'linkedin':
                    if answer.lower() in ['no', 'n', 'none', '', 'dont have one', "don't have one", 'dont have', "don't have"]:
                        print()
                        type_text("Quick follow-up:", delay=0.01, color=Color.YELLOW)
                        type_text("Do you have any other professional social media profiles you'd like to include? (e.g., GitHub, portfolio website)", delay=0.01, color=Color.YELLOW)
                        print()
                        
                        social_answer = input(f"{Color.YELLOW}> {Color.END}")
                        if social_answer.strip():
                            self.user_data[key] = f"LinkedIn: Not provided\nOther profiles: {social_answer.strip()}"
                            type_text("Thanks for the additional information!", delay=0.01, color=Color.GREEN)
                            print()
                
                # Special handling for location question
                if key == 'location':
                    print()
                    type_text("Quick follow-up:", delay=0.01, color=Color.YELLOW)
                    type_text("What is your preferred work arrangement? (Remote, Hybrid, On-site, or No preference)", delay=0.01, color=Color.YELLOW)
                    print()
                    
                    work_pref_answer = input(f"{Color.YELLOW}> {Color.END}")
                    if work_pref_answer.strip():
                        self.user_data[key] = f"Location: {answer.strip()}\nWork Arrangement: {work_pref_answer.strip()}"
                        type_text("Thanks for specifying your work arrangement preference!", delay=0.01, color=Color.GREEN)
                        print()
                
                # Check for follow-up questions
                self._check_for_follow_up(key, answer)
                
                # Get AI feedback for all responses except basic info
                if key not in ['full_name', 'email', 'phone', 'location']:
                    self._provide_feedback(key, answer)
            else:
                type_text("I notice you didn't provide an answer. Let's try again or type 'skip' to move on.", delay=0.01, color=Color.YELLOW)
                continue
            
            # Move to the next question
            self.current_question_index += 1
            time.sleep(0.5)
            print()
        
        # After gathering information, offer to edit answers
        if any(self.user_data.values()):
            self._offer_edit_answers()
            self._generate_resume()
        else:
            type_text("I don't have enough information to create a resume. Please run the program again when you're ready to provide more details.", delay=0.01, color=Color.RED)

    def _offer_edit_answers(self):
        """Offer the user a chance to edit their answers before generating the resume"""
        print()
        print_colored("=" * 80, Color.BLUE)
        print_colored(f"{' ' * 25}REVIEW YOUR ANSWERS", Color.BLUE, bold=True)
        print_colored("=" * 80, Color.BLUE)
        print()
        
        type_text("Before we create your resume, would you like to review and edit any of your answers?", delay=0.01, color=Color.CYAN)
        print()
        
        edit_choice = input(f"{Color.YELLOW}Would you like to edit any answers? (yes/no) {Color.END}")
        
        if edit_choice.lower() in ['no', 'n', 'done']:
            print()
            type_text("Great! Let's proceed with creating your resume.", delay=0.01, color=Color.GREEN)
            return
            
        if edit_choice.lower() not in ['yes', 'y']:
            type_text("Please enter 'yes' or 'no'.", delay=0.01, color=Color.RED)
            return
            
        while True:
            # Display all answers with numbers
            print()
            print_colored("Your current answers:", Color.CYAN, bold=True)
            print()
            
            for i, (key, value) in enumerate(self.user_data.items(), 1):
                # Get the question for this key
                question = next((q["question"] for q in self.questions if q["key"] == key), key)
                print_colored(f"{i}. {question}", Color.BLUE)
                print_colored(f"   Current answer: {value}", Color.DARKCYAN)
                print()
            
            # Get which answer to edit
            while True:
                try:
                    edit_num = input(f"{Color.YELLOW}Which answer would you like to edit? (Enter the number, or 'done' to finish) {Color.END}")
                    if edit_num.lower() in ['done', 'd']:
                        break
                        
                    edit_num = int(edit_num)
                    if 1 <= edit_num <= len(self.user_data):
                        # Get the key for the selected number
                        key_to_edit = list(self.user_data.keys())[edit_num - 1]
                        question = next((q["question"] for q in self.questions if q["key"] == key_to_edit), key_to_edit)
                        
                        # Get the new answer
                        print()
                        print_colored(f"Current answer: {self.user_data[key_to_edit]}", Color.DARKCYAN)
                        new_answer = input(f"{Color.YELLOW}Enter your new answer: {Color.END}")
                        
                        if new_answer.strip():
                            # Update the answer
                            self.user_data[key_to_edit] = new_answer.strip()
                            
                            # Update conversation history
                            for msg in self.conversation_history:
                                if msg["role"] == "user" and msg["content"] == self.user_data.get(key_to_edit, ""):
                                    msg["content"] = new_answer.strip()
                                    break
                            
                            type_text("Answer updated successfully!", delay=0.01, color=Color.GREEN)
                        else:
                            type_text("No changes made.", delay=0.01, color=Color.YELLOW)
                        break
                    else:
                        type_text("Please enter a valid number.", delay=0.01, color=Color.RED)
                except ValueError:
                    type_text("Please enter a valid number.", delay=0.01, color=Color.RED)
            
            print()
            continue_edit = input(f"{Color.YELLOW}Would you like to edit another answer? (yes/no) {Color.END}")
            if continue_edit.lower() not in ['yes', 'y']:
                break
        
        print()
        type_text("Great! Let's proceed with creating your resume.", delay=0.01, color=Color.GREEN)

    def _analyze_and_enhance_skills(self):
        """Analyze user responses and identify implied skills that weren't explicitly mentioned"""
    
    # Collect all user responses into a single text for analysis
        all_responses = ""
        for key, value in self.user_data.items():
            if value and isinstance(value, str):
                all_responses += value + "\n\n"
    
    # Create a prompt for GPT to extract implied skills
        analysis_prompt = f"""
        You are an expert resume writer and career coach analyzing a job candidate's responses.
    
        The candidate is applying for a {self.job_role} position at the {self.resume_level} level.
    
        Based on their responses below, identify skills and capabilities that are IMPLIED but NOT EXPLICITLY mentioned.
        Focus on relevant technical skills, soft skills, and domain knowledge for a {self.job_role} position.
    
        Only include skills that are strongly implied by their experiences, not general skills that anyone in this role might have.
    
        Candidate's responses:
        {all_responses}
    
        Return your response in JSON format:
        {{
            "technical_skills": ["skill1", "skill2"...],
            "soft_skills": ["skill1", "skill2"...],
            "domain_knowledge": ["knowledge1", "knowledge2"...],
            "tools_and_platforms": ["tool1", "tool2"...]
        }}
    
        Be specific and relevant to their actual experiences. Don't add generic skills.
        """
    
        try:
        # Get analysis from GPT
            response = openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert at identifying relevant professional skills from job descriptions and experiences."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.7,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
        
        # Parse the JSON response
            implied_skills = json.loads(response.choices[0].message.content)
        
        # Store the implied skills
            self.implied_skills = implied_skills
        
            return implied_skills
    
        except Exception as e:
            print_colored(f"Error analyzing skills: {str(e)}", Color.RED)
            return {
                "technical_skills": [],
                "soft_skills": [],
                "domain_knowledge": [],
                "tools_and_platforms": []
            }             
        
    def _confirm_enhanced_skills(self, implied_skills):
        """Allow the user to confirm which implied skills should be included"""
        print()
        print_colored("=" * 80, Color.BLUE)
        print_colored(f"{' ' * 15}ADDITIONAL SKILLS IDENTIFIED FROM YOUR RESPONSES", Color.BLUE, bold=True)
        print_colored("=" * 80, Color.BLUE)
        print()
        
        type_text("Based on your responses, I've identified additional skills and capabilities that seem relevant to your experience. Would you like to include any of these in your resume?", delay=0.01, color=Color.CYAN)
        print()
        
        # Show each category of skills and let the user select
        confirmed_skills = {
            "technical_skills": [],
            "soft_skills": [],
            "domain_knowledge": [],
            "tools_and_platforms": []
        }
        
        categories = {
            "technical_skills": "Technical Skills",
            "soft_skills": "Soft Skills and Professional Abilities",
            "domain_knowledge": "Domain Knowledge and Expertise",
            "tools_and_platforms": "Tools, Software and Platforms"
        }
        
        for category, label in categories.items():
            skills = implied_skills.get(category, [])
            if not skills:
                continue
            
            print()
            print_colored(f"{label}:", Color.YELLOW, bold=True)
            for i, skill in enumerate(skills, 1):
                print(f"{i}. {skill}")
            
            print()
            include_input = input(f"{Color.YELLOW}Include these skills? (all/none/numbers separated by commas) {Color.END}")
            
            if include_input.lower() == 'all':
                confirmed_skills[category] = skills.copy()
            elif include_input.lower() != 'none' and include_input.strip():
                try:
                    selected_indices = [int(idx.strip()) - 1 for idx in include_input.split(',')]
                    confirmed_skills[category] = [skills[idx] for idx in selected_indices if 0 <= idx < len(skills)]
                except ValueError:
                    type_text("Invalid input. Including none from this category.", delay=0.01, color=Color.RED)
        
        # Add confirmed skills to user data
        existing_skills = self.user_data.get('technical_skills', '')
        
        # Format all confirmed skills into a string
        enhanced_skills = ""
        for category, label in categories.items():
            skills = confirmed_skills[category]
            if skills:
                enhanced_skills += f"\n{label}:\n"
                enhanced_skills += "\n".join([f"- {skill}" for skill in skills])
                enhanced_skills += "\n"
        
        # Append to existing skills or create new
        if existing_skills and enhanced_skills:
            self.user_data['technical_skills'] = f"{existing_skills}\n\nAdditional Identified Skills:{enhanced_skills}"
        elif enhanced_skills:
            self.user_data['technical_skills'] = f"Skills Identified From Experience:{enhanced_skills}"
        
        print()
        type_text("Thanks! These additional skills will be incorporated into your resume in an appropriate way.", delay=0.01, color=Color.GREEN)
        print()
        
        return confirmed_skills

    def _provide_feedback(self, key, answer):
        """Get AI-generated feedback on user responses to make the conversation more interactive"""
        try:
            # Different prompts based on the type of information
            if key == "summary":
                prompt = f"Based on this professional summary for a {self.job_role} position, give ONE brief, specific, encouraging suggestion for improvement or ONE positive point worth emphasizing. Keep it under 50 words and conversational: '{answer}'"
            elif key == "job_history":
                prompt = f"Based on this work experience for a {self.job_role} resume, give ONE brief, specific tip for better highlighting achievements or impact. Keep it under 50 words and conversational: '{answer}'"
            elif key == "achievements":
                prompt = f"Based on these achievements for a {self.job_role} position, suggest ONE way to quantify or strengthen the impact. Keep it under 50 words and conversational: '{answer}'"
            elif key == "technical_skills":
                prompt = f"Based on these technical skills for a {self.job_role} position, give ONE brief suggestion for better organization or presentation. Keep it under 50 words and conversational: '{answer}'"
            else:
                return  # Skip feedback for other fields
            
            # Use the new OpenAI API format
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful resume coach giving brief, friendly, specific advice."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=100,
            )
            
            # Get the feedback from the new response format
            feedback = response.choices[0].message.content.strip()
            
            # Display the feedback with a short delay
            time.sleep(1)
            print()
            type_text(f"👉 {feedback}", delay=0.01, color=Color.DARKCYAN)
            
        except Exception as e:
            # Silently fail - feedback is a nice-to-have, not critical
            pass    

    def _translate_resume(self, original_filename):
        """תהליך תרגום קורות החיים לשפה נוספת"""
        print()
        additional_lang = input(f"{Color.YELLOW}Would you like to export your resume in another language as well? (yes/no) {Color.END}")
        
        if additional_lang.lower() not in ['yes', 'y', 'sure', 'yeah']:
            return
        
        print()
        target_language = input(f"{Color.YELLOW}What language would you like to translate your resume to? (e.g., Hebrew, French, Spanish) {Color.END}")
        
        if not target_language.strip():
            type_text("No language specified. Skipping translation.", delay=0.01, color=Color.RED)
            return
        
        # מציג הודעת התחלת התרגום
        print()
        type_text(f"Translating your resume to {target_language}...", delay=0.01, color=Color.CYAN)
        
        # אנימציית טעינה פשוטה
        for i in range(10):
            sys.stdout.write(f"{Color.PURPLE}█" * i + "░" * (10-i) + f" {i*10}%{Color.END}\r")
            sys.stdout.flush()
            time.sleep(0.3)
        
        try:
            # קביעת הנתיב המלא לקובץ המקורי (על שולחן העבודה)
            desktop_path = os.path.expanduser("~/Desktop")
            full_original_path = os.path.join(desktop_path, os.path.basename(original_filename))
            
            # קריאת הקובץ המקורי מהמיקום הנכון
            with open(full_original_path, 'r', encoding='utf-8') as file:
                original_content = file.read()
            
            # בניית שם הקובץ המתורגם
            filename_base = os.path.basename(original_filename)
            file_extension = os.path.splitext(filename_base)[1]  # .html או .txt
            base_filename = os.path.splitext(filename_base)[0]  # שם הקובץ ללא סיומת
            language_suffix = target_language.lower().replace(' ', '')
            translated_filename = f"{base_filename}_{language_suffix}{file_extension}"
            
            # יצירת הנחיות לתרגום
            instructions = f"""
            Translate the following resume content to {target_language}.
            
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
            
            For technical terms in {target_language}, use the standard industry terminology.
            """
            
            # קריאה ל-OpenAI API לתרגום
            response = openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": original_content}
                ],
                temperature=0.3,
                max_tokens=4000,
            )
            
            # קבלת התוכן המתורגם
            translated_content = response.choices[0].message.content
            
            # הוספת תמיכה בכיווניות RTL אם השפה היא עברית, ערבית או אחרת שכותבים מימין לשמאל
            rtl_languages = ['hebrew', 'עברית', 'arabic', 'ערבית', 'farsi', 'פרסית', 'urdu', 'אורדו']
            if any(lang in target_language.lower() for lang in rtl_languages):
                if file_extension.lower() == '.html':
                    # אם זה קובץ HTML, צריך להוסיף תכונות RTL לתגי HTML
                    if '<html' in translated_content:
                        # הוספת תכונות dir="rtl" ו-lang לתג HTML
                        translated_content = translated_content.replace('<html', '<html dir="rtl"', 1)
                    
                    if '<body' in translated_content:
                        # הוספת class לתג body
                        translated_content = translated_content.replace('<body', '<body style="text-align: right; direction: rtl;"', 1)
                    
                    # אם יש רק טקסט HTML בלי תגי בסיס, נעטוף אותו בתגים מתאימים
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
                    
                    # הוספת CSS מיוחד לפורמט העברי
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
                    # אם זה קובץ טקסט, נוסיף הערה בראש הקובץ
                    translated_content = f"<כיוון טקסט מימין לשמאל>\n\n{translated_content}"
            
            # שמירת הקובץ המתורגם על שולחן העבודה
            full_translated_path = os.path.join(desktop_path, translated_filename)
            
            with open(full_translated_path, "w", encoding="utf-8") as file:
                file.write(translated_content)
            
            print()
            type_text(f"Your resume has been successfully translated to {target_language}!", delay=0.01, color=Color.GREEN)
            type_text(f"The translated resume is saved as: {translated_filename} on your Desktop", delay=0.01, color=Color.GREEN)
            
        except Exception as e:
            print()
            print_colored(f"An error occurred during translation: {str(e)}", Color.RED)
            print_colored("Please try again or check your internet connection.", Color.RED)

    def _generate_resume(self):
        """Generate a resume using the OpenAI API"""
        print()
        print_colored("=" * 80, Color.BLUE)
        print_colored(f"{' ' * 25}CREATING YOUR RESUME", Color.BLUE, bold=True)
        print_colored("=" * 80, Color.BLUE)
        print()
        
        type_text("Now I'll craft a professional resume based on our conversation.", delay=0.01, color=Color.GREEN)
        print()
        
        # Ask for format preference
        format_choice = input(f"{Color.YELLOW}Would you prefer your resume in 'text' format or 'HTML' (more visually appealing)? {Color.END}")
        print()
        use_html = format_choice.lower() in ['html', 'h', 'web']
        
        # Ask for style preference
        style_choice = input(f"{Color.YELLOW}What style would you prefer? (Traditional, Modern, Creative) {Color.END}")
        print()
        
        resume_style = "traditional"
        if "modern" in style_choice.lower():
            resume_style = "modern"
            type_text("A modern resume style is a great choice for most industries today!", delay=0.01, color=Color.GREEN)
        elif "creative" in style_choice.lower():
            resume_style = "creative"
            type_text("A creative style can help you stand out in the right industries!", delay=0.01, color=Color.GREEN)
        else:
            resume_style = "traditional"
            type_text("A traditional style is classic and works well across all industries.", delay=0.01, color=Color.GREEN)
        
        print()
        type_text("Creating your personalized resume now...", delay=0.01, color=Color.CYAN)
        print()
        
        # Show a simple loading animation
        for i in range(5):
            sys.stdout.write(f"{Color.MAGENTA}." * (i + 1) + Color.END + "\r")
            sys.stdout.flush()
            time.sleep(0.7)
        print("\n")

        # Analyze and enhance skills
        implied_skills = self._analyze_and_enhance_skills()

        # Get user confirmation for implied skills
        if any(implied_skills.values()):
            confirmed_skills = self._confirm_enhanced_skills(implied_skills)
        else:
            confirmed_skills = {
                "technical_skills": [],
                "soft_skills": [],
                "domain_knowledge": [],
                "tools_and_platforms": []
            }
        
        # Build the system message for OpenAI
        system_message = f"""
        You are an expert resume writer specializing in creating {resume_style} resumes for {self.resume_level} level {self.job_role} positions.
        
        Create a highly professional, ATS-friendly resume that showcases the candidate's qualifications effectively.
        
        For a {self.resume_level} level position:
        - {self.resume_level} level priorities: {"leadership impact and strategic vision" if self.resume_level == "executive" else "professional achievements and growth" if self.resume_level == "mid-level" else "education, skills, and potential"}
        - Language style: {"authoritative and strategic" if self.resume_level == "executive" else "confident and accomplished" if self.resume_level == "mid-level" else "enthusiastic and promising"}
        - Focus areas: {"leadership, transformation, and business results" if self.resume_level == "executive" else "achievements, expertise, and career progression" if self.resume_level == "mid-level" else "education, skills, and relevant experience"}
        
        Content style for a {resume_style} resume:
        - {"Formal and structured content with traditional terminology" if resume_style == "traditional" else "Concise and impactful descriptions with modern industry terms" if resume_style == "modern" else "Engaging and distinctive content that showcases personality while remaining professional"}
        
        IMPORTANT FORMATTING GUIDELINES:
        - Create a coherent, polished, and error-free document
        - Use action verbs and quantifiable achievements
        - Ensure perfect spelling, grammar, and consistent formatting
        - Focus on results and accomplishments, not just responsibilities
        - Tailor content specifically to a {self.job_role} position

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

        Technical Skills: {', '.join(confirmed_skills.get('technical_skills', []))}
        Soft Skills: {', '.join(confirmed_skills.get('soft_skills', []))}
        Domain Knowledge: {', '.join(confirmed_skills.get('domain_knowledge', []))}
        Tools & Platforms: {', '.join(confirmed_skills.get('tools_and_platforms', []))}

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
        user_message = f"Please create a {resume_style} resume for a {self.resume_level} level {self.job_role} position based on the following information:\n\n"
        
        # Add the user information in a structured way
        user_message += f"NAME: {self.user_data.get('full_name', '')}\n"
        user_message += f"TARGET POSITION: {self.job_role}\n\n"
        
        # Add all other user data
        for question in self.questions:
            key = question["key"]
            if key in self.user_data and self.user_data[key] and key != 'full_name':
                user_message += f"{question['section'].upper()} - {question['question']}\n{self.user_data[key]}\n\n"
        
        # Output format instructions
        if use_html:
            user_message += f"""
            Please create the resume in HTML format that reflects a {resume_style} style and suitable for a {self.resume_level} level position.
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
            6. Replace [RESUME_STYLE] with the actual style name: "traditional", "modern", or "creative".
            ...


            
            DO NOT include any placeholders or lorem ipsum text - use only the information provided.
            """
        
        else:
            user_message += f"""
            Please create the resume in plain text format, formatted to be easily readable. 
            Use markdown-style formatting where helpful (bold, italics, etc.).
            Organize the content with clear section headings and consistent structure.
            """
        
        try:
            # Create a loading animation
            print_colored("Applying AI resume expertise...", Color.PURPLE)
            for i in range(10):
                sys.stdout.write(f"{Color.PURPLE}█" * i + "░" * (10-i) + f" {i*10}%{Color.END}\r")
                sys.stdout.flush()
                time.sleep(0.3)
            print("\n")
            
            # Use the new OpenAI API format
            response = openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=4000,
            )
            
            # Get the resume text from the new response format
            resume_text = response.choices[0].message.content
            
            # Generate filename with user name and job role
            name_part = self.user_data.get('full_name', 'resume').replace(' ', '_').lower()
            job_part = self.job_role.replace(' ', '_').lower()
            file_extension = "html" if use_html else "txt"
            filename = f"{name_part}_{job_part}_resume.{file_extension}"
            
            # Save the resume to a file
            self._save_resume_to_file(resume_text, filename)
            
            # Success message
            print()
            print_colored("=" * 80, Color.GREEN)
            print_colored(f"{' ' * 25}RESUME COMPLETED!", Color.GREEN, bold=True)
            print_colored("=" * 80, Color.GREEN)
            print()
            
            type_text(f"🎉 Your personalized {resume_style} resume for a {self.job_role} position is ready!", delay=0.01, color=Color.GREEN, bold=True)
            print()
            
            if use_html:
                type_text("Your resume has been saved. Would you like me to try to open it in your browser?", delay=0.01, color=Color.CYAN)
                print()
                
                open_choice = input(f"{Color.YELLOW}Open resume in browser? (yes/no) {Color.END}")
                if open_choice.lower() in ['yes', 'y', 'sure', 'yeah']:
                    import webbrowser
                    try:
                        webbrowser.open(filename)
                    except:
                        type_text("I couldn't open your browser automatically. Please open the HTML file manually.", delay=0.01, color=Color.YELLOW)
                
                # כאן תוסיף קריאה לפונקציית התרגום
                self._translate_resume(filename)

                
                # Also offer to email the resume
                email_choice = input(f"\n{Color.YELLOW}Would you like me to help you email this resume to yourself? (yes/no) {Color.END}")
                if email_choice.lower() in ['yes', 'y', 'sure', 'yeah']:
                    self._offer_email_options(filename)
            else:
                type_text(f"I've saved your resume as '{filename}' in the current directory.", delay=0.01, color=Color.CYAN)
                print()
                
                # Get resume summary feedback
                self._get_resume_feedback()
                
                preview_choice = input(f"\n{Color.YELLOW}Would you like to preview your resume in the terminal? (yes/no) {Color.END}")
                if preview_choice.lower() in ['yes', 'y', 'sure', 'yeah']:
                    print("\n")
                    print_colored("=" * 80, Color.BLUE)
                    print_colored(f"{' ' * 30}RESUME PREVIEW", Color.BLUE, bold=True)
                    print_colored("=" * 80, Color.BLUE)
                    print("\n")
                    print(resume_text)
                    print("\n")
            
            # Provide final guidance
            print()
            self._provide_final_advice()
            
        except Exception as e:
            print_colored(f"An error occurred while creating your resume: {str(e)}", Color.RED)
            print_colored("Please try again or check your internet connection.", Color.RED)

    def _save_resume_to_file(self, resume_text, filename):
        """Save the resume to a file"""
        try:
            # Get desktop path
            desktop_path = os.path.expanduser("~/Desktop")
            
            # Create full path for the file
            full_path = os.path.join(desktop_path, filename)
            
            # Save the file
            with open(full_path, "w", encoding="utf-8") as file:
                file.write(resume_text)
            
            # If it's an HTML file, enhance it
            if filename.endswith('.html'):
                self._enhance_html_resume(full_path)
            
            type_text(f"Resume saved to desktop: {filename}", delay=0.01, color=Color.GREEN)
                    
        except Exception as e:
            print_colored(f"Error saving file: {str(e)}", Color.RED)
            
    def _enhance_html_resume(self, filename):
        """Ensure the HTML resume has proper styling and structure"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                html_content = file.read()
                
# Check if the HTML has basic structure elements
            if '<!DOCTYPE html>' not in html_content:
                # If basic structure is missing, add a proper HTML wrapper
                improved_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.user_data.get('full_name', 'Resume')} - {self.job_role} Resume</title>
    <style>
        /* Base styles */
        body {{
            font-family: 'Calibri', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.5;
            color: #333;
            max-width: 8.5in;
            margin: 0 auto;
            padding: 0.5in;
        }}
        /* Add default styling if none was provided */
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
                
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(improved_html)
                    
            # Check for common styling issues and possibly enhance
            self._apply_additional_styles(filename)
                
        except Exception as e:
            # Silently fail - the original HTML should still be functional
            pass
    
    def _apply_additional_styles(self, filename):
        """Apply additional styles to ensure professional appearance"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                html_content = file.read()
                    
            # Check if there's a style section
            if '<style>' in html_content and '</style>' in html_content:
                # Add improved styling that maintains the original layout but enhances appearance
                #עיצוב תוצר סופי      
                enhanced_styles = """
            /* Enhanced base styles */
            body {
                font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f9f9f9;
                margin: 0;
                padding: 0;
            }
            
            .resume-container {
                max-width: 8.5in;
                margin: 30px auto;
                padding: 40px;
                background-color: #fff;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                border-radius: 4px;
            }
            
            /* Improved typography */
            h1 {
                font-size: 28px;
                color: #2c3e50;
                margin-bottom: 5px;
                font-weight: bold !important;
            }
            
            h2 {
                font-size: 22px;
                color: #2c3e50;
                margin-top: 25px;
                margin-bottom: 15px;
                border-bottom: 2px solid #eaeaea;
                padding-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            h3 {
                font-size: 18px;
                color: #34495e;
                margin-bottom: 8px;
                margin-top: 15px;
            }
            
            p {
                margin-bottom: 10px;
            }
            
            /* Enhanced header */
            .resume-header {
                text-align: center;
                margin-bottom: 30px;
            }
            
            .job-title {
                font-size: 18px;
                color: #7f8c8d;
                margin-bottom: 15px;
            }
            
            /* Improved contact info */
            .contact-info {
            font-size: 15px;
            margin-bottom: 15px;
            text-align: center;
            padding-bottom: 20px;
            border-bottom: 1px solid #eaeaea;  /* הוסף שורה זו */
            }
            
            .contact-info p {
                margin: 5px 0;
            }
            
            /* Enhanced sections */
            .section {
                margin-bottom: 25px;
            }
            
            /* Experience and education items */
            .experience-item, .education-item {
                margin-bottom: 20px;
                position: relative;
            }
            
            .job-position, .education-degree {
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 3px;
            }
            
            .job-date, .education-date, .date-range {
                float: right;
                font-style: italic;
                color: #7f8c8d;
            }
            
            .job-company, .education-institution, .company-name, .institution-name {
                font-weight: 500;
                color: #34495e;
            }
            
            .job-location, .education-location {
                color: #7f8c8d;
                font-style: italic;
            }
            
            /* List styling */
            ul {
                margin-top: 10px;
                margin-bottom: 15px;
                padding-left: 20px;
            }
            
            ul li {
                margin-bottom: 8px;
                position: relative;
            }
            
            /* Skills columns */
            .skills-list {
                columns: 2;
                column-gap: 30px;
                list-style-type: none;
                padding-left: 0;
            }
            
            .skills-list li {
                margin-bottom: 8px;
                break-inside: avoid;
                position: relative;
                padding-left: 15px;
            }
            
            .skills-list li:before {
                content: "•";
                position: absolute;
                left: 0;
            }
            
            /* Summary section */
            .summary {
                background-color: #f8f9fa;
                padding: 15px;
                border-left: 3px solid #3498db;
                margin-bottom: 25px;
                line-height: 1.6;
            }
            
            /* Style variations - Enhanced with fonts, borders, spacing, etc. */
            /* Traditional style */
            .traditional {
                font-family: 'Georgia', 'Times New Roman', serif;
            }
            
            .traditional h1 {
                color: #1a3c5a;
                font-weight: 600;
            }
            
            .traditional h2 {
                color: #1a3c5a;
                border-bottom: 2px solid #c4d3df;
                letter-spacing: 0.5px;
            }
            
            .traditional .job-position, .traditional .education-degree {
                color: #1a3c5a;
            }
            
            .traditional .summary {
                border-left: 3px solid #1a3c5a;
                background-color: #f5f8fa;
                border-radius: 0;
            }
            
            .traditional .skills-list li:before {
                content: "■";
                font-size: 8px;
                color: #1a3c5a;
            }
            
            .traditional p {
                line-height: 1.5;
                margin-bottom: 8px;
            }
            
            /* Modern style */
            .modern {
                font-family: 'Helvetica Neue', Arial, sans-serif;
            }
            
            .modern h1 {
                color: #3a4750;
                font-weight: 400;
            }
            
            .modern h2 {
                color: #3a4750;
                border-bottom: 1px solid #dfe4e8;
                letter-spacing: 1px;
            }
            
            .modern .job-position, .modern .education-degree {
                color: #3a4750;
            }
            
            .modern .summary {
                border-left: 4px solid #3a4750;
                background-color: #f7f7f7;
                border-radius: 2px;
            }
            
            .modern .skills-list li:before {
                content: "•";
                font-size: 14px;
                color: #3a4750;
            }
            
            .modern p {
                line-height: 1.7;
                margin-bottom: 12px;
            }
            
            /* Creative style */
            .creative {
                font-family: 'Segoe UI', 'Roboto', sans-serif;
            }
            
            .creative h1 {
                color: #654ea3;
                font-weight: 500;
            }
            
            .creative h2 {
                color: #654ea3;
                border-bottom: 2px dotted #e1d9f2;
                letter-spacing: 1.2px;
            }
            
            .creative .job-position, .creative .education-degree {
                color: #654ea3;
            }
            
            .creative .summary {
                border-left: 4px solid #654ea3;
                background-color: #f9f7fd;
                border-radius: 4px;
                box-shadow: 0 2px 5px rgba(101, 78, 163, 0.1);
            }
            
            .creative .skills-list li:before {
                content: none !important;
                font-size: 10px;
            }
            /* עיצוב "טאב" מסביב לכל סקיל */
            .creative .skills-list li {
                display: inline-block;           /* מסדר את הפריטים זה לצד זה */
                background-color: rgba(101, 78, 163, 0.08); 
                border: 1px solid #654ea3;      /* ניתן לשנות את עובי וצבע המסגרת לפי הצורך */
                border-radius: 20px;            /* יוצר את הפינות העגולות (טאב) */
                padding: 8px 14px;              /* רווח פנימי */
                margin: 4px;                    /* רווח בין סקילים */
                cursor: default;                /* לא חובה, רק כדי לבטל סמן של טקסט */
            }
            .creative p {
                line-height: 1.8;
                margin-bottom: 14px;
            }
            
            /* Experience items styling per theme */
            .traditional .experience-item, .traditional .education-item {
                border-left: 0;
                padding-left: 0;
            }
            
            .modern .experience-item, .modern .education-item {
                border-left: 0;
                padding-left: 0;
                margin-bottom: 25px;
            }
            
            .creative .experience-item, .creative .education-item {
                border-left: 2px solid #f0e9ff;
                padding-left: 15px;
                border-radius: 0 4px 4px 0;
                margin-bottom: 30px;
            }
            /* Editable content styling */
            [contenteditable=true] {
                position: relative;
            }
            
            [contenteditable=true]:hover {
                background-color: rgba(135, 206, 250, 0.3);
                cursor: default;
            }
            
            [contenteditable=true]:hover::after {
                content: "✏️";
                position: absolute;
                bottom: 4px;
                right: 4px;
                font-size: 12px;
                opacity: 0.6;
                pointer-events: none;
            }
            
            [contenteditable=true]:focus {
                outline: 1px solid #4682B4;
                background-color: rgba(135, 206, 250, 0.2);
            }
            
            .save-button {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background-color: #4682B4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
                z-index: 1000;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            
            .save-button:hover {
                background-color: #36648B;
            }
            
            .save-notification {
                position: fixed;
                bottom: 80px;
                right: 20px;
                background-color: #2E8B57;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                display: none;
                z-index: 1000;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            .print-button {
                position: fixed;
                bottom: 20px;
                left: 20px;
                background-color: #607D8B;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
                z-index: 1000;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            
            .print-button:hover {
                background-color: #455A64;
            }
            """
                
                # Insert the enhanced styles into existing style section
                html_content = html_content.replace('</style>', enhanced_styles + '\n</style>')
                
                # Add style class to body based on resume_style
                resume_style_class = ""
                if hasattr(self, 'resume_style'):
                    resume_style_class = self.resume_style
                
                # Add class to body tag for styling variations
                if '<body' in html_content and resume_style_class:
                    if 'class=' in html_content:
                        # If body already has class attribute
                        html_content = html_content.replace('<body class="', f'<body class="{resume_style_class} ')
                    else:
                        # If body doesn't have class attribute
                        html_content = html_content.replace('<body', f'<body class="{resume_style_class}"')
                
                
                    # Add container div if not already present
                    if '<div class="resume-container">' not in html_content:
                        start_content = html_content.find('<body')
                        end_body_tag = html_content.find('>', start_content) + 1
                        
                        html_content = html_content[:end_body_tag] + '\n<div class="resume-container">\n' + html_content[end_body_tag:]
                        
                        # Close the container div before the closing body tag
                        html_content = html_content.replace('</body>', '</div>\n</body>')

                    # Keep the print button if not already there
                    if '<button class="print-button"' not in html_content:
                        print_button = """
                    <button class="print-button" onclick="window.print()" style="position: fixed; bottom: 20px; left: 20px; background-color: #607D8B; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; z-index: 1000; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">Print Resume</button>
                        """
                        html_content = html_content.replace('</div>\n</body>', f'</div>\n{print_button}\n</body>')

                    # Add save button and notification if not already there
                    if '<button class="save-button"' not in html_content:
                        save_elements = """
                    <button class="save-button">Save Changes</button>
                    <div class="save-notification">Changes saved!</div>
                        """
                        html_content = html_content.replace('</div>\n</body>', f'</div>\n{save_elements}\n</body>')

                    # Add the editing script if not already there
                    if 'document.addEventListener(\'DOMContentLoaded\'' not in html_content:
                        editing_script = """
                    <script>
                        // Make all elements with contenteditable=true actually editable
                        document.addEventListener('DOMContentLoaded', function() {
                            // Keep track of original content for change detection
                            const originalContents = {};
                            const editableElements = document.querySelectorAll('[contenteditable=true]');
                            
                            editableElements.forEach(function(element, index) {
                                // Store original content
                                originalContents[index] = element.innerHTML;
                                
                                // Add event listener to track edits
                                element.addEventListener('input', function() {
                                    window.resumeHasUnsavedChanges = true;
                                });
                            });
                            
                            // Initialize the change tracker
                            window.resumeHasUnsavedChanges = false;
                            
                            // Save button functionality
                            const saveButton = document.querySelector('.save-button');
                            const saveNotification = document.querySelector('.save-notification');
                            
                            saveButton.addEventListener('click', function() {
                                // Update original contents to reflect current state
                                editableElements.forEach(function(element, index) {
                                    originalContents[index] = element.innerHTML;
                                });
                                
                                // Mark as saved
                                window.resumeHasUnsavedChanges = false;
                                
                                // Store in localStorage
                                try {
                                    localStorage.setItem('savedResumeContent', document.documentElement.outerHTML);
                                    localStorage.setItem('resumeSaveTime', new Date().toISOString());
                                    
                                    // Show notification
                                    saveNotification.style.display = 'block';
                                    setTimeout(function() {
                                        saveNotification.style.display = 'none';
                                    }, 3000);
                                } catch (e) {
                                    console.error('Error saving to localStorage:', e);
                                    saveNotification.textContent = 'Error saving changes!';
                                    saveNotification.style.backgroundColor = '#B22222';
                                    saveNotification.style.display = 'block';
                                    setTimeout(function() {
                                        saveNotification.style.display = 'none';
                                        saveNotification.textContent = 'Changes saved successfully!';
                                        saveNotification.style.backgroundColor = '#2E8B57';
                                    }, 3000);
                                }
                            });
                            
                            // Warning before leaving with unsaved changes
                            window.addEventListener('beforeunload', function(e) {
                                if (window.resumeHasUnsavedChanges) {
                                    e.preventDefault();
                                    e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
                                    return e.returnValue;
                                }
                            });
                            
                            // Auto-save every 60 seconds if there are changes
                            setInterval(function() {
                                if (window.resumeHasUnsavedChanges) {
                                    // Trigger click on save button
                                    saveButton.click();
                                }
                            }, 60000);
                        });
                    </script>
                    """
                        html_content = html_content.replace('</body>', f'{editing_script}\n</body>')
                
                # הוסף קוד פשוט להוספת contenteditable לאלמנטים
                if '<div class="resume-header">' in html_content:
                    html_content = html_content.replace('<div class="resume-header">', '<div class="resume-header" contenteditable="true">')
                if '<div class="summary">' in html_content:
                    html_content = html_content.replace('<div class="summary">', '<div class="summary" contenteditable="true">')
                if '<div class="experience-item">' in html_content:
                    html_content = html_content.replace('<div class="experience-item">', '<div class="experience-item" contenteditable="true">')
                if '<div class="education-item">' in html_content:
                    html_content = html_content.replace('<div class="education-item">', '<div class="education-item" contenteditable="true">')
                if '<div class="section">' in html_content:
                    html_content = html_content.replace('<div class="section">', '<div class="section" contenteditable="true">')

                # Write the enhanced HTML back to the file
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(html_content)

              #עיצוב ברירת מחדל      
            else:
                # If no style section exists, create one with all styling
                default_styles = """<style>
            /* Enhanced base styles */
            body {
                font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f9f9f9;
                margin: 0;
                padding: 0;
            }
            
            .resume-container {
                max-width: 8.5in;
                margin: 30px auto;
                padding: 40px;
                background-color: #fff;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                border-radius: 4px;
            }
            
            /* Improved typography */
            h1 {
                font-size: 28px;
                color: #2c3e50;
                margin-bottom: 5px;
                font-weight: bold !important;
            }
            
            h2 {
                font-size: 22px;
                color: #2c3e50;
                margin-top: 25px;
                margin-bottom: 15px;
                border-bottom: 2px solid #eaeaea;
                padding-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            h3 {
                font-size: 18px;
                color: #34495e;
                margin-bottom: 8px;
                margin-top: 15px;
            }
            
            p {
                margin-bottom: 10px;
            }
            
            /* Enhanced header */
            .resume-header {
                text-align: center;
                margin-bottom: 30px;
            }
            
            .job-title {
                font-size: 18px;
                color: #7f8c8d;
                margin-bottom: 15px;
            }
            
            /* Improved contact info */
            .contact-info {
            font-size: 15px;
            margin-bottom: 15px;
            text-align: center;
            padding-bottom: 20px;
            border-bottom: 1px solid #eaeaea;  /* הוסף שורה זו */
            }
            
            .contact-info p {
                margin: 5px 0;
            }
            
            /* Enhanced sections */
            .section {
                margin-bottom: 25px;
            }
            
            /* Experience and education items */
            .experience-item, .education-item {
                margin-bottom: 20px;
                position: relative;
            }
            
            .job-position, .education-degree {
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 3px;
            }
            
            .job-date, .education-date, .date-range {
                float: right;
                font-style: italic;
                color: #7f8c8d;
            }
            
            .job-company, .education-institution, .company-name, .institution-name {
                font-weight: 500;
                color: #34495e;
            }
            
            .job-location, .education-location {
                color: #7f8c8d;
                font-style: italic;
            }
            
            /* List styling */
            ul {
                margin-top: 10px;
                margin-bottom: 15px;
                padding-left: 20px;
            }
            
            ul li {
                margin-bottom: 8px;
                position: relative;
            }
            
            /* Skills columns */
            .skills-list {
                columns: 2;
                column-gap: 30px;
                list-style-type: none;
                padding-left: 0;
            }
            
            .skills-list li {
                margin-bottom: 8px;
                break-inside: avoid;
                position: relative;
                padding-left: 15px;
            }
            
            .skills-list li:before {
                content: "•";
                position: absolute;
                left: 0;
            }
            
            /* Summary section */
            .summary {
                background-color: #f8f9fa;
                padding: 15px;
                border-left: 3px solid #3498db;
                margin-bottom: 25px;
                line-height: 1.6;
            }
            
            /* Style variations - Enhanced with fonts, borders, spacing, etc. */
            /* Traditional style */
            .traditional {
                font-family: 'Georgia', 'Times New Roman', serif;
            }
            
            .traditional h1 {
                color: #1a3c5a;
                font-weight: 600;
            }
            
            .traditional h2 {
                color: #1a3c5a;
                border-bottom: 2px solid #c4d3df;
                letter-spacing: 0.5px;
            }
            
            .traditional .job-position, .traditional .education-degree {
                color: #1a3c5a;
            }
            
            .traditional .summary {
                border-left: 3px solid #1a3c5a;
                background-color: #f5f8fa;
                border-radius: 0;
            }
            
            .traditional .skills-list li:before {
                content: "■";
                font-size: 8px;
                color: #1a3c5a;
            }
            
            .traditional p {
                line-height: 1.5;
                margin-bottom: 8px;
            }
            
            /* Modern style */
            .modern {
                font-family: 'Helvetica Neue', Arial, sans-serif;
            }
            
            .modern h1 {
                color: #3a4750;
                font-weight: 400;
            }
            
            .modern h2 {
                color: #3a4750;
                border-bottom: 1px solid #dfe4e8;
                letter-spacing: 1px;
            }
            
            .modern .job-position, .modern .education-degree {
                color: #3a4750;
            }
            
            .modern .summary {
                border-left: 4px solid #3a4750;
                background-color: #f7f7f7;
                border-radius: 2px;
            }
            
            .modern .skills-list li:before {
                content: "•";
                font-size: 14px;
                color: #3a4750;
            }
            
            .modern p {
                line-height: 1.7;
                margin-bottom: 12px;
            }
            
            /* Creative style */
            .creative {
                font-family: 'Segoe UI', 'Roboto', sans-serif;
            }
            
            .creative h1 {
                color: #654ea3;
                font-weight: 500;
            }
            
            .creative h2 {
                color: #654ea3;
                border-bottom: 2px dotted #e1d9f2;
                letter-spacing: 1.2px;
            }
            
            .creative .job-position, .creative .education-degree {
                color: #654ea3;
            }
            
            .creative .summary {
                border-left: 4px solid #654ea3;
                background-color: #f9f7fd;
                border-radius: 4px;
                box-shadow: 0 2px 5px rgba(101, 78, 163, 0.1);
            }
            
            .creative .skills-list li:before {
                content: none !important;
                font-size: 10px;
            }
            /* עיצוב "טאב" מסביב לכל סקיל */
            .creative .skills-list li {
                display: inline-block;           /* מסדר את הפריטים זה לצד זה */
                background-color: rgba(101, 78, 163, 0.08); 
                border: 1px solid #654ea3;      /* ניתן לשנות את עובי וצבע המסגרת לפי הצורך */
                border-radius: 20px;            /* יוצר את הפינות העגולות (טאב) */
                padding: 8px 14px;              /* רווח פנימי */
                margin: 4px;                    /* רווח בין סקילים */
                cursor: default;                /* לא חובה, רק כדי לבטל סמן של טקסט */
            }
            
            .creative p {
                line-height: 1.8;
                margin-bottom: 14px;
            }
            
            /* Experience items styling per theme */
            .traditional .experience-item, .traditional .education-item {
                border-left: 0;
                padding-left: 0;
            }
            
            .modern .experience-item, .modern .education-item {
                border-left: 0;
                padding-left: 0;
                margin-bottom: 25px;
            }
            
            .creative .experience-item, .creative .education-item {
                border-left: 2px solid #f0e9ff;
                padding-left: 15px;
                border-radius: 0 4px 4px 0;
                margin-bottom: 30px;
            }
            /* Editable content styling */
            [contenteditable=true] {
                position: relative;
            }
            
            [contenteditable=true]:hover {
                background-color: rgba(135, 206, 250, 0.3);
                cursor: default;
            }
            
            [contenteditable=true]:hover::after {
                content: "✏️";
                position: absolute;
                bottom: 4px;
                right: 4px;
                font-size: 12px;
                opacity: 0.6;
                pointer-events: none;
            }
            
            [contenteditable=true]:focus {
                outline: 1px solid #4682B4;
                background-color: rgba(135, 206, 250, 0.2);
            }
            
            .save-button {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background-color: #4682B4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
                z-index: 1000;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            
            .save-button:hover {
                background-color: #36648B;
            }
            
            .save-notification {
                position: fixed;
                bottom: 80px;
                right: 20px;
                background-color: #2E8B57;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                display: none;
                z-index: 1000;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            .print-button {
                position: fixed;
                bottom: 20px;
                left: 20px;
                background-color: #607D8B;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
                z-index: 1000;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            
            .print-button:hover {
                background-color: #455A64;
            }
        </style>

        <head>"""
                html_content = html_content.replace("<head>", default_styles)
                
                # Add a body class for style variations
                resume_style_class = ""
                if hasattr(self, 'resume_style'):
                    resume_style_class = self.resume_style
                    
                # Add wrapper div
                if '<body' in html_content and resume_style_class:
                    if 'class=' in html_content:
                        html_content = html_content.replace('<body class="', f'<body class="{resume_style_class} ')
                    else:
                        html_content = html_content.replace('<body', f'<body class="{resume_style_class}"')
                
                # Add container
                start_content = html_content.find('<body')
                end_body_tag = html_content.find('>', start_content) + 1
                
                html_content = html_content[:end_body_tag] + '\n<div class="resume-container">\n' + html_content[end_body_tag:]
                
                # Close the container
                html_content = html_content.replace('</body>', '</div>\n<button class="print-button" onclick="window.print()">Print Resume</button>\n</body>')
                
                # Write the enhanced HTML back to the file
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(html_content)
        except Exception as e:
            # Silently fail - the original HTML should still be functional
            pass
    
    def _get_resume_feedback(self):
        """Get AI analysis of the resume strengths and areas for improvement"""
        try:
            # Create a prompt for resume analysis
            analysis_prompt = f"""
            Based on the information collected for this {self.resume_level} level {self.job_role} resume, provide:
            1. THREE specific strengths of this candidate's profile
            2. TWO specific suggestions for how they could strengthen their resume in the future
            
            Keep each point brief (under 20 words) and specific to their profile.
            """
            
            # Collect user data into a single string
            user_profile = ""
            for key, value in self.user_data.items():
                user_profile += f"{key}: {value}\n\n"
            
            # Use the new OpenAI API format
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional resume analyst providing brief, specific feedback."},
                    {"role": "user", "content": analysis_prompt + "\n\nCANDIDATE PROFILE:\n" + user_profile}
                ],
                temperature=0.7,
                max_tokens=300,
            )
            
            # Get the feedback from the new response format
            feedback = response.choices[0].message.content.strip()
            
            # Display the feedback
            print()
            print_colored("RESUME ANALYSIS:", Color.PURPLE, bold=True)
            print()
            print(feedback)
            
        except Exception as e:
            # If this fails, we can skip it silently - it's a bonus feature
            pass
    
    def _offer_email_options(self, filename):
        """Offer to email the resume file to the user"""
        print_colored("\nTo email your resume:", Color.CYAN, bold=True)
        print()
        
        # Get user's email if not already provided
        user_email = self.user_data.get('email', '')
        if not user_email:
            user_email = input(f"{Color.YELLOW}What email address should I send the resume to? {Color.END}")
        
        # Provide instructions for different email clients
        type_text("Since I can't send emails directly, here are instructions to email your resume:", delay=0.01, color=Color.CYAN)
        print()
        
        # Gmail instructions
        print_colored("Gmail:", Color.BLUE, bold=True)
        type_text(f"1. Go to Gmail and click 'Compose'", delay=0.005, color=Color.DARKCYAN)
        type_text(f"2. Enter your email address: {user_email}", delay=0.005, color=Color.DARKCYAN)
        type_text(f"3. Subject: 'My Professional Resume for {self.job_role} Positions'", delay=0.005, color=Color.DARKCYAN)
        type_text(f"4. Click the attachment icon and select the file: {filename}", delay=0.005, color=Color.DARKCYAN)
        type_text(f"5. Add a brief message and click 'Send'", delay=0.005, color=Color.DARKCYAN)
        print()
        
        # Outlook instructions
        print_colored("Outlook:", Color.BLUE, bold=True)
        type_text(f"1. Open Outlook and click 'New Email'", delay=0.005, color=Color.DARKCYAN)
        type_text(f"2. Enter your email address: {user_email}", delay=0.005, color=Color.DARKCYAN)
        type_text(f"3. Subject: 'My Professional Resume for {self.job_role} Positions'", delay=0.005, color=Color.DARKCYAN)
        type_text(f"4. Click 'Attach File' and select the file: {filename}", delay=0.005, color=Color.DARKCYAN)
        type_text(f"5. Add a brief message and click 'Send'", delay=0.005, color=Color.DARKCYAN)
        print()
        
        # File location reminder
        type_text(f"Your resume file is located at: {os.path.abspath(filename)}", delay=0.01, color=Color.YELLOW)
        print()

    def _provide_final_advice(self):
        """Provide personalized advice for using the resume based on user's responses and target role"""
        try:
            # Create a prompt for personalized advice
            advice_prompt = f"""
            Based on this candidate's profile for a {self.job_role} position, provide 3 BRIEF, actionable tips (max 15 words each) for:
            1. How to best present their experience in interviews
            2. One specific way to strengthen their profile
            3. One practical job search strategy
            
            Candidate Profile:
            - Experience Level: {self.resume_level}
            - Target Role: {self.job_role}
            - Key Skills: {self.user_data.get('technical_skills', '')}
            - Notable Achievements: {self.user_data.get('achievements', '')}
            - Education: {self.user_data.get('education', '')}
            
            Keep tips:
            - Under 15 words each
            - Specific to their background
            - Actionable and practical
            - Based on their actual experience
            """
            
            # Get personalized advice from GPT
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert career coach providing brief, actionable tips based on the candidate's profile."},
                    {"role": "user", "content": advice_prompt}
                ],
                temperature=0.7,
                max_tokens=300,
            )
            
            # Get the advice from the response
            personalized_advice = response.choices[0].message.content.strip()
            
            # Display the advice
            print()
            print_colored("QUICK CAREER TIPS:", Color.CYAN, bold=True)
            print()
            type_text(personalized_advice, delay=0.01, color=Color.DARKCYAN)
            print()
            
            # Final goodbye message
            type_text(f"Thank you for using the Interactive Resume Builder by Roy Leshem, {self.user_name}! Best of luck in your job search for {self.job_role} positions!", 
                     delay=0.01, color=Color.GREEN, bold=True)
            print("\n")
            
        except Exception as e:
            # Fallback to basic tips if AI advice fails
            print()
            print_colored("ADVICES BASED ON YOUR RESUME:", Color.CYAN, bold=True)
            print()
            type_text(f"Thank you for using the Interactive Resume Builder by Roy Leshem, {self.user_name}! Best of luck in your job search for {self.job_role} positions!", 
                     delay=0.01, color=Color.GREEN, bold=True)
            print("\n")

    def _check_for_follow_up(self, key, answer):
        """Check if a follow-up question is needed based on the user's answer"""
        try:
            # Special handling for LinkedIn
            if key == 'linkedin':
                # Only ask if we haven't asked before
                if 'linkedin_followup_asked' not in self.user_data:
                    print()
                    type_text("Quick follow-up:", delay=0.01, color=Color.YELLOW)
                    type_text("Do you have any other professional social media profiles you'd like to include? (e.g., GitHub, portfolio website)", delay=0.01, color=Color.YELLOW)
                    print()
                    
                    social_answer = input(f"{Color.YELLOW}> {Color.END}")
                    if social_answer.strip():
                        self.user_data[key] = f"{answer}\nOther profiles: {social_answer.strip()}"
                    # Mark that we've asked the follow-up
                    self.user_data['linkedin_followup_asked'] = True
                    type_text("Thanks for the additional information!", delay=0.01, color=Color.GREEN)
                    print()
                return

            # Special handling for work experience
            if key == 'job_history':
                # Use GPT to analyze if essential details are missing
                analysis_prompt = f"""
                Analyze this work experience answer and check if any of these essential details are missing:
                1. Company name
                2. Time period/dates
                3. Role/title
                
                Answer to analyze: "{answer}"
                
                If any of these details are missing, respond with "MISSING_DETAILS"
                If all details are present, respond with "NO_FOLLOW_UP"
                """
                
                # Get analysis from GPT
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a resume expert checking for missing essential work experience details. Be strict in checking for missing information."},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=150,
                )
                
                # Get the analysis from the response
                analysis = response.choices[0].message.content.strip()
                
                # If follow-up is needed, ask the unified question
                if "MISSING_DETAILS" in analysis:
                    print()
                    type_text("Quick follow-up:", delay=0.01, color=Color.YELLOW)
                    type_text("If you accidentally left out any of the details regarding the date range, job title, or company name, it's recommended to add them now for maximum clarity", delay=0.01, color=Color.YELLOW)
                    print()
                    
                    # Get user's response
                    follow_up_answer = input(f"{Color.YELLOW}> {Color.END}")
                    if follow_up_answer.strip():
                        # Update the original answer with the additional information
                        self.user_data[key] = f"{answer}\n{follow_up_answer.strip()}"
                        type_text("Great! Let's move on", delay=0.01, color=Color.GREEN)
                        print()
                return

            # For all other questions, use GPT to analyze the answer
            analysis_prompt = f"""
            You are a resume expert analyzing a user's answer to determine if a follow-up question is needed.
            
            Question Key: {key}
            Answer: "{answer}"
            
            Analyze the answer in the context of a resume for a {self.job_role} position.
            
            If a follow-up is needed, respond with "FOLLOW_UP_NEEDED" followed by a brief, specific question (max 10 words).
            If no follow-up is needed, respond with "NO_FOLLOW_UP"
            
            Consider:
            1. Are there any missing essential details?
            2. Could the answer be more specific or detailed?
            3. Would additional information add value to the resume?
            4. Is there ambiguity that needs clarification?
            
            Example responses:
            - If work experience is missing dates: "FOLLOW_UP_NEEDED: What was the duration of this position?"
            - If all details are present: "NO_FOLLOW_UP"
            """
            
            # Get analysis from GPT
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a resume expert analyzing if a follow-up question would add valuable information."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.7,
                max_tokens=150,
            )
            
            # Get the analysis from the response
            analysis = response.choices[0].message.content.strip()
            
            # If follow-up is needed, ask the question
            if "FOLLOW_UP_NEEDED:" in analysis:
                print()
                type_text("Quick follow-up:", delay=0.01, color=Color.YELLOW)
                # Extract just the question from the analysis
                follow_up = analysis.split("FOLLOW_UP_NEEDED:")[1].strip()
                type_text(follow_up, delay=0.01, color=Color.YELLOW)
                print()
                
                # Get user's response
                follow_up_answer = input(f"{Color.YELLOW}> {Color.END}")
                if follow_up_answer.strip():
                    # Update the original answer with the additional information
                    self.user_data[key] = f"{answer}\n{follow_up_answer.strip()}"
                    type_text("Thanks for the additional detail!", delay=0.01, color=Color.GREEN)
                    print()
            
        except Exception as e:
            # Silently fail - follow-up questions are optional
            pass

    def _analyze_professional_context(self, text, original_question=None, question_key=None, question_section=None):
        """
        Analyze text for professional context and generate relevant followup questions using GPT
        
        Args:
            text: User's answer
            original_question: The original question that was asked
            question_key: The key identifier for the question (e.g., 'job_history', 'technical_skills')
            question_section: The section this question belongs to (e.g., 'Experience', 'Skills')
        """
        try:
            # Base prompt for GPT
            base_prompt = f"""
            Analyze this professional response for a {self.job_role} position at the {self.resume_level} level.
            
            Original question: "{original_question if original_question else 'Not provided'}"
            User's answer: "{text}"
            """
            
            # Section-specific prompts
            if question_section == "Personal":
                analysis_prompt = base_prompt + f"""
                For personal information questions, check if:
                1. The answer is relevant to the question.
                2. All requested information (ACCORDING TO THE QUESTION) is provided 


                Generate specific followup question (Short and concise) only if essential information is missing or needs clarification.
                """
                
            elif question_section == "Summary" or question_key == "summary":
                analysis_prompt = base_prompt + f"""
                For a professional summary for a {self.resume_level} {self.job_role}, check if:
                1. The summary demonstrates relevant expertise for the role
                2. It highlights career achievements appropriate for their level
                3. It conveys their professional value proposition clearly
                4. It includes industry-specific keywords and terminology
                5. The tone matches the seniority level ({self.resume_level})
                
                Generate 1 specific followup question to help:
                - Add quantifiable achievements or metrics
                - Include relevant industry keywords or specializations
                - Highlight leadership or strategic contributions (for mid-level or executive)
                - Better articulate unique professional value
                """
                
            elif question_section == "Experience" or question_key in ["job_history", "achievements", "technical_impact", "leadership_impact", "business_impact", "analytical_impact", "people_impact", "financial_impact", "product_impact", "design_impact", "project_impact", "operational_impact", "customer_impact", "content_impact", "consulting_impact", "security_impact", "legal_impact", "healthcare_impact", "research_impact", "educational_impact"]:
                analysis_prompt = base_prompt + f"""
                For work experience details for a {self.job_role} position, check if:
                1. IMPORTANT - All essential job details are included (company names, positions, time periods) 
                2. Achievements are quantified with metrics where possible
                3. Responsibilities are described with action verbs
                4. Industry-specific skills and tools are mentioned
                5. There's progression or growth visible (especially for {self.resume_level} level)
                6. Impact and results are clearly articulated
                
                Generate 1 targeted followup question to help:
                - Cover All essential job details (company names, positions, time periods) if missing 
                - Quantify achievements with specific metrics (numbers, percentages, timelines)
                - Highlight specific technical skills or tools used (relevant to {self.job_role})
                - Demonstrate leadership or strategic contributions (if appropriate for {self.resume_level})
                - Show business impact or results
                - Fill gaps in employment timeline if any exist
                """
                
            elif question_section == "Education" or question_key in ["education", "certifications"]:
                analysis_prompt = base_prompt + f"""
                For education and certification details, check if:
                1. IMPORTANT - Degrees, institutions, and graduation dates are clearly specified IF MENTIONED. 
                2. Relevant certifications for a {self.job_role} position are included and clearly specified. 
                3. Key coursework or academic achievements relevant to the role are mentioned
                4. Any continuing education or professional development is highlighted
                
                Generate 1 specific followup question to help:
                - IMPORTANT - Cover and clarify all essential education details IF MENTIONED. (What degree if mentioned and not clearly specified, where, when, relevant courses taken) if missing
                - IMPORTANT - Include relevant coursework or specializations related to {self.job_role}
                - Highlight academic achievements or projects if appropriate
                - Clarify timeframes if missing
                - Identify industry-specific certifications that might be valuable to mention
                """
                
            elif question_key == "languages":
                analysis_prompt = base_prompt + f"""
                For language skills, check if:
                1. IMPORTANT - Languages are listed with proficiency levels
                2. IMPORTANT - Proficiency levels are specified (native, fluent, intermediate, etc.)
                Generate 1 followup question only if:
                - Proficiency levels are not specified (native, fluent, intermediate, etc.)
                """
                
            elif question_section == "Skills" or question_key in ["technical_skills", "soft_skills", "leadership_skills", "analytical_skills", "domain_knowledge", "business_skills", "tools_and_platforms", "marketing_skills", "sales_skills", "hr_skills", "pm_skills", "operations_skills", "design_skills", "writing_skills", "consulting_skills", "security_skills", "legal_skills", "clinical_skills", "research_skills", "teaching_skills"]:
                analysis_prompt = base_prompt + f"""
                For skills relevant to a {self.job_role} position, check if:
                1. Technical skills specific to the {self.job_role} field are included
                2. Soft skills that complement the technical abilities are mentioned
                3. Tools, software, or platforms are specified with proficiency levels where appropriate
                4. Skills are organized in a logical, scannable way for recruiters
                5. Skill set aligns with the seniority level ({self.resume_level})
                
                Generate 2-3 specific followup questions to help:
                - Identify any missing critical skills for a {self.job_role} position
                - Clarify proficiency levels for technical skills
                - Include specific tools or software relevant to the industry
                - Add measurable results achieved using specific skills
                - Highlight leadership or strategic skills (for mid-level or executive)
                """
                
            elif question_section == "Additional" or question_key in ["board_positions", "speaking", "industry_leadership", "projects", "professional_activities", "industry_contributions", "activities", "achievements", "additional_info"]:
                analysis_prompt = base_prompt + f"""
                For additional qualifications or achievements relevant to a {self.job_role}, check if:
                1. Information adds unique value beyond standard qualifications
                2. Relevant volunteer work, projects, or leadership roles are described
                3. Industry involvement or professional network activities are included
                4. Special accomplishments are quantified where possible
                
                Generate 1-2 specific followup questions to help:
                - Highlight unique aspects of their professional background
                - Quantify impact of additional activities
                - Connect additional experiences to the target {self.job_role} position
                - Identify transferable skills from these activities
                """
                
            else:
                # Default prompt for any other question types
                analysis_prompt = base_prompt + f"""
                Consider:
                1. What specific professional expertise or experience is mentioned?
                2. What technical or domain-specific details could be clarified?
                3. What achievements or impacts could be better quantified?
                4. What professional tools, methodologies, or systems are mentioned?
                5. What industry-specific knowledge is demonstrated?
                6. How does the answer relate to the original question, and what might be missing?
                
                Generate 2-3 specific, targeted followup questions that would help:
                - Better understand their professional expertise
                - Quantify their achievements
                - Clarify technical or domain-specific details
                - Highlight relevant tools or methodologies
                - Fill any gaps between what was asked and what was answered
                """
            
            # Final instructions for all question types
            analysis_prompt += """
            
            Format: Return ONLY the questions, one per line, without any other text.
            Make each question conversational, brief (under 15 words), and directly relevant to their response.
            Focus on areas where additional detail would strengthen their resume for this specific role.
            """
            
            # Get analysis from GPT
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional resume expert analyzing experience and generating targeted followup questions."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.7,
                max_tokens=200,
            )
            
            # Get the questions from the response
            questions = response.choices[0].message.content.strip().split('\n')
            
            # Clean up and filter questions
            questions = [q.strip() for q in questions if q.strip()]
            
            return questions
                
        except Exception as e:
            # If GPT analysis fails, fall back to basic template questions
            return self._generate_template_questions(text)

    def _generate_template_questions(self, text):
        """Generate template-based questions for employment history"""
        template_questions = []
        
        # Check for company mentions
        if any(word in text.lower() for word in ['company', 'worked at', 'employed at', 'position at']):
            template_questions.extend([
                "What was the duration of your employment?",
                "What was your exact role and title?",
                "What were your main responsibilities?",
                "Can you quantify any achievements (e.g., revenue growth, team size)?",
                "What was the company's industry and size?",
                "Did you receive any promotions or recognition?"
            ])
        
        # Check for project mentions
        if any(word in text.lower() for word in ['project', 'initiative', 'program']):
            template_questions.extend([
                "What was the project's scope and duration?",
                "What was your role in the project?",
                "What were the key outcomes or deliverables?",
                "How did you measure project success?",
                "What challenges did you overcome?"
            ])
        
        return template_questions

    def _get_followup_questions(self, text, original_question=None, question_key=None, question_section=None):
        """Get both professional and template-based followup questions"""
        # Get GPT-generated professional questions
        professional_questions = self._analyze_professional_context(text, original_question, question_key, question_section)
        
        # Get template questions for basic information
        template_questions = self._generate_template_questions(text)
        
        # Combine and deduplicate questions
        all_questions = list(set(professional_questions + template_questions))
        
        # Limit to most relevant questions
        return all_questions[:5]  # Return top 5 most relevant questions

    def _get_user_input(self, prompt, color=Color.WHITE):
        """Get user input with typing effect"""
        print_colored(prompt, color)
        type_text("> ", delay=0.01, color=Color.WHITE, end="")
        user_input = input()
        
        # Get followup questions based on user input
        followup_questions = self._get_followup_questions(user_input, prompt)
        if followup_questions:
            self.followup_questions.extend(followup_questions)
        
        return user_input


# Main execution block
if __name__ == "__main__":
    resume_builder = EnhancedResumeBuilder()
    resume_builder.welcome()