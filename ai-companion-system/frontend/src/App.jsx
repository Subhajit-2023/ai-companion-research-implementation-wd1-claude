import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { useState } from 'react';
import Layout from './components/Layout';
import ChatInterface from './components/ChatInterface';
import CharacterSelector from './components/CharacterSelector';
import ImageGeneration from './components/ImageGeneration';
import Settings from './components/Settings';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#2196f3',
    },
    secondary: {
      main: '#f50057',
    },
    background: {
      default: '#0a0e27',
      paper: '#141b2d',
    },
  },
});

function App() {
  const [selectedView, setSelectedView] = useState('chat');
  const [selectedCharacter, setSelectedCharacter] = useState(null);

  const renderView = () => {
    switch (selectedView) {
      case 'chat':
        return <ChatInterface selectedCharacter={selectedCharacter} />;
      case 'characters':
        return <CharacterSelector onCharacterSelect={setSelectedCharacter} />;
      case 'images':
        return <ImageGeneration />;
      case 'settings':
        return <Settings />;
      default:
        return <ChatInterface selectedCharacter={selectedCharacter} />;
    }
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Layout
        selectedView={selectedView}
        onViewChange={setSelectedView}
        selectedCharacter={selectedCharacter}
      >
        {renderView()}
      </Layout>
    </ThemeProvider>
  );
}

export default App;
