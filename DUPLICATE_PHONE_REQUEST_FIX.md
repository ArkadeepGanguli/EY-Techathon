# Fix: Duplicate Mobile Number Request

## Problem
The chatbot was asking for the mobile number twice when the application started:
1. First request: "Please enter a valid 10-digit mobile number (e.g., 9876543210):"
2. Second request: Same message again

## Root Cause
The issue was caused by the "start" message being sent twice to the backend:

1. **App.jsx** called `/api/chat/start` which processed the greeting
2. **ChatInterface.jsx** had a `useEffect` that also sent a "start" message to `/api/chat`

This meant:
- First call: Showed greeting, transitioned to INTENT_CAPTURE stage
- Second call: Already in INTENT_CAPTURE stage, checked for phone (not found in "start"), asked for phone

## Changes Made

### Backend Changes (`backend/master_agent.py`)
1. **Added phone request to greeting message** (lines 102-108):
   - Greeting now includes: "**To get started, please enter your 10-digit mobile number:**"
   - This ensures the phone request appears once as part of the welcome message

### Frontend Changes

1. **Updated App.jsx**:
   - Added `initialMessage` state to capture the greeting from `/api/chat/start`
   - Passes `initialMessage` as a prop to `ChatInterface`

2. **Updated ChatInterface.jsx**:
   - Removed the duplicate `useEffect` that was sending "start" message
   - Added new `useEffect` to display the initial greeting message from props
   - Now accepts `initialMessage` prop from parent component

## Result
✅ Mobile number is now requested **only once** in the initial greeting message
✅ No duplicate messages
✅ Cleaner user experience

## Testing
To test the fix:
1. Restart the backend and frontend servers
2. Open the application
3. You should see the greeting message with the phone number request only once
4. Enter a 10-digit mobile number to proceed with the loan application
