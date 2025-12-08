# 🚀 Quick Start Guide - AI Salary Parser

## ⚡ 3-Step Setup

### 1️⃣ Add Your API Key
```bash
# Edit .env file
OPENROUTER_API_KEY=your_actual_api_key_here
```
Get your key: https://openrouter.ai/keys

### 2️⃣ Dependencies (Already Installed ✅)
```bash
cd backend
pip install -r requirements.txt
```

### 3️⃣ Test It
```bash
cd backend/utils
python test_salary_parser.py your_salary_slip.pdf
```

---

## 📋 What Changed

### Before (Mock Parser)
```python
# Only parsed filename
"50k.pdf" → ₹50,000
```

### After (AI Parser)
```python
# Reads actual PDF content + AI analysis
"salary_slip.pdf" → Extracts real salary from PDF text
                  → Falls back to filename if needed
```

---

## 🎯 How It Works

```
Upload PDF
    ↓
Extract Text (PyPDF2)
    ↓
AI Analysis (OpenRouter GLM-4.5-air) ✨
    ↓
Parse Salary Components
    ↓
Return Structured Data
```

**If AI fails** → Automatic fallback to filename parsing

---

## 📊 What Gets Extracted

✅ Basic Salary  
✅ HRA (House Rent Allowance)  
✅ Special Allowance  
✅ Gross Salary  
✅ PF Deduction  
✅ Tax Deduction  
✅ Net/Monthly Salary  

---

## 🔧 Files Modified

| File | Status | Purpose |
|------|--------|---------|
| `backend/utils/salary_parser.py` | ✅ Updated | Main parser with AI integration |
| `backend/requirements.txt` | ✅ Updated | Added openai, dotenv, PyPDF2 |
| `.env` | ✅ Created | API key configuration |
| `.env.example` | ✅ Created | Template for team |

---

## 📝 Usage in Code

```python
from utils.salary_parser import parse_salary_slip

result = parse_salary_slip("path/to/salary.pdf")

print(f"Monthly Salary: ₹{result['parsed_data']['monthly_salary']}")
print(f"Method: {result['method']}")  # "ai_powered" or "filename_based"
```

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| API key error | Add key to `.env` file |
| AI parsing fails | System auto-falls back to filename |
| Dependencies missing | Run `pip install -r requirements.txt` |

---

## 📚 Full Documentation

- **Complete Setup**: `AI_SALARY_PARSER_SETUP.md`
- **Implementation Details**: `IMPLEMENTATION_SUMMARY.md`
- **Test Script**: `backend/utils/test_salary_parser.py`

---

## ✨ Benefits

🎯 **Accurate**: AI reads actual PDF content  
🔄 **Reliable**: Automatic fallback mechanism  
🆓 **Free**: Uses free OpenRouter tier  
🚀 **Fast**: Low latency with GLM-4.5-air  
📊 **Complete**: Extracts all salary components  

---

**Status**: ✅ Ready to use (add API key)  
**Model**: GLM-4.5-air (free)  
**Provider**: OpenRouter  

---

*Need help? Check `IMPLEMENTATION_SUMMARY.md` for detailed info*
