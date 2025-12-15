function Header({ view, setView, selectedCharacter, onCreateCharacter }) {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-bold text-gray-800">AI Companion System</h1>
          {selectedCharacter && (
            <span className="text-sm text-gray-500">
              Chatting with {selectedCharacter.name}
            </span>
          )}
        </div>

        <div className="flex items-center space-x-4">
          <button
            onClick={() => setView('chat')}
            className={`px-4 py-2 rounded-lg transition ${
              view === 'chat'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Chat
          </button>

          <button
            onClick={() => setView('gallery')}
            className={`px-4 py-2 rounded-lg transition ${
              view === 'gallery'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Gallery
          </button>

          <button
            onClick={onCreateCharacter}
            className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition"
          >
            + New Character
          </button>
        </div>
      </div>
    </header>
  );
}

export default Header;
