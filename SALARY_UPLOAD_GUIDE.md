# 📄 Salary Slip Upload Guide

## Problem Solved ✅

The salary parser has been **enhanced** to better detect salary amounts from uploaded PDF filenames.

---

## How It Works

The system extracts the salary amount from the **filename** of the uploaded PDF (since this is a mock OCR system). The parser now uses **multiple patterns** to detect salary:

### Pattern Detection (in order of priority):

1. **Pattern 1**: Numbers followed by 'k' → `50k.pdf`, `85k.pdf`
   - Detected as: ₹50,000, ₹85,000

2. **Pattern 2**: Full salary numbers (4-6 digits) → `50000.pdf`, `85000.pdf`
   - Detected as: ₹50,000, ₹85,000

3. **Pattern 3**: Any number in filename
   - Numbers < 1000 → multiplied by 1000 (e.g., `50.pdf` → ₹50,000)
   - Numbers ≥ 1000 → used as-is (e.g., `50000.pdf` → ₹50,000)

4. **Fallback**: If no number found → Random salary between ₹40,000-₹1,50,000

---

## ✅ Correct Filename Examples

For a monthly salary of **₹50,000**, use any of these filenames:

### **Recommended (Most Reliable)**
```
50k.pdf          ← Best option
50000.pdf        ← Also works perfectly
salary_50k.pdf   ← Works great
slip_50000.pdf   ← Works great
```

### **Also Works**
```
50.pdf           ← Will be interpreted as ₹50,000
payslip_50k.pdf
monthly_50000.pdf
income_50k.pdf
```

---

## ❌ Filenames That Won't Work

These will result in **random salary** being assigned:

```
salary_slip.pdf     ← No number detected
payslip.pdf         ← No number detected
document.pdf        ← No number detected
my_salary.pdf       ← No number detected
```

---

## 🧪 Testing for Customer 9876543210

**Customer**: Rajesh Kumar  
**Actual Salary**: ₹85,000 (from mock CRM)  
**Requested Loan**: ₹5,00,000 for 36 months

### To upload salary slip for ₹50,000:

1. **Create or rename any PDF file** to one of these:
   - `50k.pdf` ✅ (Recommended)
   - `50000.pdf` ✅
   - `salary_50k.pdf` ✅

2. **Upload the file** when prompted

3. **System will detect**: ₹50,000 monthly salary

4. **Backend logs will show**:
   ```
   [Salary Parser] Detected salary from 'Xk' pattern: ₹50000.0
   ```

---

## 📊 EMI Calculation

For the loan request:
- **Loan Amount**: ₹5,00,000
- **Tenure**: 36 months
- **Interest Rate**: 12% p.a.
- **EMI**: ₹16,607

### With ₹50,000 salary:
- **EMI to Salary Ratio**: 16,607 / 50,000 = **33.2%** ✅
- **Threshold**: 50%
- **Result**: **APPROVED** (EMI is within acceptable range)

### With ₹85,000 salary (actual):
- **EMI to Salary Ratio**: 16,607 / 85,000 = **19.5%** ✅
- **Result**: **APPROVED** (even better ratio)

---

## 🔧 Backend Changes Made

Enhanced `backend/utils/salary_parser.py`:

```python
# Old pattern (less flexible)
salary_match = re.search(r'(\d+)k?', file_name)

# New patterns (more robust)
# Pattern 1: Xk format
salary_match_k = re.search(r'(\d+)k', file_name)

# Pattern 2: Full numbers (4-6 digits)
salary_match_full = re.search(r'(\d{4,6})', file_name)

# Pattern 3: Any number (fallback)
salary_match_any = re.search(r'(\d+)', file_name)
```

---

## 🚀 Next Steps

1. **Backend has been restarted** with the new parser
2. **Frontend is still running** on http://localhost:3000
3. **Try uploading again** with a properly named file:
   - For ₹50,000 → use `50k.pdf` or `50000.pdf`
   - For ₹85,000 → use `85k.pdf` or `85000.pdf`

---

## 📝 Quick Test Checklist

- [ ] Create a PDF file (any PDF will work)
- [ ] Rename it to `50k.pdf` or `50000.pdf`
- [ ] Start conversation with phone: `9876543210`
- [ ] Request loan: `500000 for 36 months`
- [ ] Confirm: `yes`
- [ ] Upload the renamed PDF
- [ ] Verify system shows: "Verified Monthly Salary: ₹50,000.00"
- [ ] Check approval status

---

## 💡 Pro Tips

1. **Always include the salary amount in the filename** for reliable detection
2. **Use 'k' suffix** for thousands (e.g., `50k` = ₹50,000)
3. **Use full numbers** for exact amounts (e.g., `50000` = ₹50,000)
4. **Check backend logs** to see what salary was detected
5. **File content doesn't matter** - only the filename is parsed (this is a mock system)

---

## 🐛 Debugging

If salary is still not detected correctly:

1. **Check the filename** - ensure it contains the salary amount
2. **Check backend logs** - look for `[Salary Parser]` messages
3. **Verify file is PDF** - only `.pdf` extension is accepted
4. **Check file size** - must be between 10KB and 5MB

---

**System Status**: ✅ Backend restarted with enhanced parser  
**Ready to test**: Yes! Upload `50k.pdf` or `50000.pdf`

---

*Last Updated: December 5, 2024*
