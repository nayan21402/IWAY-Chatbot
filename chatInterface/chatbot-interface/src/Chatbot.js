import React, { useState } from 'react';
import axios from 'axios';
import './Chatbot.css'; // Assuming you create a Chatbot.css file for styling

function Chatbot() {
    const [message, setMessage] = useState('');
    const [chatHistory, setChatHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (message.trim() === '') return;

        setLoading(true);
        setError(null);

        const newMessage = { userMessage: message, botResponse: '' };
        setChatHistory([...chatHistory, newMessage]);
        setMessage('');

        try {
            // Use axios to send a GET request to the backend
            const response = await axios.get(`http://localhost:5000/chat?message=${encodeURIComponent(message)}`);
            
            // Update the bot's response with the received answer
            newMessage.botResponse = response.data.answer;
            setChatHistory([...chatHistory, newMessage]);
        } catch (error) {
            console.error('Error communicating with the chatbot', error);
            setError('Error communicating with the chatbot');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-history">
                {chatHistory.map((chat, index) => (
                    <div key={index} className='flex flex-col'>
                        <div className="user-message message-box">
                            <p>{chat.userMessage}</p>
                        </div>
                        <div className="bot-message message-box">
                            <p>{chat.botResponse}</p>
                        </div>
                    </div>
                ))}
                {loading && <div className="loading">Loading...</div>}
                {error && <div className="error-message">{error}</div>}
            </div>
            <form onSubmit={handleSubmit} className="chat-form">
                <input 
                    type="text" 
                    value={message} 
                    onChange={(e) => setMessage(e.target.value)} 
                    placeholder="Type your message here"
                    className="chat-input"
                />
                <button type="submit" className="chat-button">Send</button>
            </form>
        </div>
    );
}

export default Chatbot;
