"""FastAPI main application"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil
import uuid
import io

from models import ChatMessage, ChatResponse
from master_agent import master_agent
from memory_manager import memory_manager
from utils.salary_parser import parse_salary_slip, validate_salary_slip
from utils.sanction_letter_generator import SanctionLetterGenerator
from agents.verification_agent import verification_agent
import config

# Create FastAPI app
app = FastAPI(
    title="NBFC Agentic AI Loan System",
    description="Multi-agent AI system for personal loan sales",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for sanction letters
app.mount("/sanctions", StaticFiles(directory=str(config.SANCTION_DIR)), name="sanctions")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NBFC Agentic AI Loan System",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Main chat endpoint - processes user messages
    
    Args:
        message: User's chat message
        
    Returns:
        ChatResponse from the master agent
    """
    try:
        response = master_agent.process_message(message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/start")
async def start_chat():
    """
    Start a new chat session
    
    Returns:
        New session ID
    """
    session_id = memory_manager.create_session()
    
    # Get initial greeting
    initial_message = ChatMessage(session_id=session_id, message="start")
    response = master_agent.process_message(initial_message)
    
    return {
        "session_id": session_id,
        "message": response.message,
        "stage": response.stage
    }


@app.post("/api/upload")
async def upload_file(session_id: str, file: UploadFile = File(...)):
    """
    Handle file upload (salary slip)
    
    Args:
        session_id: Chat session ID
        file: Uploaded file
        
    Returns:
        Upload result with parsed salary
    """
    try:
        # Get session memory
        memory = memory_manager.get_session(session_id)
        if not memory:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Validate file
        file_size = 0
        file_content = await file.read()
        file_size = len(file_content)
        
        validation = verification_agent.validate_uploaded_file(file.filename, file_size)
        if not validation['success']:
            return {
                "success": False,
                "message": validation['message']
            }
        
        # Save file
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        saved_filename = f"{file_id}{file_extension}"
        file_path = config.UPLOAD_DIR / saved_filename
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Parse salary slip
        parsed_result = parse_salary_slip(str(file_path))
        
        if parsed_result['success']:
            parsed_data = parsed_result['parsed_data']
            
            # Check if employee name was extracted
            employee_name = parsed_data.get('employee_name', None)
            customer_name = memory.customer.name
            
            # Verify name match if we have the employee name from salary slip
            if employee_name and employee_name != "Unknown":
                print(f"[Upload] Verifying name match...")
                print(f"[Upload] Customer: {customer_name}")
                print(f"[Upload] Salary Slip: {employee_name}")
                
                from utils.name_verifier import verify_names_match
                verification = verify_names_match(customer_name, employee_name)
                
                print(f"[Upload] Name verification result: {verification}")
                
                # If names don't match, reject the upload
                # We reject if match is False, regardless of confidence
                # The 'confidence' in the response represents how confident the AI is in its decision
                if not verification['match']:
                    print(f"[Upload] ❌ Name mismatch detected!")
                    print(f"[Upload] Confidence in mismatch: {verification['confidence']}")
                    
                    # Mark that name verification failed
                    memory_manager.update_context(session_id, 'name_mismatch_detected', True)
                    memory_manager.update_context(session_id, 'awaiting_salary_slip', True)
                    
                    mismatch_message = f"""
❌ **Name Verification Failed**

The name on the salary slip doesn't match your customer profile:

**Customer Name (CRM):** {customer_name}
**Salary Slip Name:** {employee_name}

**Reason:** {verification['reason']}

**What would you like to do?**

1️⃣ **Upload Correct Salary Slip** - Please upload your salary slip with the correct name
2️⃣ **Cancel Application** - Type 'cancel' to cancel this loan application

Please respond with your choice.
""".strip()
                    
                    return {
                        "success": False,
                        "message": mismatch_message,
                        "name_mismatch": True,
                        "customer_name": customer_name,
                        "salary_slip_name": employee_name
                    }
            
            # Name matches or no name extracted - proceed normally
            print(f"[Upload] ✅ Name verification passed")
            
            # Update application with parsed salary
            application = memory.application
            application.salary_slip_uploaded = True
            application.salary_slip_url = f"/uploads/{saved_filename}"
            application.parsed_salary = parsed_data['monthly_salary']
            memory_manager.set_application(session_id, application)
            
            # Update context
            memory_manager.update_context(session_id, 'awaiting_salary_slip', False)
            memory_manager.update_context(session_id, 'salary_verified', True)
            memory_manager.update_context(session_id, 'name_mismatch_detected', False)
            
            # Get confirmation message
            confirmation = verification_agent.confirm_salary_verification(
                application.parsed_salary,
                memory.customer.name
            )
            
            # Re-run underwriting with salary
            from master_agent import master_agent
            underwriting_response = master_agent._process_underwriting(session_id, memory)
            
            return {
                "success": True,
                "message": confirmation + "\n\n" + underwriting_response.message,
                "parsed_salary": application.parsed_salary,
                "stage": underwriting_response.stage,
                "metadata": underwriting_response.metadata
            }
        else:
            return {
                "success": False,
                "message": "Failed to parse salary slip. Please upload a clear, readable PDF."
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sanction/download/{sanction_id}")
async def download_sanction(sanction_id: str):
    """
    Download sanction letter PDF
    
    Args:
        sanction_id: Sanction ID
        
    Returns:
        PDF file
    """
    file_path = config.SANCTION_DIR / f"sanction_{sanction_id}.pdf"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Sanction letter not found")
    
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=f"sanction_{sanction_id}.pdf"
    )


@app.get("/api/sanction/generate/{session_id}")
async def generate_sanction_letter(session_id: str):
    """
    Generate or retrieve sanction letter PDF for a session
    
    Args:
        session_id: Session ID
        
    Returns:
        PDF file as streaming response
    """
    try:
        print(f"[Sanction] Request for sanction letter - session: {session_id}")
        
        # Get session memory
        memory = memory_manager.get_session(session_id)
        if not memory:
            print(f"[Sanction] ERROR: Session not found: {session_id}")
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if application is approved
        application = memory.application
        if not application:
            print(f"[Sanction] ERROR: No application found for session: {session_id}")
            raise HTTPException(status_code=400, detail="No application found")
            
        if not application.loan_approved:
            print(f"[Sanction] ERROR: Loan not approved for session: {session_id}")
            raise HTTPException(status_code=400, detail="Loan not approved yet")
        
        # Check if sanction letter already exists
        if application.sanction_id:
            sanction_filename = f"sanction_{application.sanction_id}.pdf"
            sanction_path = config.SANCTION_DIR / sanction_filename
            
            if sanction_path.exists():
                print(f"[Sanction] ✅ Reusing existing PDF: {sanction_path}")
                
                # Read existing PDF
                with open(sanction_path, 'rb') as f:
                    pdf_bytes = f.read()
                
                print(f"[Sanction] Returning existing PDF ({len(pdf_bytes)} bytes)")
                
                # Return existing file
                return StreamingResponse(
                    io.BytesIO(pdf_bytes),
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f"attachment; filename={sanction_filename}",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Expose-Headers": "Content-Disposition"
                    }
                )
        
        # If no existing PDF, generate a new one
        print(f"[Sanction] No existing PDF found, generating new one...")
        
        # Initialize generator
        generator = SanctionLetterGenerator()
        
        # Prepare application data
        application_data = {
            'application_id': application.application_id or session_id[:8].upper(),
            'sanction_letter_no': f'SL/2025/{application.application_id or session_id[:8].upper()}'
        }
        
        # Prepare customer data
        customer = memory.customer
        customer_data = {
            'name': customer.name,
            'email': customer.email or 'N/A',
            'phone': customer.phone or 'N/A',
            'address': customer.address or 'N/A'
        }
        
        # Prepare loan details
        loan_details = {
            'amount': application.approved_amount,
            'interest_rate': application.interest_rate or 10.5,
            'tenure': application.tenure,
            'emi': application.emi_amount,
            'processing_fee': application.approved_amount * 0.02  # 2% processing fee
        }
        
        print(f"[Sanction] Generating new PDF...")
        print(f"[Sanction] Application ID: {application_data['application_id']}")
        print(f"[Sanction] Customer: {customer_data['name']}")
        print(f"[Sanction] Amount: Rs. {loan_details['amount']:,.2f}")
        
        # Generate PDF
        pdf_bytes = generator.generate_sanction_letter(
            application_data=application_data,
            customer_data=customer_data,
            loan_details=loan_details
        )
        
        # Save to file (use application_id for consistency)
        sanction_filename = f"sanction_{application_data['application_id']}.pdf"
        sanction_path = config.SANCTION_DIR / sanction_filename
        
        print(f"[Sanction] Saving PDF to: {sanction_path}")
        with open(sanction_path, 'wb') as f:
            f.write(pdf_bytes)
        print(f"[Sanction] PDF saved successfully")
        
        # Update application with sanction info if not already set
        if not application.sanction_id:
            application.sanction_id = application_data['application_id']
            application.sanction_letter_url = f"/api/sanction/download/{application_data['application_id']}"
            memory_manager.set_application(session_id, application)
        
        print(f"[Sanction] Returning new PDF ({len(pdf_bytes)} bytes)")
        
        # Return as downloadable file
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={sanction_filename}",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Sanction] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))




@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """
    Get session details
    
    Args:
        session_id: Session ID
        
    Returns:
        Session memory
    """
    memory = memory_manager.get_session(session_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": memory.session_id,
        "stage": memory.current_stage,
        "customer": memory.customer.dict() if memory.customer else None,
        "application": memory.application.dict() if memory.application else None,
        "conversation_history": memory.conversation_history
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "NBFC Agentic AI Loan System"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
