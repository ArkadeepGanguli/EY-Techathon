import React from 'react';
import './MessageBubble.css';

const MessageBubble = ({ message }) => {
    const isUser = message.role === 'user';

    // Format message content with markdown-like styling
    const formatMessage = (content) => {
        // Split by lines
        const lines = content.split('\n');

        return lines.map((line, index) => {
            // Bold text
            line = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

            // Emojis and icons stay as is

            // Links
            line = line.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

            return (
                <span key={index} dangerouslySetInnerHTML={{ __html: line }} />
            );
        });
    };

    return (
        <div className={`message ${isUser ? 'user' : 'assistant'}`}>
            <div className="message-content">
                {message.content.split('\n').map((line, index) => {
                    if (!line.trim()) return <br key={index} />;

                    // Check if line is a heading (starts with **)
                    if (line.includes('**')) {
                        const parts = line.split('**');
                        return (
                            <div key={index} className="message-line">
                                {parts.map((part, i) =>
                                    i % 2 === 1 ? <strong key={i}>{part}</strong> : part
                                )}
                            </div>
                        );
                    }

                    // Check if line is a bullet point
                    if (line.trim().startsWith('•') || line.trim().startsWith('✅') ||
                        line.trim().startsWith('❌') || line.trim().startsWith('⚠️') ||
                        line.trim().startsWith('💰') || line.trim().startsWith('📋') ||
                        line.trim().match(/^[0-9]+\./)) {
                        return <div key={index} className="message-line bullet">{line}</div>;
                    }

                    return <div key={index} className="message-line">{line}</div>;
                })}
            </div>
            <div className="message-time">
                {new Date(message.timestamp).toLocaleTimeString('en-US', {
                    hour: '2-digit',
                    minute: '2-digit',
                })}
            </div>
        </div>
    );
};

export default MessageBubble;
