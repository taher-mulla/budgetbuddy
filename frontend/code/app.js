// Configuration
const API_GATEWAY_URL = 'YOUR_API_GATEWAY_URL'; // Update after agent deployment

// DOM Elements
const micButton = document.getElementById('mic-button');
const statusText = document.getElementById('status-text');
const textInput = document.getElementById('text-input');
const textSubmitBtn = document.getElementById('text-submit-btn');
const loadingOverlay = document.getElementById('loading-overlay');
const popupModal = document.getElementById('popup-modal');
const popupMessage = document.getElementById('popup-message');
const popupIcon = document.getElementById('popup-icon');
const closePopup = document.getElementById('close-popup');

// Speech Recognition Setup
let recognition = null;
let isListening = false;

function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        console.error('Speech Recognition not supported in this browser');
        statusText.textContent = 'Voice input not supported. Please use text input.';
        micButton.disabled = true;
        return;
    }
    
    recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;
    
    recognition.onstart = () => {
        isListening = true;
        micButton.classList.add('listening');
        statusText.textContent = 'Listening...';
    };
    
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log('Transcript:', transcript);
        statusText.textContent = `You said: "${transcript}"`;
        submitExpense(transcript);
    };
    
    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        isListening = false;
        micButton.classList.remove('listening');
        
        let errorMessage = 'Error occurred. Please try again.';
        if (event.error === 'not-allowed') {
            errorMessage = 'Microphone access denied. Please enable it in browser settings.';
        } else if (event.error === 'no-speech') {
            errorMessage = 'No speech detected. Please try again.';
        }
        
        statusText.textContent = errorMessage;
        setTimeout(() => {
            statusText.textContent = 'Tap to speak';
        }, 3000);
    };
    
    recognition.onend = () => {
        isListening = false;
        micButton.classList.remove('listening');
        if (statusText.textContent === 'Listening...') {
            statusText.textContent = 'Tap to speak';
        }
    };
}

// Start Listening
function startListening() {
    if (!recognition) {
        showPopup('error', 'Speech recognition not available');
        return;
    }
    
    if (isListening) {
        recognition.stop();
    } else {
        try {
            recognition.start();
        } catch (error) {
            console.error('Error starting recognition:', error);
            showPopup('error', 'Could not start voice recognition');
        }
    }
}

// Submit Expense to API
async function submitExpense(text) {
    if (!text || text.trim() === '') {
        showPopup('error', 'Please enter or speak an expense');
        return;
    }
    
    showLoadingSpinner();
    
    const payload = {
        text: text.toLowerCase().trim(),
        timestamp: new Date().toISOString()
    };
    
    try {
        // Check if API URL is configured
        if (API_GATEWAY_URL === 'YOUR_API_GATEWAY_URL') {
            throw new Error('API Gateway URL not configured');
        }
        
        const response = await fetch(`${API_GATEWAY_URL}/expense`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        
        hideLoadingSpinner();
        
        if (response.ok) {
            const message = result.message || 'Expense added successfully!';
            showPopup('success', message);
            textInput.value = ''; // Clear text input
            statusText.textContent = 'Tap to speak';
        } else {
            const errorMsg = result.error || result.message || 'Failed to add expense';
            showPopup('error', errorMsg);
        }
    } catch (error) {
        console.error('Error submitting expense:', error);
        hideLoadingSpinner();
        
        let errorMessage = 'Network error. Please check your connection.';
        if (error.message === 'API Gateway URL not configured') {
            errorMessage = 'API not configured yet. Please update API_GATEWAY_URL in app.js';
        }
        
        showPopup('error', errorMessage);
    }
}

// UI Functions
function showLoadingSpinner() {
    loadingOverlay.classList.remove('hidden');
}

function hideLoadingSpinner() {
    loadingOverlay.classList.add('hidden');
}

function showPopup(type, message) {
    popupIcon.className = `popup-icon ${type}`;
    popupMessage.textContent = message;
    popupModal.classList.remove('hidden');
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        hidePopup();
    }, 3000);
}

function hidePopup() {
    popupModal.classList.add('hidden');
}

// Event Listeners
micButton.addEventListener('click', startListening);

textSubmitBtn.addEventListener('click', () => {
    const text = textInput.value.trim();
    if (text) {
        submitExpense(text);
    }
});

textInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const text = textInput.value.trim();
        if (text) {
            submitExpense(text);
        }
    }
});

closePopup.addEventListener('click', hidePopup);

// Click outside popup to close
popupModal.addEventListener('click', (e) => {
    if (e.target === popupModal) {
        hidePopup();
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initSpeechRecognition();
    
    // Basic authentication check (placeholder - not secure)
    // TODO: Replace with proper authentication mechanism
    console.log('Frontend loaded. Authentication should be handled by CloudFront/ALB.');
});


