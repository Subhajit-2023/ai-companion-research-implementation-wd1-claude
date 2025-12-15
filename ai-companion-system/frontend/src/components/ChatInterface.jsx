import { useState, useEffect, useRef } from 'react';
import { Box, TextField, IconButton, Paper, Typography, CircularProgress, Avatar, Chip } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import SearchIcon from '@mui/icons-material/Search';
import NewspaperIcon from '@mui/icons-material/Newspaper';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

export default function ChatInterface({ selectedCharacter }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (selectedCharacter) {
      loadChatHistory();
    }
  }, [selectedCharacter]);

  const loadChatHistory = async () => {
    if (!selectedCharacter) return;

    try {
      const response = await axios.get(`/api/chat/history/${selectedCharacter.id}`, {
        params: { user_id: 1, limit: 50 }
      });
      setMessages(response.data.messages || []);
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || !selectedCharacter || loading) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post('/api/chat/send', {
        character_id: selectedCharacter.id,
        message: input,
        user_id: 1,
        stream: false,
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.content,
        timestamp: new Date().toISOString(),
        image_urls: response.data.image_url ? [response.data.image_url] : [],
        metadata: {
          search_performed: response.data.search_performed,
          search_query: response.data.search_query,
        },
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!selectedCharacter) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
        <Typography variant="h6" color="text.secondary">
          Select a character to start chatting
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Box sx={{ flexGrow: 1, overflow: 'auto', mb: 2 }}>
        {messages.map((message, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
              mb: 2,
            }}
          >
            {message.role === 'assistant' && (
              <Avatar sx={{ mr: 1 }}>{selectedCharacter.name[0]}</Avatar>
            )}
            <Paper
              sx={{
                p: 2,
                maxWidth: '70%',
                bgcolor: message.role === 'user' ? 'primary.dark' : 'background.paper',
              }}
            >
              {message.metadata?.search_performed && (
                <Box sx={{ mb: 1 }}>
                  <Chip
                    icon={message.metadata.search_query?.includes('news') ? <NewspaperIcon /> : <SearchIcon />}
                    label={`Searched: ${message.metadata.search_query}`}
                    size="small"
                    color="info"
                    variant="outlined"
                  />
                </Box>
              )}
              <ReactMarkdown>{message.content}</ReactMarkdown>
              {message.image_urls && message.image_urls.length > 0 && (
                <Box sx={{ mt: 1 }}>
                  {message.image_urls.map((url, i) => (
                    <img
                      key={i}
                      src={url}
                      alt="Generated"
                      style={{ maxWidth: '100%', borderRadius: 8 }}
                    />
                  ))}
                </Box>
              )}
            </Paper>
            {message.role === 'user' && (
              <Avatar sx={{ ml: 1 }}>U</Avatar>
            )}
          </Box>
        ))}
        {loading && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Avatar sx={{ mr: 1 }}>{selectedCharacter.name[0]}</Avatar>
            <CircularProgress size={20} />
            <Typography variant="body2" color="text.secondary">Thinking...</Typography>
          </Box>
        )}
        <div ref={messagesEndRef} />
      </Box>

      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type a message..."
          disabled={loading}
        />
        <IconButton
          color="primary"
          onClick={sendMessage}
          disabled={!input.trim() || loading}
        >
          <SendIcon />
        </IconButton>
      </Box>
    </Box>
  );
}
