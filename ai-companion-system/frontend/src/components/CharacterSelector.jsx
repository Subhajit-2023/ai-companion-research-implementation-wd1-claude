function CharacterSelector({ characters, selectedCharacter, onSelect, onCreateNew }) {
  return (
    <div className="w-64 bg-white border-r border-gray-200 overflow-y-auto">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800">Characters</h2>
      </div>

      <div className="p-2">
        {characters.map((character) => (
          <div
            key={character.id}
            onClick={() => onSelect(character)}
            className={`p-3 mb-2 rounded-lg cursor-pointer transition ${
              selectedCharacter?.id === character.id
                ? 'bg-blue-100 border-2 border-blue-500'
                : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
            }`}
          >
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-bold">
                {character.name[0]}
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-800">{character.name}</h3>
                <p className="text-xs text-gray-500 capitalize">{character.persona_type}</p>
              </div>
            </div>
          </div>
        ))}

        {characters.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <p className="mb-4">No characters yet</p>
            <button
              onClick={onCreateNew}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
            >
              Create First Character
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default CharacterSelector;
