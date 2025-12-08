# NBFC Agentic AI Multi-Agent Loan System

A production-ready multi-agent AI system for personal loan sales, built for NBFC (Non-Banking Financial Company) operations. This system simulates a complete loan processing workflow using specialized AI agents for sales, verification, underwriting, and sanction letter generation.

## 🎯 Features

### Multi-Agent Architecture
- **Master Agent (Orchestrator)** - Manages conversation flow and delegates to worker agents
- **Sales Agent** - Presents offers, handles negotiations and objections
- **Verification Agent** - Performs KYC verification and document validation
- **Underwriting Agent** - Evaluates loan applications with business rules
- **Sanction Agent** - Generates professional PDF sanction letters

### Complete Loan Workflow
1. **Greeting & Intent Capture** - Collect customer phone number
2. **Lead Qualification** - Fetch customer profile from CRM
3. **Offer Presentation** - Present personalized loan offers
4. **KYC Verification** - Verify identity with OTP simulation
5. **Underwriting** - Apply credit rules and risk assessment
6. **Decision** - Approve, reject, or request additional documents
7. **Sanction Letter** - Generate and deliver PDF sanction letter
8. **Close** - Complete the conversation

### Business Rules (Underwriting)
- ❌ **Reject** if credit score < 700
- ✅ **Instant Approval** if amount ≤ pre-approved limit
- 📄 **Conditional Approval** if amount ≤ 2× pre-approved limit (requires salary slip)
  - EMI must be ≤ 50% of monthly salary
- ❌ **Reject** if amount > 2× pre-approved limit

### Premium UI/UX
- 🎨 Modern dark theme with glassmorphism
- ✨ Smooth animations and micro-interactions
- 📱 Fully responsive (desktop & mobile)
- 💬 Real-time chat interface
- 📤 File upload for salary slips
- 📥 Sanction letter download

## 🏗️ Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** - High-performance async web framework
- **Pydantic** - Data validation and settings management
- **ReportLab** - PDF generation for sanction letters
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - UI library
- **Vite** - Fast build tool
- **Axios** - HTTP client
- **Modern CSS** - Custom design system with animations

## 📁 Project Structure

```
EY Techathon/
├── backend/
│   ├── agents/
│   │   ├── sales_agent.py          # Offer presentation & negotiation
│   │   ├── verification_agent.py   # KYC & document verification
│   │   ├── underwriting_agent.py   # Risk assessment & approval logic
│   │   └── sanction_agent.py       # PDF sanction letter generation
│   ├── mocks/
│   │   ├── crm_service.py          # Mock CRM data
│   │   ├── credit_bureau.py        # Mock credit score API
│   │   └── offer_mart.py           # Mock loan offers
│   ├── utils/
│   │   ├── emi_calculator.py       # EMI calculation logic
│   │   ├── salary_parser.py        # Mock salary slip OCR
│   │   └── pdf_generator.py        # Sanction letter PDF creation
│   ├── master_agent.py             # Main orchestrator
│   ├── state_machine.py            # Conversation flow management
│   ├── memory_manager.py           # Session & context management
│   ├── models.py                   # Pydantic data models
│   ├── config.py                   # Configuration settings
│   ├── main.py                     # FastAPI application
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx   # Main chat UI
│   │   │   ├── MessageBubble.jsx   # Message display
│   │   │   └── FileUpload.jsx      # File upload component
│   │   ├── App.jsx                 # Main app component
│   │   ├── main.jsx                # React entry point
│   │   └── index.css               # Design system & styles
│   ├── index.html                  # HTML template
│   ├── vite.config.js              # Vite configuration
│   └── package.json                # Node dependencies
├── mock_data.json                  # 10 synthetic customer profiles
├── uploads/                        # Uploaded salary slips
├── sanctions/                      # Generated sanction letters
└── README.md                       # This file
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- npm or yarn

### Installation

#### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt
```

#### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install
```

### Running the Application

#### Start Backend Server

```bash
# From backend directory
python main.py

# Server will start on http://localhost:8000
```

#### Start Frontend Development Server

```bash
# From frontend directory (in a new terminal)
npm run dev

# Frontend will start on http://localhost:3000
```

### Access the Application

Open your browser and navigate to:
```
http://localhost:3000
```

## 📊 Test Scenarios

### Scenario 1: Instant Approval (High Credit Score, Within Limit)
- **Phone**: 9876543211
- **Customer**: Priya Sharma
- **Credit Score**: 820
- **Pre-approved**: ₹5,00,000
- **Request**: ₹3,00,000 for 24 months
- **Result**: ✅ Instant Approval

### Scenario 2: Conditional Approval (Requires Salary Slip)
- **Phone**: 9876543210
- **Customer**: Rajesh Kumar
- **Credit Score**: 780
- **Pre-approved**: ₹3,00,000
- **Request**: ₹5,00,000 for 36 months
- **Result**: 📄 Salary slip required → ✅ Approved (if EMI ≤ 50% salary)

### Scenario 3: Rejection (Low Credit Score)
- **Phone**: 9876543218
- **Customer**: Arjun Gupta
- **Credit Score**: 580
- **Result**: ❌ Rejected (credit score < 700)

### Scenario 4: Rejection (High EMI Ratio)
- **Phone**: 9876543216
- **Customer**: Rahul Mehta
- **Credit Score**: 620 (but passes threshold)
- **Salary**: ₹48,000
- **Request**: ₹1,50,000 for 12 months
- **Result**: ❌ Rejected (EMI > 50% of salary)

## 🔌 API Endpoints

### Chat Endpoints
- `POST /api/chat/start` - Start new chat session
- `POST /api/chat` - Send message to chatbot
- `GET /api/session/{session_id}` - Get session details

### File Upload
- `POST /api/upload?session_id={id}` - Upload salary slip PDF

### Sanction Letter
- `GET /api/sanction/download/{sanction_id}` - Download sanction letter PDF

### Health Check
- `GET /api/health` - Health check endpoint

## 📝 Mock Data

The system includes 10 synthetic customer profiles with varying:
- Credit scores (580-840)
- Monthly salaries (₹42,000 - ₹1,35,000)
- Pre-approved limits (₹80,000 - ₹6,00,000)
- Existing loans (0-3)
- KYC status (verified/pending)

See `mock_data.json` for complete customer data.

## 🎨 Design System

### Color Palette
- **Primary**: Deep indigo (#1a237e)
- **Accent**: Cyan (#00bcd4)
- **Success**: Green (#4caf50)
- **Background**: Dark gradient with glassmorphism

### Typography
- **Font**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700

### Key Features
- Glassmorphism effects
- Smooth micro-animations
- Gradient backgrounds
- Premium dark theme

## 🔒 Security Considerations

**Note**: This is a demo/MVP system. For production deployment:

1. Add authentication & authorization
2. Implement rate limiting
3. Add input sanitization
4. Use HTTPS/TLS
5. Implement CSRF protection
6. Add logging & monitoring
7. Use environment variables for secrets
8. Implement data encryption
9. Add audit trails
10. Comply with data privacy regulations (GDPR, etc.)

## 🐛 Troubleshooting

### Backend won't start
- Ensure Python 3.11+ is installed
- Check if port 8000 is available
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Frontend won't start
- Ensure Node.js 18+ is installed
- Delete `node_modules` and run `npm install` again
- Check if port 3000 is available

### File upload fails
- Ensure file is PDF format
- Check file size is under 5MB
- Verify `uploads/` directory exists and is writable

### Sanction letter not generating
- Check `sanctions/` directory exists and is writable
- Verify ReportLab is installed correctly

## 📄 License

This project is created for demonstration purposes.

## 👥 Support

For questions or issues, please contact the development team.

---

**Built with ❤️ for EY Techathon**
