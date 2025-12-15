import { useState, useEffect } from 'react';
import useStore from './store/useStore';
import { charactersAPI, chatAPI, imagesAPI } from './services/api';
import ChatInterface from './components/ChatInterface';
import CharacterSelector from './components/CharacterSelector';
import ImageGallery from './components/ImageGallery';
import Header from './components/Header';

function App() {
  const [view, setView] = useState('chat');
  const [showCharacterModal, setShowCharacterModal] = useState(false);

  const {
    characters,
    selectedCharacter,
    setCharacters,
    setSelectedCharacter,
    setSdAvailable,
  } = useStore();

  useEffect(() => {
    loadCharacters();
    checkImageGenerationStatus();
  }, []);

  const loadCharacters = async () => {
    try {
      const data = await charactersAPI.list();
      setCharacters(data.characters);

      if (data.characters.length > 0 && !selectedCharacter) {
        setSelectedCharacter(data.characters[0]);
      }
    } catch (error) {
      console.error('Failed to load characters:', error);
    }
  };

  const checkImageGenerationStatus = async () => {
    try {
      const status = await imagesAPI.checkStatus();
      setSdAvailable(status.available);
    } catch (error) {
      console.error('Failed to check image generation status:', error);
    }
  };

  const handleCreateCharacter = async (templateName) => {
    try {
      const newCharacter = await charactersAPI.createFromTemplate(templateName);
      await loadCharacters();
      setSelectedCharacter(newCharacter);
      setShowCharacterModal(false);
    } catch (error) {
      console.error('Failed to create character:', error);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <Header
        view={view}
        setView={setView}
        selectedCharacter={selectedCharacter}
        onCreateCharacter={() => setShowCharacterModal(true)}
      />

      <div className="flex flex-1 overflow-hidden">
        <CharacterSelector
          characters={characters}
          selectedCharacter={selectedCharacter}
          onSelect={setSelectedCharacter}
          onCreateNew={() => setShowCharacterModal(true)}
        />

        <div className="flex-1 flex flex-col">
          {view === 'chat' && <ChatInterface />}
          {view === 'gallery' && <ImageGallery />}
        </div>
      </div>

      {showCharacterModal && (
        <CharacterCreationModal
          onClose={() => setShowCharacterModal(false)}
          onCreate={handleCreateCharacter}
        />
      )}
    </div>
  );
}

function CharacterCreationModal({ onClose, onCreate }) {
  const [templates, setTemplates] = useState([]);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const data = await charactersAPI.listTemplates();
      setTemplates(data.templates);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Create New Character</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {templates.map((template) => (
            <div
              key={template.name}
              className="border rounded-lg p-4 hover:border-blue-500 cursor-pointer transition"
              onClick={() => onCreate(template.name)}
            >
              <h3 className="text-lg font-semibold mb-2">{template.display_name}</h3>
              <p className="text-sm text-gray-600 mb-2">{template.personality}</p>
              <p className="text-xs text-gray-500">{template.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
