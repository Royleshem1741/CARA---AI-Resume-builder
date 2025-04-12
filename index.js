        // API Configuration
        const API_BASE_URL = 'https://cara-ai-resume-builder.onrender.com/api';

        // השלמה אוטומטית לשדה job-role
        const autocompleteStyle = `
        .autocomplete-container {
        position: relative;
        width: 100%;
        }

        .autocomplete-suggestions {
        position: absolute;
        border: 1px solid #ddd;
        border-top: none;
        border-radius: 0 0 4px 4px;
        z-index: 99;
        top: 100%;
        left: 0;
        right: 0;
        max-height: 200px;
        overflow-y: auto;
        background-color: white;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        .autocomplete-suggestion {
        padding: 10px;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        .autocomplete-suggestion:hover, .autocomplete-suggestion.selected {
        background-color: #f1f8fe;
        color: var(--primary-color);
        }
        `;

        // נוסיף את הסגנון לעמוד
        const styleElement = document.createElement('style');
        styleElement.textContent = autocompleteStyle;
        document.head.appendChild(styleElement);

        // רשימת תפקידים מבוססת על הקובץ שצורף
        const jobRoles = [
        "Software Developer",
        "Frontend Developer", 
        "Backend Developer",
        "Full Stack Developer",
        "Software Engineer",
        "DevOps Engineer",
        "Product Manager",
        "Product Owner",
        "Project Manager",
        "UX Designer",
        "UI Designer",
        "Data Analyst",
        "Data Scientist",
        "Marketing Manager",
        "Sales Manager",
        "Sales",
        "Director of Sales",
        "Team Lead",
        "Engineering Manager",
        "Director of Engineering",
        "Human Resources Manager",
        "HR Specialist",
        "Financial Analyst",
        "Accountant",
        "Financial Manager",
        "Operations Manager",
        "Customer Service Representative",
        "Customer Success Manager",
        "Content Writer",
        "Copywriter",
        "Consultant",
        "Cybersecurity Analyst",
        "Security Engineer",
        "Attorney",
        "Lawyer",
        "Legal Counsel",
        "Healthcare Manager",
        "Medical Professional",
        "Clinical Director",
        "Research Scientist",
        "Teacher",
        "Educator",
        "Instructor"
        ];

        // פונקציה המוסיפה השלמה אוטומטית לאלמנט הקלט
        function setupAutocomplete(inputElement) {
        // צור מיכל לעטיפת האלמנט והצעות ההשלמה
        const parentElement = inputElement.parentElement;
        const wrapper = document.createElement('div');
        wrapper.className = 'autocomplete-container';
        
        // העבר את האלמנט לתוך העטיפה
        parentElement.insertBefore(wrapper, inputElement);
        wrapper.appendChild(inputElement);
        
        // צור את מיכל ההצעות
        const suggestionsContainer = document.createElement('div');
        suggestionsContainer.className = 'autocomplete-suggestions';
        suggestionsContainer.style.display = 'none';
        wrapper.appendChild(suggestionsContainer);
        
        // מאזין לשינויים בשדה הקלט
        inputElement.addEventListener('input', function(e) {
            const value = this.value.toLowerCase();
            suggestionsContainer.innerHTML = '';
            
            if (!value) {
            suggestionsContainer.style.display = 'none';
            return;
            }
            
            // סנן את ההצעות הרלוונטיות
            const filteredSuggestions = jobRoles.filter(job => 
            job.toLowerCase().includes(value)
            ).slice(0, 8); // הגבל ל-8 הצעות מקסימום
            
            if (filteredSuggestions.length === 0) {
            suggestionsContainer.style.display = 'none';
            return;
            }
            
            // יצירת אלמנט עבור כל הצעה
            filteredSuggestions.forEach(suggestion => {
            const suggestionElement = document.createElement('div');
            suggestionElement.className = 'autocomplete-suggestion';
            suggestionElement.textContent = suggestion;
            
            // בעת לחיצה על הצעה - מילוי השדה
            suggestionElement.addEventListener('click', function() {
                inputElement.value = suggestion;
                suggestionsContainer.style.display = 'none';
            });
            
            suggestionsContainer.appendChild(suggestionElement);
            });
            
            suggestionsContainer.style.display = 'block';
        });
        
        // טיפול במקלדת (לבחירה עם חיצים ו-Enter)
        let selectedIndex = -1;
        
        inputElement.addEventListener('keydown', function(e) {
            const suggestions = suggestionsContainer.querySelectorAll('.autocomplete-suggestion');
            
            if (suggestions.length === 0) return;
            
            // מקש חץ למטה
            if (e.key === 'ArrowDown') {
            selectedIndex = (selectedIndex + 1) % suggestions.length;
            highlightSuggestion(suggestions, selectedIndex);
            e.preventDefault();
            } 
            // מקש חץ למעלה
            else if (e.key === 'ArrowUp') {
            selectedIndex = (selectedIndex - 1 + suggestions.length) % suggestions.length;
            highlightSuggestion(suggestions, selectedIndex);
            e.preventDefault();
            } 
            // מקש Enter
            else if (e.key === 'Enter' && selectedIndex > -1) {
            inputElement.value = suggestions[selectedIndex].textContent;
            suggestionsContainer.style.display = 'none';
            e.preventDefault();
            }
            // מקש Escape
            else if (e.key === 'Escape') {
            suggestionsContainer.style.display = 'none';
            selectedIndex = -1;
            }
        });
        
        // הסתרת ההצעות כשלוחצים מחוץ לאזור
        document.addEventListener('click', function(e) {
            if (!wrapper.contains(e.target)) {
            suggestionsContainer.style.display = 'none';
            selectedIndex = -1;
            }
        });
        
        // הדגשת ההצעה הנבחרת
        function highlightSuggestion(suggestions, index) {
            suggestions.forEach(s => s.classList.remove('selected'));
            if (index > -1) {
            suggestions[index].classList.add('selected');
            suggestions[index].scrollIntoView({ block: 'nearest' });
            }
        }
        }

        // יישום ההשלמה האוטומטית על שדה job-role
        document.addEventListener('DOMContentLoaded', function() {
        const jobRoleInput = document.getElementById('job-role');
        if (jobRoleInput) {
            setupAutocomplete(jobRoleInput);
        }
        });

        // פונקציה שמדמה הקלדה של טקסט אות אחר אות
        function typeText(element, text, speed = 30) {
            return new Promise((resolve) => {
                let i = 0;
                element.textContent = '';
                
                function type() {
                    if (i < text.length) {
                        element.textContent += text.charAt(i);
                        i++;
                        setTimeout(type, speed);
                    } else {
                        resolve();
                    }
                }
                
                type();
            });
        }


        // Main application class
        class ResumeBuilder {
            constructor() {
                this.userData = {};
                this.questions = [];
                this.currentQuestionIndex = 0;
                this.resumeLevel = "mid-level"; // Default level
                this.jobRole = "";
                this.userName = "";
                this.impliedSkills = {
                    technical_skills: [],
                    soft_skills: [],
                    domain_knowledge: [],
                    tools_and_platforms: []
                };
                this.confirmedSkills = {
                    technical_skills: [],
                    soft_skills: [],
                    domain_knowledge: [],
                    tools_and_platforms: []
                };
                this.resumeFilename = "";
                this.translatedFilename = "";
                
                this.initEventListeners();
            }
            
            // Initialize all event listeners
            initEventListeners() {
                // Welcome screen
                document.getElementById('start-interview-btn').addEventListener('click', () => this.startInterview());
                
                // Interview screen
                document.getElementById('next-question-btn').addEventListener('click', () => this.nextQuestion());
                document.getElementById('previous-question-btn').addEventListener('click', () => this.previousQuestion());
                document.getElementById('skip-question-btn').addEventListener('click', () => this.skipQuestion());
                document.getElementById('finish-interview-btn').addEventListener('click', () => this.finishInterview());
                document.getElementById('answer-input').addEventListener('input', () => this.checkAnswerForFollowup());
                
                // Review screen
                document.getElementById('back-to-interview-btn').addEventListener('click', () => this.showScreen('interview-screen'));
                document.getElementById('proceed-to-generate-btn').addEventListener('click', () => this.proceedToGenerate());
                
                // Generate screen
                document.getElementById('back-to-review-btn').addEventListener('click', () => this.showScreen('review-screen'));
                document.getElementById('generate-resume-btn').addEventListener('click', () => this.generateResume());
                
                // Results screen
                document.getElementById('open-resume-btn').addEventListener('click', () => this.openResumeInBrowser());
                document.getElementById('translate-resume-btn').addEventListener('click', () => this.openTranslateModal());
                document.getElementById('email-resume-btn').addEventListener('click', () => this.openEmailModal());
                
                // Email modal
                document.getElementById('close-email-modal').addEventListener('click', () => this.closeEmailModal());
                document.getElementById('close-email-instructions-btn').addEventListener('click', () => this.closeEmailModal());
                
                // Translate modal
                document.getElementById('close-translate-modal').addEventListener('click', () => this.closeTranslateModal());
                document.getElementById('cancel-translation-btn').addEventListener('click', () => this.closeTranslateModal());
                document.getElementById('start-translation-btn').addEventListener('click', () => this.translateResume());
                document.getElementById('translation-done-btn').addEventListener('click', () => this.closeTranslateModal());
                
                // Edit modal
                document.getElementById('close-edit-modal').addEventListener('click', () => this.closeEditModal());
                document.getElementById('cancel-edit-btn').addEventListener('click', () => this.closeEditModal());
                document.getElementById('save-edit-btn').addEventListener('click', () => this.saveEditedAnswer());
            }
            
            // API Methods
            async apiRequest(endpoint, method = 'GET', data = null) {
                try {
                    const url = `${API_BASE_URL}/${endpoint}`;
                    const options = {
                        method: method,
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    };
                    
                    if (data && (method === 'POST' || method === 'PUT')) {
                        options.body = JSON.stringify(data);
                    }
                    
                    const response = await fetch(url, options);
                    
                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.detail || 'API request failed');
                    }
                    
                    return await response.json();
                } catch (error) {
                    console.error('API Request Error:', error);
                    this.showNotification(error.message || 'Failed to connect to the server. Please try again.', 'error');
                    throw error;
                }
            }
            
            // Start the interview process
            async startInterview() {
                // Get user information
                this.userName = document.getElementById('user-name').value.trim();
                this.jobRole = document.getElementById('job-role').value.trim();
                this.resumeLevel = document.getElementById('experience-level').value;
                
                // Validate inputs
                if (!this.userName || !this.jobRole || !this.resumeLevel) {
                    this.showNotification('Please fill in all the fields', 'error');
                    return;
                }
                
                try {
                    // Initialize session on the backend
                    const initResponse = await this.apiRequest('initialize', 'POST', {
                        full_name: this.userName,
                        job_role: this.jobRole,
                        resume_level: this.resumeLevel
                    });
                    
                    // Save basic info to userData
                    this.userData['full_name'] = this.userName;
                    
                    // Get questions from the backend
                    const questionsResponse = await this.apiRequest('questions');
                    this.questions = questionsResponse.questions;
                    
                    // Show interview screen
                    this.showScreen('interview-screen');
                    
                    // Update UI with first question
                    this.updateQuestionUI();
                } catch (error) {
                    // Error is already handled in apiRequest
                    console.error('Failed to start interview:', error);
                }
            }
            
            // Update the question UI
            async updateQuestionUI() {
                try {
                    // Get the current question details from the API
                    const questionResponse = await this.apiRequest(`question/${this.currentQuestionIndex}`);
                    
                    // Update question number and text
                    document.getElementById('current-question').textContent = this.currentQuestionIndex + 1;
                    document.getElementById('total-questions').textContent = this.questions.length;
                    
                    // Add section name next to question number (in a subtle way)
                    const questionNumberElement = document.querySelector('.question-number');
                    // Check if section span already exists and remove it if it does
                    const existingSection = questionNumberElement.querySelector('.question-section');
                    if (existingSection) {
                        existingSection.remove();
                    }
                    
                    // Create and add the section element
                    const sectionElement = document.createElement('span');
                    sectionElement.textContent = ` - ${questionResponse.section}`;
                    sectionElement.className = 'question-section';
                    questionNumberElement.appendChild(sectionElement);
                    
                    document.getElementById('question-text').textContent = questionResponse.question;
                    
                    // Get textarea and set its value
                    const answerInput = document.getElementById('answer-input');
                    answerInput.value = questionResponse.current_answer || '';
                    
                    // Focus on the textarea
                    answerInput.focus();
                    
                    // Hide feedback initially
                    document.getElementById('feedback-container').style.display = 'none';
                    
                    // Update progress bar
                    const progressPercentage = ((this.currentQuestionIndex + 1) / this.questions.length) * 100;
                    document.getElementById('progress-bar').style.width = `${progressPercentage}%`;
                    
                    // Update button visibility
                    document.getElementById('previous-question-btn').style.display = 
                        this.currentQuestionIndex > 0 ? 'inline-block' : 'none';
                    
                    document.getElementById('finish-interview-btn').style.display = 
                        this.currentQuestionIndex >= Math.floor(this.questions.length * 0.75) ? 'inline-block' : 'none';
                } catch (error) {
                    console.error('Failed to update question UI:', error);
                }
            }
            
            async nextQuestion() {
                // שמירת השאלה והתשובה הנוכחית
                const currentQuestion = this.questions[this.currentQuestionIndex];
                const answer = document.getElementById('answer-input').value.trim();
                
                try {
                    // השבת את כל כפתורי הניווט בזמן עיבוד
                    const nextButton = document.getElementById('next-question-btn');
                    const skipButton = document.getElementById('skip-question-btn');
                    const prevButton = document.getElementById('previous-question-btn');
                    
                    // השבתת כפתור Next
                    nextButton.disabled = true;
                    nextButton.style.opacity = "0.6";
                    nextButton.style.cursor = "not-allowed";
                    
                    // השבתת כפתור Skip
                    skipButton.disabled = true;
                    skipButton.style.opacity = "0.6";
                    skipButton.style.cursor = "not-allowed";
                    
                    // השבתת כפתור Previous
                    prevButton.disabled = true;
                    prevButton.style.opacity = "0.6";
                    prevButton.style.cursor = "not-allowed";
                    
                    // הצג את אינדיקטור הטעינה והסתר את תוכן הפידבק
                    const feedbackContainer = document.getElementById('feedback-container');
                    feedbackContainer.style.display = 'block';
                    document.getElementById('feedback-loading').style.display = 'block';
                    document.getElementById('feedback-content') && (document.getElementById('feedback-content').style.display = 'none');
                    document.getElementById('feedback-text').style.display = 'none';
                    
                    // שלח את התשובה לבקאנד
                    const saveResponse = await this.apiRequest(`answer/${this.currentQuestionIndex}`, 'POST', {
                        key: currentQuestion.key,
                        answer: answer
                    });
                    
                    // שמור מקומית
                    this.userData[currentQuestion.key] = answer;
                    
                    // הסתר את אינדיקטור הטעינה
                    document.getElementById('feedback-loading').style.display = 'none';
                    
                    // בדוק אם יש פידבק
                    if (saveResponse.feedback) {
                        const feedbackTextElement = document.getElementById('feedback-text');
                        feedbackTextElement.style.display = 'inline-block';
                        
                        if (document.getElementById('feedback-content')) {
                            document.getElementById('feedback-content').style.display = 'block';
                        }
                        
                        // הקלדת הטקסט של הפידבק בהדרגה
                        await typeText(feedbackTextElement, saveResponse.feedback.message);
                        
                        // אם יש גם שאלת מעקב, נמתין רגע קל נוסף לפני שנציג אותה
                        if (saveResponse.followup) {
                            // המתן 500 מילישניות נוספות אחרי סיום ההקלדה לפני הצגת שאלת המעקב
                            setTimeout(() => {
                                this.showFollowUpQuestion(saveResponse.followup, currentQuestion.key);
                                // הפעל מחדש את כל הכפתורים אחרי הצגת שאלת המעקב
                                this.enableNavigationButtons();
                            }, 500);
                            return; // אל תמשיך לשאלה הבאה עד שהמעקב יושלם
                        }
                    } else {
                        // אם אין פידבק, הסתר את המיכל
                        feedbackContainer.style.display = 'none';
                        
                        // בדוק אם יש שאלת מעקב
                        if (saveResponse.followup) {
                            this.showFollowUpQuestion(saveResponse.followup, currentQuestion.key);
                            // הפעל מחדש את הכפתורים אחרי הצגת שאלת המעקב
                            this.enableNavigationButtons();
                            return; // אל תמשיך לשאלה הבאה עד שהמעקב יושלם
                        }
                    }
                    
                    // הפעל מחדש את כל כפתורי הניווט
                    this.enableNavigationButtons();
                    
                    // תהליך רגיל - המשך לשאלה הבאה
                    // בדוק אם הגענו לסוף
                    if (this.currentQuestionIndex >= this.questions.length - 1) {
                        this.finishInterview();
                        return;
                    }
                    
                    // עבור לשאלה הבאה
                    this.currentQuestionIndex++;
                    this.updateQuestionUI();
                } catch (error) {
                    // הסתר את אינדיקטור הטעינה במקרה של שגיאה
                    document.getElementById('feedback-loading').style.display = 'none';
                    feedbackContainer.style.display = 'none';
                    
                    // הפעל מחדש את כל כפתורי הניווט גם במקרה של שגיאה
                    this.enableNavigationButtons();
                    
                    if (error.message.includes('Invalid email format')) {
                        this.showNotification('Please enter a valid email address', 'error');
                    } else {
                        console.error('Failed to save answer:', error);
                    }
                }
            }
            
            // פונקציה חדשה להפעלה מחדש של כל כפתורי הניווט
            enableNavigationButtons() {
                const nextButton = document.getElementById('next-question-btn');
                const skipButton = document.getElementById('skip-question-btn');
                const prevButton = document.getElementById('previous-question-btn');
                
                // הפעלת כפתור Next
                nextButton.disabled = false;
                nextButton.style.opacity = "1";
                nextButton.style.cursor = "pointer";
                
                // הפעלת כפתור Skip
                skipButton.disabled = false;
                skipButton.style.opacity = "1";
                skipButton.style.cursor = "pointer";
                
                // הפעלת כפתור Previous
                prevButton.disabled = false;
                prevButton.style.opacity = "1";
                prevButton.style.cursor = "pointer";
            }

            
            // Handle follow-up questions
            showFollowUpQuestion(followup, originalKey) {
                // Create modal or inline display for follow-up
                const followupModal = document.createElement('div');
                followupModal.className = 'follow-up-container';
                
                const followupQuestion = document.createElement('div');
                followupQuestion.className = 'follow-up-question';
                followupQuestion.textContent = followup.message;
                
                const followupInput = document.createElement('textarea');
                followupInput.className = 'follow-up-input';
                followupInput.placeholder = 'Type your answer here...';
                
                const followupActions = document.createElement('div');
                followupActions.className = 'follow-up-actions';
                
                const skipBtn = document.createElement('button');
                skipBtn.className = 'btn btn-outline';
                skipBtn.textContent = 'Skip';
                skipBtn.addEventListener('click', () => {
                    document.body.removeChild(followupModal);
                    this.proceedAfterFollowUp();
                });
                
                const submitBtn = document.createElement('button');
                submitBtn.className = 'btn btn-primary';
                submitBtn.textContent = 'Submit';
                submitBtn.addEventListener('click', async () => {
                    const followupAnswer = followupInput.value.trim();
                    if (followupAnswer) {
                        try {
                            // Send follow-up answer based on type
                            await this.apiRequest(`follow-up/${followup.type}`, 'POST', {
                                answer: followupAnswer,
                                original_key: originalKey,
                                next_question: followup.additional_questions ? followup.additional_questions[0] : null
                            });
                            
                            this.showNotification('Additional information saved', 'success');
                        } catch (error) {
                            console.error('Failed to save follow-up:', error);
                        }
                    }
                    
                    document.body.removeChild(followupModal);
                    this.proceedAfterFollowUp();
                });
                
                followupActions.appendChild(skipBtn);
                followupActions.appendChild(submitBtn);
                
                followupModal.appendChild(followupQuestion);
                followupModal.appendChild(followupInput);
                followupModal.appendChild(followupActions);
                
                document.body.appendChild(followupModal);
            }

            // Continue after follow-up is handled
            proceedAfterFollowUp() {
                // Check if we're at the end
                if (this.currentQuestionIndex >= this.questions.length - 1) {
                    this.finishInterview();
                    return;
                }
                
                // Move to next question
                this.currentQuestionIndex++;
                this.updateQuestionUI();
            }

            // Navigate to the previous question
            previousQuestion() {
                if (this.currentQuestionIndex > 0) {
                    this.currentQuestionIndex--;
                    this.updateQuestionUI();
                }
            }
            
            // Skip the current question
            skipQuestion() {
                // Check if we're at the end
                if (this.currentQuestionIndex >= this.questions.length - 1) {
                    this.finishInterview();
                    return;
                }
                
                // Move to next question
                this.currentQuestionIndex++;
                this.updateQuestionUI();
                
                // Show notification
                this.showNotification('Question skipped. You can come back to it later.', 'info');
            }
            
            // Finish the interview and go to review screen
            async finishInterview() {
                // Save current answer if any
                const currentQuestion = this.questions[this.currentQuestionIndex];
                const answer = document.getElementById('answer-input').value.trim();
                
                if (answer) {
                    try {
                        // Send answer to the backend
                        await this.apiRequest(`answer/${this.currentQuestionIndex}`, 'POST', {
                            key: currentQuestion.key,
                            answer: answer
                        });
                        
                        // Save locally as well
                        this.userData[currentQuestion.key] = answer;
                    } catch (error) {
                        console.error('Failed to save final answer:', error);
                    }
                }
                
                try {
                    // Get all answers from the backend to ensure we have the latest data
                    const answersResponse = await this.apiRequest('answers');
                    this.userData = answersResponse.answers;
                    
                    // Generate review items
                    this.populateReviewScreen();
                    
                    // Show review screen
                    this.showScreen('review-screen');
                } catch (error) {
                    console.error('Failed to get answers for review:', error);
                }
            }
            
            // Populate the review screen with user's answers
            populateReviewScreen() {
                const reviewContainer = document.getElementById('review-items-container');
                reviewContainer.innerHTML = '';
                
                // Group questions by section
                const sectionMap = {};
                
                this.questions.forEach(question => {
                    if (!sectionMap[question.section]) {
                        sectionMap[question.section] = [];
                    }
                    sectionMap[question.section].push(question);
                });
                
                // Create review items by section
                for (const section in sectionMap) {
                    const sectionHeader = document.createElement('h3');
                    sectionHeader.textContent = section;
                    reviewContainer.appendChild(sectionHeader);
                    
                    sectionMap[section].forEach(question => {
                        const answer = this.userData[question.key] || '';
                        
                        if (answer || section === 'Personal') { // Always show personal info items
                            const reviewItem = document.createElement('div');
                            reviewItem.className = 'review-item';
                            
                            const reviewQuestion = document.createElement('div');
                            reviewQuestion.className = 'review-question';
                            reviewQuestion.textContent = question.question.split('\n')[0]; // Just the first line of question
                            
                            const reviewAnswer = document.createElement('div');
                            reviewAnswer.className = 'review-answer';
                            reviewAnswer.textContent = answer || 'Not provided';
                            
                            const reviewActions = document.createElement('div');
                            reviewActions.className = 'review-actions';
                            
                            const editBtn = document.createElement('button');
                            editBtn.className = 'btn btn-small btn-outline';
                            editBtn.textContent = 'Edit';
                            editBtn.addEventListener('click', () => this.openEditModal(question, answer));
                            
                            reviewActions.appendChild(editBtn);
                            reviewItem.appendChild(reviewQuestion);
                            reviewItem.appendChild(reviewAnswer);
                            reviewItem.appendChild(reviewActions);
                            
                            reviewContainer.appendChild(reviewItem);
                        }
                    });
                }
            }
            
            // Proceed to generate screen
            async proceedToGenerate() {
                try {
                    // Analyze implied skills via the backend
                    const skillsResponse = await this.apiRequest('analyze-skills', 'POST');
                    
                    if (skillsResponse.implied_skills) {
                        this.impliedSkills = skillsResponse.implied_skills;
                        
                        // Populate the implied skills section
                        this.populateImpliedSkills();
                        document.getElementById('implied-skills-section').classList.remove('hidden');
                    } else {
                        document.getElementById('implied-skills-section').classList.add('hidden');
                    }
                    
                    // Show generate screen
                    this.showScreen('generate-screen');
                } catch (error) {
                    console.error('Failed to analyze skills:', error);
                    // Still proceed to generate screen even if skills analysis fails
                    this.showScreen('generate-screen');
                }
            }
            
            // Populate the implied skills section UI
            populateImpliedSkills() {
                const categories = {
                    'technical-skills-list': this.impliedSkills.technical_skills,
                    'soft-skills-list': this.impliedSkills.soft_skills,
                    'domain-knowledge-list': this.impliedSkills.domain_knowledge,
                    'tools-platforms-list': this.impliedSkills.tools_and_platforms
                };
                
                // Clear existing skills
                for (const listId in categories) {
                    const list = document.getElementById(listId);
                    list.innerHTML = '';
                    
                    // Hide empty categories
                    const category = list.closest('.skill-category');
                    if (categories[listId].length === 0) {
                        category.style.display = 'none';
                    } else {
                        category.style.display = 'block';
                    }
                    
                    // Add each skill as a clickable item
                    categories[listId].forEach(skill => {
                        const skillItem = document.createElement('div');
                        skillItem.className = 'skill-item';
                        skillItem.textContent = skill;
                        skillItem.dataset.skill = skill;
                        skillItem.dataset.category = listId.replace('-list', '');
                        
                        // Make skills selectable
                        skillItem.addEventListener('click', () => {
                            skillItem.classList.toggle('selected');
                            this.updateConfirmedSkills();
                        });
                        
                        list.appendChild(skillItem);
                    });
                }
            }
            
            // Update the list of confirmed skills based on selection
            updateConfirmedSkills() {
                // Reset confirmed skills
                this.confirmedSkills = {
                    technical_skills: [],
                    soft_skills: [],
                    domain_knowledge: [],
                    tools_and_platforms: []
                };
                
                // Get all selected skills
                const selectedSkills = document.querySelectorAll('.skill-item.selected');
                selectedSkills.forEach(item => {
                    const category = item.dataset.category;
                    const skill = item.dataset.skill;
                    
                    switch(category) {
                        case 'technical-skills':
                            this.confirmedSkills.technical_skills.push(skill);
                            break;
                        case 'soft-skills':
                            this.confirmedSkills.soft_skills.push(skill);
                            break;
                        case 'domain-knowledge':
                            this.confirmedSkills.domain_knowledge.push(skill);
                            break;
                        case 'tools-platforms':
                            this.confirmedSkills.tools_and_platforms.push(skill);
                            break;
                    }
                });
            }
            
            // Generate the resume
            // עדכון הפונקציה generateResume()
            async generateResume() {
                // Get resume format and style
                const resumeFormat = document.getElementById('resume-format').value;
                const resumeStyle = document.getElementById('resume-style').value;
                
                // Update confirmed skills
                this.updateConfirmedSkills();
                
                // Show loading screen
                this.showScreen('results-screen');
                document.getElementById('resume-loading').classList.remove('hidden');
                document.getElementById('resume-success').classList.add('hidden');
                
                try {
                    // Call the API to generate the resume
                    const generateResponse = await this.apiRequest('generate-resume', 'POST', {
                        format: resumeFormat,
                        style: resumeStyle,
                        confirmed_skills: this.confirmedSkills
                    });
                    
                    // Save the filename for later use
                    this.resumeFilename = generateResponse.filename;
                    
                    // Update UI
                    document.getElementById('resume-loading').classList.add('hidden');
                    document.getElementById('resume-success').classList.remove('hidden');
                    document.getElementById('resume-filename').textContent = this.resumeFilename;
                    
                    // Add career tips if provided
                    if (generateResponse.career_tips) {
                        this.displayCareerTips(generateResponse.career_tips);
                    }
                    
                    // הורדה אוטומטית של הקובץ אם יש לנו URL להורדה
                    if (generateResponse.download_url) {
                        // מחכים רגע קט כדי לתת לממשק להתעדכן לפני ההורדה
                        setTimeout(() => {
                            // יצירת אלמנט קישור סמוי להורדה
                            const downloadLink = document.createElement('a');
                            downloadLink.href = `${API_BASE_URL}${generateResponse.download_url}`;
                            downloadLink.style.display = 'none';
                            downloadLink.setAttribute('download', this.resumeFilename);
                            
                            // הוספה לעמוד, לחיצה והסרה
                            document.body.appendChild(downloadLink);
                            downloadLink.click();
                            document.body.removeChild(downloadLink);
                            
                            // הצגת הודעה למשתמש
                            this.showNotification('Resume download started automatically', 'success');
                        }, 1000);
                    }
                    
                } catch (error) {
                    console.error('Failed to generate resume:', error);
                    this.showNotification('Failed to generate resume. Please try again.', 'error');
                    
                    // Show a basic success view anyway for demo purposes
                    document.getElementById('resume-loading').classList.add('hidden');
                    document.getElementById('resume-success').classList.remove('hidden');
                    document.getElementById('resume-filename').textContent = `${this.userName.replace(' ', '_').toLowerCase()}_resume.${resumeFormat}`;
                }
            }
            
            // Display career tips
            displayCareerTips(tips) {
                const tipsContainer = document.getElementById('career-tips-container');
                tipsContainer.innerHTML = '';
                
                const tipIcons = ['fa-comment', 'fa-lightbulb', 'fa-chart-line', 'fa-search'];
                
                tips.forEach((tip, index) => {
                    const tipItem = document.createElement('div');
                    tipItem.className = 'tip-item';
                    
                    const icon = tipIcons[index % tipIcons.length];
                    
                    tipItem.innerHTML = `
                        <div class="tip-icon">
                            <i class="fas ${icon}"></i>
                        </div>
                        <div class="tip-content">
                            <div class="tip-text">${tip}</div>
                        </div>
                    `;
                    
                    tipsContainer.appendChild(tipItem);
                });
            }
            
            // Open resume in browser
            openResumeInBrowser() {
                // This would depend on the specific implementation of your backend
                // For now, just show a notification
                this.showNotification('Opening resume in browser...', 'info');
                
                // In a real implementation, you might do something like:
                // window.open('/open-resume?filename=' + encodeURIComponent(this.resumeFilename), '_blank');
            }
            
            // Open the translate modal
            openTranslateModal() {
                document.getElementById('translate-modal').style.display = 'block';
                document.getElementById('translation-loading').classList.add('hidden');
                document.getElementById('translation-success').classList.add('hidden');
                document.getElementById('start-translation-btn').classList.remove('hidden');
                document.getElementById('translation-done-btn').classList.add('hidden');
            }

            //פונקציה לתרגום קורות החיים
            async translateResume() {
                const targetLanguage = document.getElementById('target-language').value;
                
                if (!targetLanguage) {
                    this.showNotification('Please select a language for translation', 'error');
                    return;
                }
                
                // Show loading
                document.getElementById('translation-loading').classList.remove('hidden');
                document.getElementById('start-translation-btn').classList.add('hidden');
                
                try {
                    // Call API to translate
                    const translateResponse = await this.apiRequest('translate-resume', 'POST', {
                        filename: this.resumeFilename,
                        target_language: targetLanguage
                    });
                    
                    // Update UI with success
                    document.getElementById('translation-loading').classList.add('hidden');
                    document.getElementById('translation-success').classList.remove('hidden');
                    document.getElementById('translation-done-btn').classList.remove('hidden');
                    
                    // Set translated info
                    this.translatedFilename = translateResponse.translated_filename;
                    document.getElementById('translated-language').textContent = targetLanguage;
                    document.getElementById('translated-filename').textContent = this.translatedFilename;
                    
                    // שמירת ה-URL להורדה
                    this.translatedDownloadUrl = translateResponse.download_url;
                    
                    // הוספת כפתור להורדת התרגום אם לא קיים
                    if (!document.getElementById('download-translated-btn')) {
                        const downloadTranslatedBtn = document.createElement('button');
                        downloadTranslatedBtn.id = 'download-translated-btn';
                        downloadTranslatedBtn.className = 'btn btn-primary mt-3';
                        downloadTranslatedBtn.textContent = 'Download Translated Resume';
                        downloadTranslatedBtn.addEventListener('click', () => this.downloadTranslatedResume());
                        
                        // הוספת הכפתור לתוך האלמנט המתאים
                        const translationSuccess = document.getElementById('translation-success');
                        translationSuccess.appendChild(downloadTranslatedBtn);
                    }
                    
                    // התחלת הורדה אוטומטית אחרי רגע קצר
                    setTimeout(() => {
                        this.downloadTranslatedResume();
                    }, 1500);
                    
                } catch (error) {
                    console.error('Failed to translate resume:', error);
                    this.showNotification('Failed to translate resume. Please try again.', 'error');
                    
                    // Hide loading and show the start button again
                    document.getElementById('translation-loading').classList.add('hidden');
                    document.getElementById('start-translation-btn').classList.remove('hidden');
                }
            }

            // הוספת פונקציה חדשה להורדת התרגום
            downloadTranslatedResume() {
                try {
                    // יצירת קישור להורדת התרגום
                    const downloadUrl = `${API_BASE_URL}${this.translatedDownloadUrl}`;
                    
                    // יצירת אלמנט קישור סמוי להורדה
                    const downloadLink = document.createElement('a');
                    downloadLink.href = downloadUrl;
                    downloadLink.style.display = 'none';
                    downloadLink.setAttribute('download', this.translatedFilename);
                    
                    // הוספה לעמוד, לחיצה והסרה
                    document.body.appendChild(downloadLink);
                    downloadLink.click();
                    document.body.removeChild(downloadLink);
                    
                    this.showNotification('Translation download started', 'success');
                } catch (error) {
                    console.error('Failed to download translated resume:', error);
                    this.showNotification('Failed to download the translated resume. Please try again.', 'error');
                }
            }

            // עדכון פונקציית closeTranslateModal
            closeTranslateModal() {
                document.getElementById('translate-modal').style.display = 'none';
                // מחיקת כפתור ההורדה המתורגמת אם קיים
                const downloadBtn = document.getElementById('download-translated-btn');
                if (downloadBtn) {
                    downloadBtn.remove();
                }
            }

            // Open the email modal
            openEmailModal() {
                document.getElementById('email-modal').style.display = 'block';
                
                // Fill in user email if available
                const userEmail = this.userData.email || '';
                document.getElementById('user-email').textContent = userEmail;
                document.getElementById('outlook-user-email').textContent = userEmail;
                
                // Fill in job role
                document.getElementById('email-job-role').textContent = this.jobRole;
                document.getElementById('outlook-job-role').textContent = this.jobRole;
                
                // Fill in filename
                document.getElementById('email-filename').textContent = this.resumeFilename;
                document.getElementById('outlook-filename').textContent = this.resumeFilename;
            }
            
            // Close the email modal
            closeEmailModal() {
                document.getElementById('email-modal').style.display = 'none';
            }
            
            // Open edit modal
            openEditModal(question, answer) {
                document.getElementById('edit-modal').style.display = 'block';
                document.getElementById('edit-question-label').textContent = question.question.split('\n')[0];
                document.getElementById('edit-answer-input').value = answer;
                
                // Store the question key for saving
                document.getElementById('edit-answer-input').dataset.questionKey = question.key;
                document.getElementById('edit-answer-input').dataset.questionIndex = this.findQuestionIndex(question.key);
            }
            
            // Find the question index by key
            findQuestionIndex(key) {
                return this.questions.findIndex(q => q.key === key);
            }
            
            // Close edit modal
            closeEditModal() {
                document.getElementById('edit-modal').style.display = 'none';
            }
            
            // Save edited answer
            async saveEditedAnswer() {
                const input = document.getElementById('edit-answer-input');
                const questionKey = input.dataset.questionKey;
                const questionIndex = input.dataset.questionIndex;
                const newAnswer = input.value.trim();
                
                try {
                    // Send updated answer to the backend
                    await this.apiRequest(`answer/${questionIndex}`, 'POST', {
                        key: questionKey,
                        answer: newAnswer
                    });
                    
                    // Update user data locally
                    this.userData[questionKey] = newAnswer;
                    
                    // Close modal
                    this.closeEditModal();
                    
                    // Update review screen
                    this.populateReviewScreen();
                    
                    // Show notification
                    this.showNotification('Your answer has been updated', 'success');
                } catch (error) {
                    if (error.message.includes('Invalid email format')) {
                        this.showNotification('Please enter a valid email address', 'error');
                    } else {
                        console.error('Failed to save edited answer:', error);
                        this.showNotification('Failed to save your changes. Please try again.', 'error');
                    }
                }
            }
            
            // Check for follow-up questions based on answer
            checkAnswerForFollowup() {
                // This would be more sophisticated when connected to your backend
                // For now, we'll implement a simplified version
                const currentQuestion = this.questions[this.currentQuestionIndex];
                const answer = document.getElementById('answer-input').value.trim();
                
                if (currentQuestion.key === 'job_history' && answer.length > 50) {
                    // Simple check if the answer mentions dates
                    if (!answer.match(/\b(19|20)\d{2}\b/) && !answer.match(/\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b/i)) {
                        // Show feedback about missing dates
                        const feedbackContainer = document.getElementById('feedback-container');
                        feedbackContainer.style.display = 'block';
                        document.getElementById('feedback-text').textContent = 
                            "Tip: Consider including specific dates for each position to strengthen your work history.";
                    } else {
                        // Hide feedback if dates are found
                        document.getElementById('feedback-container').style.display = 'none';
                    }
                }
            }
            
            // Switch between screens
            showScreen(screenId) {
                // Hide all screens
                document.querySelectorAll('.welcome-screen, .interview-screen, .review-screen, .generate-screen, .results-screen').forEach(screen => {
                    screen.classList.remove('active-screen');
                });
                
                // Show selected screen
                document.getElementById(screenId).classList.add('active-screen');
                
                // Scroll to top
                window.scrollTo(0, 0);
            }
            
            // Show notification
            showNotification(message, type = 'success') {
                const notification = document.getElementById('notification');
                document.getElementById('notification-text').textContent = message;
                
                // Set notification color based on type
                if (type === 'error') {
                    notification.style.backgroundColor = '#e74c3c';
                } else if (type === 'info') {
                    notification.style.backgroundColor = '#3498db';
                } else {
                    notification.style.backgroundColor = '#2ecc71';
                }
                
                // Show notification
                notification.classList.add('show');
                
                // Hide after 3 seconds
                setTimeout(() => {
                    notification.classList.remove('show');
                }, 3000);
            }
        }
        
        // Initialize the application when the DOM is fully loaded
        document.addEventListener('DOMContentLoaded', () => {
            const resumeBuilder = new ResumeBuilder();
        });

        // קוד לולידציה של שדות הטופס
        function setupFieldValidation() {
            // השדות שצריכים ולידציה
            const fieldsToValidate = [
                {
                    id: 'user-name',
                    validator: (value) => {
                        // בדיקה שהשם מכיל רק אותיות, רווחים, גרש וגרשיים, מקפים ונקודות (ללא מספרים וסימנים מיוחדים אחרים)
                        return /^[a-zA-Zא-ת\s.'"-]+$/.test(value);
                    }
                },
                {
                    id: 'job-role',
                    validator: (value) => {
                        // בדיקה שהתפקיד מכיל רק אותיות, רווחים, מספרים, מקפים ופסיקים
                        return /^[a-zA-Zא-ת0-9\s,.&()-]+$/.test(value);
                    }
                }
            ];

            // מעבר על כל השדות והוספת אירועי ולידציה
            fieldsToValidate.forEach(field => {
                const inputElement = document.getElementById(field.id);
                if (!inputElement) return;

                // יצירת אלמנט סימון (ישאר בלתי נראה בהתחלה)
                const indicatorElement = document.createElement('span');
                indicatorElement.className = 'validation-indicator';
                indicatorElement.style.position = 'absolute';
                indicatorElement.style.right = '10px';
                indicatorElement.style.top = '50%';
                indicatorElement.style.transform = 'translateY(-50%)';
                indicatorElement.style.display = 'none';
                
                // יצירת מיכל יחסי לאינדיקטור
                const containerDiv = document.createElement('div');
                containerDiv.style.position = 'relative';
                containerDiv.style.display = 'block';
                
                // העברת ה-input למיכל החדש
                inputElement.parentNode.insertBefore(containerDiv, inputElement);
                containerDiv.appendChild(inputElement);
                
                // הוספת האינדיקטור למיכל
                containerDiv.appendChild(indicatorElement);

                // הוספת אירוע בדיקה כשהמשתמש יוצא מהשדה
                inputElement.addEventListener('blur', function() {
                    const value = this.value.trim();
                    
                    // אם השדה ריק, הסתר את האינדיקטור
                    if (value === '') {
                        indicatorElement.style.display = 'none';
                        inputElement.style.borderColor = ''; // מחזיר לסגנון ברירת המחדל
                        return;
                    }

                    // הפעלת הולידציה והצגת האינדיקטור המתאים
                    const isValid = field.validator(value);
                    
                    if (isValid) {
                        // סימון וי ירוק
                        indicatorElement.innerHTML = '<i class="fas fa-check" style="color: #2ecc71;"></i>';
                        inputElement.style.borderColor = ''; // ללא מסגרת ירוקה
                    } else {
                        // סימון איקס אדום
                        indicatorElement.innerHTML = '<i class="fas fa-times" style="color: #e74c3c;"></i>';
                        inputElement.style.borderColor = '#e74c3c';
                    }
                    
                    indicatorElement.style.display = 'inline';
                });

                // תיקון המראה כאשר המשתמש מתחיל להקליד שוב
                inputElement.addEventListener('focus', function() {
                    inputElement.style.borderColor = 'var(--primary-color)';
                });
            });
        }

        // להפעיל את הולידציה לאחר טעינת העמוד
        document.addEventListener('DOMContentLoaded', function() {
            setupFieldValidation();
        });
              
