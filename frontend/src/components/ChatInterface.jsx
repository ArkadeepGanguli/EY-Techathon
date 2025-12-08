import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import MessageBubble from './MessageBubble';
import FileUpload from './FileUpload';
import './ChatInterface.css';

const ChatInterface = ({ sessionId, initialMessage, onSessionUpdate }) => {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [currentStage, setCurrentStage] = useState('greeting');
    const [requiresFileUpload, setRequiresFileUpload] = useState(false);
    const [sanctionData, setSanctionData] = useState(null);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    useEffect(() => {
        // Display initial greeting message if available
        if (initialMessage) {
            const assistantMessage = {
                role: 'assistant',
                content: initialMessage,
                timestamp: new Date().toISOString(),
            };
            setMessages([assistantMessage]);
        }
    }, [initialMessage]);



    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const sendMessage = async (text) => {
        if (!text.trim() && text !== 'start') return;

        // Add user message to chat (except for start)
        if (text !== 'start') {
            const userMessage = {
                role: 'user',
                content: text,
                timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, userMessage]);
        }

        setInputValue('');
        setIsLoading(true);

        try {
            const response = await axios.post('/api/chat', {
                session_id: sessionId,
                message: text,
            });

            const assistantMessage = {
                role: 'assistant',
                content: response.data.message,
                timestamp: new Date().toISOString(),
                metadata: response.data.metadata,
            };

            setMessages((prev) => [...prev, assistantMessage]);
            setCurrentStage(response.data.stage);

            // Check if file upload is required
            if (response.data.input_type === 'file') {
                setRequiresFileUpload(true);
            } else {
                setRequiresFileUpload(false);
            }

            // Check for sanction letter
            if (response.data.metadata?.sanction_id) {
                setSanctionData(response.data.metadata);
            }

            // Emit session update to parent
            if (onSessionUpdate) {
                // Fetch session data to get customer and application info
                try {
                    const sessionResponse = await axios.get(`/api/session/${sessionId}`);
                    onSessionUpdate({
                        customer: sessionResponse.data.customer,
                        application: sessionResponse.data.application,
                        stage: response.data.stage,
                        metadata: response.data.metadata
                    });
                } catch (err) {
                    console.error('Failed to fetch session data:', err);
                }
            }
        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = {
                role: 'assistant',
                content: '❌ Sorry, something went wrong. Please try again.',
                timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (inputValue.trim()) {
            sendMessage(inputValue);
        }
    };

    const handleFileUpload = async (file) => {
        setIsLoading(true);

        const uploadMessage = {
            role: 'user',
            content: `📄 Uploaded: ${file.name}`,
            timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, uploadMessage]);

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await axios.post(
                `/api/upload?session_id=${sessionId}`,
                formData,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                }
            );

            if (response.data.success) {
                const assistantMessage = {
                    role: 'assistant',
                    content: response.data.message,
                    timestamp: new Date().toISOString(),
                    metadata: response.data.metadata,
                };
                setMessages((prev) => [...prev, assistantMessage]);
                setCurrentStage(response.data.stage);
                setRequiresFileUpload(false);

                // Check for sanction letter
                if (response.data.metadata?.sanction_id) {
                    setSanctionData(response.data.metadata);
                }

                // Emit session update to parent
                if (onSessionUpdate) {
                    try {
                        const sessionResponse = await axios.get(`/api/session/${sessionId}`);
                        onSessionUpdate({
                            customer: sessionResponse.data.customer,
                            application: sessionResponse.data.application,
                            stage: response.data.stage,
                            metadata: response.data.metadata
                        });
                    } catch (err) {
                        console.error('Failed to fetch session data:', err);
                    }
                }
            } else {
                const errorMessage = {
                    role: 'assistant',
                    content: response.data.message,
                    timestamp: new Date().toISOString(),
                };
                setMessages((prev) => [...prev, errorMessage]);
            }
        } catch (error) {
            console.error('Error uploading file:', error);
            const errorMessage = {
                role: 'assistant',
                content: '❌ Failed to upload file. Please try again.',
                timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="chat-interface">
            <div className="chat-header">
                <div className="chat-status">
                    <div className="status-indicator"></div>
                    <span className="status-text">AI Assistant Active</span>
                </div>
                <div className="stage-badge">
                    {currentStage.replace('_', ' ').replace(/kyc/gi, 'KYC').split(' ').map(word =>
                        word.toUpperCase() === 'KYC' ? 'KYC' : word.charAt(0).toUpperCase() + word.slice(1)
                    ).join(' ')}
                </div>
            </div>

            <div className="chat-messages">
                {messages.map((message, index) => (
                    <MessageBubble key={index} message={message} />
                ))}
                {isLoading && (
                    <div className="typing-indicator">
                        <div className="typing-dot"></div>
                        <div className="typing-dot"></div>
                        <div className="typing-dot"></div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-container">
                {requiresFileUpload && (
                    <FileUpload onFileSelect={handleFileUpload} disabled={isLoading} />
                )}

                <form onSubmit={handleSubmit} className="chat-input-form">
                    <input
                        ref={inputRef}
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        placeholder={
                            requiresFileUpload
                                ? 'Upload your salary slip above...'
                                : 'Type your message...'
                        }
                        disabled={isLoading || currentStage === 'close'}
                        className="chat-input"
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !inputValue.trim() || currentStage === 'close'}
                        className="send-button"
                    >
                        <svg
                            width="24"
                            height="24"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        >
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                        </svg>
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ChatInterface;
