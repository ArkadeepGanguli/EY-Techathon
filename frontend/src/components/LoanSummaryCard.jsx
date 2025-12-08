import React from 'react';
import './LoanSummaryCard.css';

const LoanSummaryCard = ({ application, customer }) => {
    const formatCurrency = (amount) => {
        if (!amount) return '₹ 0';
        return `₹ ${amount.toLocaleString('en-IN')}`;
    };

    const loanAmount = application?.requested_amount || application?.approved_amount || 0;
    const tenure = application?.requested_tenure || application?.approved_tenure || 0;
    const interestRate = application?.interest_rate || 0;
    const emi = application?.emi || application?.emi_amount || 0;

    return (
        <div className="loan-summary-card">
            <div className="card-header">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm7 16H5V5h2v3h10V5h2v14z" />
                </svg>
                <h2 className="card-title">Loan Summary</h2>
            </div>

            <div className="summary-details">
                <div className="detail-row">
                    <span className="label">Loan Amount</span>
                    <span className="value">{formatCurrency(loanAmount)}</span>
                </div>
                <div className="detail-row">
                    <span className="label">Tenure</span>
                    <span className="value">{tenure} Months</span>
                </div>
                <div className="detail-row">
                    <span className="label">Interest Rate</span>
                    <span className="value">{interestRate}% p.a.</span>
                </div>
                <div className="detail-row emi-row">
                    <span className="label">Monthly EMI</span>
                    <span className="value-large">{formatCurrency(emi)}</span>
                </div>
            </div>
        </div>
    );
};

export default LoanSummaryCard;
