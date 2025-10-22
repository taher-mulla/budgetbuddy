# Frontend - Voice-Activated Expense Entry Interface

## Purpose

The frontend is a single-page web application that provides a fast, voice-first interface for logging expenses. Users can tap a large microphone button to speak their expense (e.g., "add thirty dollars for groceries") or use a fallback text input for manual entry.

## AWS Services Used

- **Amazon S3**: Hosts static files (HTML, CSS, JavaScript)
- **Amazon CloudFront**: Provides HTTPS delivery, caching, and fast global access
- **Application Load Balancer (ALB)**: Optionally routes traffic with basic HTTP authentication

## Key Features

- **Web Speech API Integration**: Client-side speech-to-text using Chrome's native API (no server processing required)
- **Basic HTTP Authentication**: Simple username/password prompt before page access
- **Real-time Feedback**: Loading spinner during processing, confirmation popup after successful submission
- **Responsive Design**: Large, tappable microphone button (~2-inch diameter) optimized for mobile use

## Files in this Folder

### `code/`
- `index.html` - Main HTML structure with microphone button, text input, and confirmation popup
- `styles.css` - Modern, responsive styling with emphasis on the voice input button
- `app.js` - JavaScript handling Web Speech API, form submission, API Gateway integration

### `cloudformation/`
- CloudFormation templates for provisioning S3 bucket, CloudFront distribution, and ALB configuration

## Integration Points

- **Sends to**: Agent Lambda function via API Gateway
- **Request Format**: `POST` with JSON payload: `{"text": "add thirty dollars groceries", "timestamp": "2025-10-21T19:53:00Z"}`
- **Receives**: Confirmation JSON or clarification prompt from agent


