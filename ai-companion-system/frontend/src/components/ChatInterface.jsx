import { useState, useEffect, useRef } from 'react';
import useStore from '../store/useStore';
import { chatAPI } from '../services/api';

function ChatInterface() {
  const [input, setInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const messagesEndRef = useRef(null);

  const {
    selectedCharacter,
    messages,
    setMessages,
    addMessage,
    appendToLastMessage,
    isLoading,
    setIsLoading,
  } = useStore();

  useEffect(() => {
    if (selectedCharacter) {
      loadHistory();
    }
  }, [selectedCharacter]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadHistory = async () => {
    if (!selectedCharacter) return;

    try {
      const data = await chatAPI.getHistory(selectedCharacter.id);
      setMessages(data.messages);
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || !selectedCharacter || isGenerating) return;

    const userMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString(),
    };

    addMessage(userMessage);
    setInput('');
    setIsGenerating(true);

    try {
      addMessage({
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
      });

      const eventSource = new EventSource(
        `http://localhost:8000/api/chat/send?character_id=${selectedCharacter.id}&message=${encodeURIComponent(userMessage.content)}&user_id=1&stream=true&include_memory=true`
      );

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'chunk') {
          appendToLastMessage(data.content);
        } else if (data.type === 'done') {
          setIsGenerating(false);
          eventSource.close();

          if (data.image_url) {
            addMessage({
              role: 'assistant',
              content: '[Generated Image]',
              image_url: data.image_url,
              timestamp: new Date().toISOString(),
            });
          }
        } else if (data.type === 'error') {
          console.error('Streaming error:', data.error);
          setIsGenerating(false);
          eventSource.close();
        }
      };

      eventSource.onerror = (error) => {
        console.error('EventSource error:', error);
        setIsGenerating(false);
        eventSource.close();

        const response = await chatAPI.sendMessage(
          selectedCharacter.id,
          userMessage.content,
          1,
          false
        );

        addMessage({
          role: 'assistant',
          content: response.content,
          timestamp: new Date().toISOString(),
        });
      };
    } catch (error) {
      console.error('Failed to send message:', error);
      setIsGenerating(false);
    }
  };

  const clearHistory = async () => {
    if (!selectedCharacter) return;

    if (confirm('Clear all chat history with this character?')) {
      try {
        await chatAPI.clearHistory(selectedCharacter.id);
        setMessages([]);
      } catch (error) {
        console.error('Failed to clear history:', error);
      }
    }
  };

  if (!selectedCharacter) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <p className="text-gray-500">Select a character to start chatting</p>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-white">
      <div className="border-b border-gray-200 p-4 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-semibold">{selectedCharacter.name}</h2>
          <p className="text-sm text-gray-500">{selectedCharacter.personality}</p>
        </div>
        <button
          onClick={clearHistory}
          className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600 transition"
        >
          Clear History
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 chat-scrollbar">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] rounded-lg px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-800'
              }`}
            >
              {message.image_url ? (
                <img
                  src={message.image_url}
                  alt="Generated"
                  className="max-w-full rounded"
                />
              ) : (
                <p className="whitespace-pre-wrap">{message.content}</p>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={isGenerating}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
          />
          <button
            type="submit"
            disabled={!input.trim() || isGenerating}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {isGenerating ? 'Sending...' : 'Send'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default ChatInterface;
