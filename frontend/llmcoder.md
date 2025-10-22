# LLM Coder Instructions: Frontend Implementation

## Objective

Create a voice-first expense tracking web interface that runs entirely in the browser using Chrome's Web Speech API. The interface should be fast, intuitive, and optimized for mobile use with a prominent microphone button.

## Technical Requirements

### 1. HTML Structure (`code/index.html`)

Create a single-page HTML5 application with:

**Required Elements:**
- Large, circular microphone button (minimum 80px diameter, recommend 120px for mobile)
- Visual states: idle (red), listening (pulsing animation), processing (disabled)
- Fallback text input field below the microphone button
- Submit button for text input
- Loading spinner overlay (show during API call)
- Success/error popup modal for feedback
- Responsive meta viewport tag for mobile optimization

**HTML5 Boilerplate:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BudgetBuddy - Expense Tracker</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <!-- Microphone button, text input, loading spinner, popup modal -->
    <script src="app.js"></script>
</body>
</html>
```

### 2. CSS Styling (`code/styles.css`)

**Design Principles:**
- Clean, modern interface with ample whitespace
- Mobile-first responsive design
- Prominent call-to-action (microphone button)
- Smooth animations for state transitions

**Key Styling Requirements:**
- Microphone button: Circular, red background (#E74C3C or similar), white icon, centered on page
- Pulsing animation when listening (scale or glow effect using CSS keyframes)
- Loading spinner: Semi-transparent overlay with centered spinner animation
- Popup modal: Centered, rounded corners, shadow for depth
- Text input: Large font (16px+ to prevent iOS zoom), rounded borders

**CSS Animation Example:**
```css
@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}

.listening {
    animation: pulse 1.5s infinite;
}
```

### 3. JavaScript Logic (`code/app.js`)

**Core Functionality:**

#### A. Web Speech API Integration

```javascript
// Initialize Speech Recognition (Chrome only)
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();

recognition.lang = 'en-US';
recognition.continuous = false; // Stop after one utterance
recognition.interimResults = false; // Only return final result

recognition.onstart = () => {
    // Update UI: Add 'listening' class to button
};

recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    // Send transcript to API
};

recognition.onerror = (event) => {
    // Handle errors (no microphone, permission denied)
};

recognition.onend = () => {
    // Reset UI to idle state
};
```

#### B. API Gateway Integration

**Endpoint:** Replace `YOUR_API_GATEWAY_URL` with actual API Gateway endpoint from agent deployment.

**Request Format:**
```javascript
async function submitExpense(text) {
    const payload = {
        text: text.toLowerCase(),
        timestamp: new Date().toISOString()
    };

    try {
        const response = await fetch('https://YOUR_API_GATEWAY_URL/expense', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        
        if (response.ok) {
            showPopup('success', result.message || 'Expense added successfully!');
        } else {
            showPopup('error', result.error || 'Something went wrong');
        }
    } catch (error) {
        showPopup('error', 'Network error. Please try again.');
    }
}
```

#### C. UI State Management

**State Transitions:**
1. **Idle**: Red button, clickable
2. **Listening**: Pulsing animation, voice recording active
3. **Processing**: Disabled button, loading spinner visible
4. **Success/Error**: Popup modal with confirmation or error message

**Functions to Implement:**
- `startListening()` - Triggered by microphone button click
- `stopListening()` - Called when user stops speaking or timeout
- `submitExpense(text)` - Sends data to API Gateway
- `showLoadingSpinner()` / `hideLoadingSpinner()` - Toggle overlay
- `showPopup(type, message)` - Display success/error modal with auto-dismiss after 3 seconds

#### D. Fallback Text Input

Handle manual text entry:
```javascript
document.getElementById('text-submit-btn').addEventListener('click', () => {
    const textInput = document.getElementById('text-input').value.trim();
    if (textInput) {
        submitExpense(textInput);
    }
});
```

### 4. Basic HTTP Authentication

**Implementation Options:**

**Option A: CloudFront Lambda@Edge**
- Attach Lambda@Edge function to CloudFront distribution
- Check `Authorization` header, return 401 if missing/invalid
- Credentials stored in environment variables

**Option B: Application Load Balancer Authentication**
- Configure ALB with basic authentication rules
- Simpler but requires ALB (additional cost)

**Option C: JavaScript Prompt (Quick MVP)**
- Simple client-side prompt (not secure, placeholder only)
```javascript
const username = prompt('Username:');
const password = prompt('Password:');
// Hardcoded check (INSECURE - for MVP only)
if (username !== 'admin' || password !== 'password123') {
    document.body.innerHTML = '<h1>Access Denied</h1>';
}
```

For MVP, Option C is fastest. For production, use Option A or B.

### 5. Error Handling

**Scenarios to Handle:**
- Microphone permission denied → Show fallback text input with message
- No speech detected → Timeout after 5 seconds, show "No speech detected" message
- API Gateway unreachable → Display network error message
- Invalid API response → Show generic error with retry option

### 6. Testing Checklist

- [ ] Microphone button triggers speech recognition
- [ ] Spoken text is correctly transcribed
- [ ] Transcribed text is sent to API Gateway with correct format
- [ ] Loading spinner appears during API call
- [ ] Success popup shows on successful expense addition
- [ ] Error popup shows on API failure
- [ ] Fallback text input works when entered manually
- [ ] UI is responsive on mobile (test on actual device)
- [ ] Authentication prompt blocks unauthorized access

## Expected Output

After implementation, the frontend should:
1. Load instantly (< 1 second on fast connection)
2. Respond to voice input within 2-3 seconds of speaking
3. Provide clear visual feedback at every step
4. Work seamlessly on Chrome mobile and desktop

## Integration with Other Components

**Agent Endpoint:** The `app.js` file must be updated with the actual API Gateway URL after the agent is deployed. Look for `YOUR_API_GATEWAY_URL` placeholder.

**Expected API Response:**
```json
{
    "status": "success",
    "message": "$30.00 added to groceries",
    "expense_id": 123
}
```

or for clarification:
```json
{
    "status": "clarification_needed",
    "message": "Did you mean 'dining' or 'groceries'?",
    "options": ["dining", "groceries"]
}
```

## Deployment Notes

1. Upload `code/` contents to S3 bucket
2. Enable static website hosting on S3
3. Configure CloudFront distribution to point to S3 bucket
4. Update `app.js` with API Gateway endpoint
5. Test basic authentication before public access


