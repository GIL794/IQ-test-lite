/**
 * IQ Test Lite - Frontend Application
 * Vanilla JavaScript implementation
 */

// API Configuration
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : '';

// Application State
let testItems = [];
let currentQuestionIndex = 0;
let userAnswers = [];

// DOM Elements
const welcomeScreen = document.getElementById('welcomeScreen');
const testScreen = document.getElementById('testScreen');
const resultsScreen = document.getElementById('resultsScreen');
const loadingSpinner = document.getElementById('loadingSpinner');

const startBtn = document.getElementById('startBtn');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const submitBtn = document.getElementById('submitBtn');
const retakeBtn = document.getElementById('retakeBtn');

const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const questionText = document.getElementById('questionText');
const optionsContainer = document.getElementById('optionsContainer');

const iqScore = document.getElementById('iqScore');
const rawScore = document.getElementById('rawScore');
const percentile = document.getElementById('percentile');
const description = document.getElementById('description');
const resultsDisclaimer = document.getElementById('resultsDisclaimer');

// Event Listeners
startBtn.addEventListener('click', startTest);
prevBtn.addEventListener('click', previousQuestion);
nextBtn.addEventListener('click', nextQuestion);
submitBtn.addEventListener('click', submitTest);
retakeBtn.addEventListener('click', resetTest);

// Initialize
async function startTest() {
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE_URL}/api/test-items`);
        if (!response.ok) {
            throw new Error('Failed to load test items');
        }
        const data = await response.json();
        testItems = data.items;
        
        // Initialize user answers array
        userAnswers = new Array(testItems.length).fill(null);
        currentQuestionIndex = 0;
        
        showScreen('test');
        displayQuestion();
    } catch (error) {
        console.error('Error loading test:', error);
        alert('Failed to load test. Please try again.');
    } finally {
        showLoading(false);
    }
}

// Display current question
function displayQuestion() {
    const question = testItems[currentQuestionIndex];
    
    // Update progress
    const progress = ((currentQuestionIndex + 1) / testItems.length) * 100;
    progressFill.style.width = `${progress}%`;
    progressText.textContent = `Question ${currentQuestionIndex + 1} of ${testItems.length}`;
    
    // Update question text
    questionText.textContent = question.question;
    
    // Create options
    optionsContainer.innerHTML = '';
    question.options.forEach((option, index) => {
        const optionDiv = document.createElement('div');
        optionDiv.className = 'option';
        optionDiv.textContent = option;
        optionDiv.dataset.index = index;
        
        // Highlight if already selected
        if (userAnswers[currentQuestionIndex] === index) {
            optionDiv.classList.add('selected');
        }
        
        optionDiv.addEventListener('click', () => selectOption(index));
        optionsContainer.appendChild(optionDiv);
    });
    
    // Update navigation buttons
    prevBtn.disabled = currentQuestionIndex === 0;
    
    if (currentQuestionIndex === testItems.length - 1) {
        nextBtn.style.display = 'none';
        submitBtn.style.display = 'block';
    } else {
        nextBtn.style.display = 'block';
        submitBtn.style.display = 'none';
    }
}

// Select an option
function selectOption(index) {
    userAnswers[currentQuestionIndex] = index;
    
    // Update UI
    const options = optionsContainer.querySelectorAll('.option');
    options.forEach((option, i) => {
        if (i === index) {
            option.classList.add('selected');
        } else {
            option.classList.remove('selected');
        }
    });
}

// Navigate to previous question
function previousQuestion() {
    if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        displayQuestion();
    }
}

// Navigate to next question
function nextQuestion() {
    if (currentQuestionIndex < testItems.length - 1) {
        currentQuestionIndex++;
        displayQuestion();
    }
}

// Submit test and get results
async function submitTest() {
    // Check if all questions are answered
    const unanswered = userAnswers.findIndex(answer => answer === null);
    if (unanswered !== -1) {
        const confirmSubmit = confirm(
            `You haven't answered all questions. Question ${unanswered + 1} is unanswered. Submit anyway?`
        );
        if (!confirmSubmit) {
            return;
        }
    }
    
    showLoading(true);
    
    try {
        // Prepare submission
        const answers = testItems.map((item, index) => ({
            question_id: item.id,
            selected_option: userAnswers[index] !== null ? userAnswers[index] : -1
        }));
        
        const response = await fetch(`${API_BASE_URL}/api/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ answers })
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit test');
        }
        
        const results = await response.json();
        displayResults(results);
    } catch (error) {
        console.error('Error submitting test:', error);
        alert('Failed to submit test. Please try again.');
    } finally {
        showLoading(false);
    }
}

// Display results
function displayResults(results) {
    iqScore.textContent = results.iq_score;
    rawScore.textContent = `${results.raw_score} / ${results.total_questions}`;
    percentile.textContent = `${results.percentile}th percentile`;
    description.textContent = results.description;
    resultsDisclaimer.textContent = results.disclaimer;
    
    showScreen('results');
}

// Reset test
function resetTest() {
    testItems = [];
    userAnswers = [];
    currentQuestionIndex = 0;
    showScreen('welcome');
}

// Screen management
function showScreen(screenName) {
    welcomeScreen.classList.remove('active');
    testScreen.classList.remove('active');
    resultsScreen.classList.remove('active');
    
    switch(screenName) {
        case 'welcome':
            welcomeScreen.classList.add('active');
            break;
        case 'test':
            testScreen.classList.add('active');
            break;
        case 'results':
            resultsScreen.classList.add('active');
            break;
    }
}

// Loading spinner
function showLoading(show) {
    loadingSpinner.style.display = show ? 'flex' : 'none';
}

// Check API health on load
window.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        if (!response.ok) {
            console.warn('API health check failed');
            // Note: In a production app, you might want to show a warning banner
        }
    } catch (error) {
        console.warn('Could not connect to API:', error);
        // Note: The startTest function will handle and display errors when user attempts to start
    }
});
