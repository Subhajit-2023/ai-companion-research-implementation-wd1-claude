import { useState, useEffect } from 'react';
import useStore from '../store/useStore';
import { imagesAPI } from '../services/api';

function ImageGallery() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [prompt, setPrompt] = useState('');
  const [style, setStyle] = useState('realistic');

  const { selectedCharacter, imageGallery, setImageGallery, addImageToGallery, sdAvailable } = useStore();

  useEffect(() => {
    loadGallery();
  }, [selectedCharacter]);

  const loadGallery = async () => {
    try {
      const data = await imagesAPI.getGallery(selectedCharacter?.id);
      setImageGallery(data.images);
    } catch (error) {
      console.error('Failed to load gallery:', error);
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!prompt.trim() || isGenerating) return;

    setIsGenerating(true);

    try {
      const data = await imagesAPI.generate({
        prompt: prompt.trim(),
        style,
        character_id: selectedCharacter?.id,
      });

      addImageToGallery(data.image);
      setPrompt('');
      alert('Image generated successfully!');
    } catch (error) {
      console.error('Failed to generate image:', error);
      alert('Image generation failed. Make sure Stable Diffusion WebUI is running.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleGenerateCharacter = async () => {
    if (!selectedCharacter || !selectedCharacter.appearance_description) {
      alert('Selected character has no appearance description');
      return;
    }

    setIsGenerating(true);

    try {
      const data = await imagesAPI.generateCharacter(selectedCharacter.id, 'portrait', style);
      addImageToGallery(data.image);
      alert('Character image generated successfully!');
    } catch (error) {
      console.error('Failed to generate character image:', error);
      alert('Character image generation failed.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-gray-50">
      <div className="bg-white border-b border-gray-200 p-6">
        <h2 className="text-2xl font-bold mb-4">Image Gallery</h2>

        {!sdAvailable && (
          <div className="mb-4 p-4 bg-yellow-100 border border-yellow-300 rounded-lg">
            <p className="text-sm text-yellow-800">
              Stable Diffusion WebUI is not available. Start it with --api flag to enable image generation.
            </p>
          </div>
        )}

        <form onSubmit={handleGenerate} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Image Prompt
            </label>
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the image you want to generate..."
              disabled={!sdAvailable || isGenerating}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            />
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Style
              </label>
              <select
                value={style}
                onChange={(e) => setStyle(e.target.value)}
                disabled={!sdAvailable || isGenerating}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              >
                <option value="realistic">Realistic</option>
                <option value="anime">Anime</option>
                <option value="manga">Manga</option>
                <option value="artistic">Artistic</option>
                <option value="photographic">Photographic</option>
              </select>
            </div>

            <div className="flex space-x-2">
              <button
                type="submit"
                disabled={!sdAvailable || !prompt.trim() || isGenerating}
                className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                {isGenerating ? 'Generating...' : 'Generate'}
              </button>

              {selectedCharacter && selectedCharacter.appearance_description && (
                <button
                  type="button"
                  onClick={handleGenerateCharacter}
                  disabled={!sdAvailable || isGenerating}
                  className="px-6 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  Generate {selectedCharacter.name}
                </button>
              )}
            </div>
          </div>
        </form>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {imageGallery.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <p>No images yet. Generate your first image!</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {imageGallery.map((image) => (
              <div key={image.id} className="bg-white rounded-lg shadow overflow-hidden">
                <img
                  src={image.file_url}
                  alt={image.prompt}
                  className="w-full h-48 object-cover"
                />
                <div className="p-3">
                  <p className="text-xs text-gray-600 line-clamp-2">{image.prompt}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(image.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default ImageGallery;
