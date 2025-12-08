# Sanction Letter Generation - Implementation Guide

## Overview
The sanction letter generation feature has been successfully implemented using the professional PDF generator in `backend/utils/sanction_letter_generator.py`.

## What Was Done

### 1. Backend Implementation

#### Updated Files:
- **`backend/main.py`**: Added new endpoint `/api/sanction/generate/{session_id}` to generate sanction letters
- **`backend/agents/sanction_agent.py`**: Updated to use the new `SanctionLetterGenerator` class
- **`backend/models.py`**: Added fields to `LoanApplication` model:
  - `application_id`
  - `approved_amount`
  - `approved_tenure`
  - `tenure`
  - `emi_amount`
  - `loan_approved`
- **`backend/master_agent.py`**: Updated `_process_underwriting` to set approved fields when loan is approved

#### New Endpoint:
```
POST /api/sanction/generate/{session_id}
```
This endpoint:
- Retrieves the session data (customer + application)
- Validates that the loan has been approved
- Generates a professional PDF sanction letter using `SanctionLetterGenerator`
- Saves the PDF to the `sanctions` directory
- Returns the PDF as a downloadable file

### 2. Sanction Letter Generator Features

The `SanctionLetterGenerator` class in `backend/utils/sanction_letter_generator.py` generates professional PDF sanction letters with:

#### Letter Contents:
- **Company Letterhead** (Tata Capital Limited)
- **Application Details**: Sanction Letter No., Date, Application ID
- **Customer Information**: Name, Address, Email, Phone
- **Loan Details Table**:
  - Loan Amount Sanctioned
  - Interest Rate (per annum)
  - Loan Tenure
  - Monthly EMI
  - Processing Fee (2%)
  - Net Disbursement Amount
  - Total Amount Payable
  - Total Interest Payable
  - EMI Start Date
  - Loan Maturity Date
- **Terms and Conditions** (10 detailed terms)
- **Documents Required for Disbursement** (6 items)
- **Authorized Signatory**
- **Footer** with company contact information

#### Design Features:
- Professional typography using Helvetica fonts
- Color scheme with Tata Capital blue (#1a237e)
- Alternating row backgrounds in tables
- Proper spacing and margins
- A4 page size
- Computer-generated document disclaimer

### 3. Test Generation

A sample sanction letter has been generated for Rajesh Kumar with the following details:
- **Customer**: Rajesh Kumar
- **Loan Amount**: ₹500,000.00
- **Tenure**: 36 months (3 years)
- **EMI**: ₹16,473.60
- **Interest Rate**: 10.5% p.a.
- **Processing Fee**: ₹10,000.00
- **Total Payable**: ₹593,049.60

The generated PDF is saved as: `sanction_letter_rajesh_kumar.pdf`

## How to Use

### 1. Test Generation (Standalone)

Run the test script to generate a sample sanction letter:

```bash
cd backend
python test_sanction_letter.py
```

This will create `sanction_letter_rajesh_kumar.pdf` in the backend directory.

### 2. API Integration

When a loan is approved in the chat flow, the master agent automatically generates the sanction letter. You can also manually trigger it via the API:

```bash
POST http://localhost:8000/api/sanction/generate/{session_id}
```

The response will be a PDF file download.

### 3. Frontend Integration

To integrate with the frontend, add a "Download Sanction Letter" button when the loan is approved:

```javascript
// After loan approval, show download button
if (response.metadata?.sanction_id) {
  const downloadUrl = `/api/sanction/generate/${sessionId}`;
  // Create download button with this URL
}
```

Example React component:
```jsx
{metadata?.sanction_id && (
  <a 
    href={`/api/sanction/generate/${sessionId}`}
    download
    className="btn-download"
  >
    📥 Download Sanction Letter
  </a>
)}
```

## File Structure

```
backend/
├── utils/
│   ├── sanction_letter_generator.py  # PDF generator class
│   └── pdf_generator.py              # Old generator (not used)
├── agents/
│   └── sanction_agent.py             # Updated to use new generator
├── main.py                           # Added /api/sanction/generate endpoint
├── models.py                         # Updated LoanApplication model
├── master_agent.py                   # Updated to set approved fields
└── test_sanction_letter.py          # Test script

frontend/
└── (to be integrated)
```

## Configuration

The sanction letters are saved in the directory specified in `config.py`:
```python
SANCTION_DIR = Path("sanctions")
```

Make sure this directory exists or it will be created automatically.

## Dependencies

All required dependencies are already in `requirements.txt`:
- `reportlab==4.0.7` - For PDF generation
- `python-dateutil==2.8.2` - For date handling

## Customization

To customize the sanction letter:

1. **Company Details**: Edit `SanctionLetterGenerator.__init__()` to change company name, address, contact info
2. **Letter Content**: Modify `generate_sanction_letter()` method to change sections
3. **Styling**: Update the custom styles in `generate_sanction_letter()` to change colors, fonts, sizes
4. **Terms & Conditions**: Edit the `terms` list in the method
5. **Processing Fee**: Currently set to 2% in multiple places, search for `0.02` to change

## Next Steps

### Frontend Integration:
1. Add a download button in the chat UI when `stage === 'close'` and `metadata.sanction_id` exists
2. Implement a preview modal to show PDF before download (optional)
3. Add loading state while PDF is being generated
4. Show success message after download

### Backend Enhancements:
1. Send sanction letter via email automatically
2. Store PDF in cloud storage (S3, etc.) for persistence
3. Add digital signature or QR code for verification
4. Generate sanction letter in multiple languages
5. Add watermark or security features

## Testing Checklist

- [✓] Standalone PDF generation works
- [✓] API endpoint created
- [✓] Sanction agent updated
- [✓] Models updated with required fields
- [✓] Master agent sets approved fields
- [ ] Frontend integration
- [ ] End-to-end testing with actual chat flow
- [ ] Email delivery (future)

## Troubleshooting

### PDF not generating?
- Check if `reportlab` is installed: `pip install reportlab`
- Ensure `SANCTION_DIR` exists and is writable
- Check console for error messages

### Fields missing in PDF?
- Ensure `LoanApplication` model has all approved fields set in `_process_underwriting`
- Check that `application_id` is generated
- Verify `loan_approved` is set to `True`

### Download not working in frontend?
- Check CORS settings in `main.py`
- Verify the session_id is correct
- Ensure loan is approved before attempting download

## Example Output

The generated sanction letter includes:
- Professional Tata Capital letterhead
- All loan details in a well-formatted table
- 10 comprehensive terms and conditions
- Document requirements list
- Authorized signatory section
- Company contact information

See `sanction_letter_rajesh_kumar.pdf` for a complete example.

---

**Generated on**: December 7, 2025  
**Implementation Status**: ✅ Complete (Backend), ⏳ Pending (Frontend)
