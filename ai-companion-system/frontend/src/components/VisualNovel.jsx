import { useState, useEffect } from 'react';
import {
  Box, Typography, Button, Card, CardMedia, CardContent, Grid,
  Dialog, DialogTitle, DialogContent, List, ListItem, ListItemText,
  Paper, Fade, ButtonGroup, Chip
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import SaveIcon from '@mui/icons-material/Save';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import axios from 'axios';

export default function VisualNovel() {
  const [novels, setNovels] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [currentScene, setCurrentScene] = useState(null);
  const [sceneAssets, setSceneAssets] = useState(null);
  const [userSessions, setUserSessions] = useState([]);
  const [sessionDialogOpen, setSessionDialogOpen] = useState(false);
  const [selectedNovel, setSelectedNovel] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadNovels();
    loadUserSessions();
  }, []);

  const loadNovels = async () => {
    try {
      const response = await axios.get('/api/vn/novels');
      setNovels(response.data.novels || []);
    } catch (error) {
      console.error('Error loading novels:', error);
    }
  };

  const loadUserSessions = async () => {
    try {
      const response = await axios.get('/api/vn/sessions/user/1');
      setUserSessions(response.data.sessions || []);
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  const startNewSession = async (novelId) => {
    setLoading(true);
    try {
      const response = await axios.post('/api/vn/sessions/start', {
        visual_novel_id: novelId,
        user_id: 1,
      });

      setCurrentSession(response.data.session);
      setCurrentScene(response.data.current_scene);
      await loadSceneAssets(response.data.current_scene.id);
    } catch (error) {
      console.error('Error starting session:', error);
      alert('Failed to start visual novel');
    } finally {
      setLoading(false);
    }
  };

  const loadSession = async (sessionId) => {
    setLoading(true);
    try {
      const response = await axios.get(`/api/vn/sessions/${sessionId}`);
      setCurrentSession(response.data.session);
      setCurrentScene(response.data.current_scene);
      if (response.data.current_scene) {
        await loadSceneAssets(response.data.current_scene.id);
      }
      setSessionDialogOpen(false);
    } catch (error) {
      console.error('Error loading session:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSceneAssets = async (sceneId) => {
    try {
      const response = await axios.get(`/api/vn/scenes/${sceneId}/assets`);
      setSceneAssets(response.data.assets || []);
    } catch (error) {
      console.error('Error loading assets:', error);
      setSceneAssets([]);
    }
  };

  const advanceScene = async () => {
    if (!currentSession) return;

    setLoading(true);
    try {
      const response = await axios.post(`/api/vn/sessions/${currentSession.id}/advance`);

      if (response.data.ending) {
        alert(`Story Complete! Ending: ${response.data.ending}`);
        setCurrentSession(null);
        setCurrentScene(null);
        setSceneAssets(null);
        loadUserSessions();
      } else {
        setCurrentScene(response.data.current_scene);
        setCurrentSession(response.data.session);
        await loadSceneAssets(response.data.current_scene.id);
      }
    } catch (error) {
      console.error('Error advancing scene:', error);
      if (error.response?.data?.message) {
        alert(error.response.data.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const makeChoice = async (choiceIndex) => {
    if (!currentSession) return;

    setLoading(true);
    try {
      const response = await axios.post(`/api/vn/sessions/${currentSession.id}/choice`, {
        session_id: currentSession.id,
        choice_index: choiceIndex,
      });

      setCurrentScene(response.data.current_scene);
      setCurrentSession(response.data.session);
      await loadSceneAssets(response.data.current_scene.id);
    } catch (error) {
      console.error('Error making choice:', error);
      alert('Failed to make choice');
    } finally {
      setLoading(false);
    }
  };

  const generateSceneImage = async (assetType = 'background') => {
    if (!currentScene) return;

    setLoading(true);
    try {
      await axios.post(`/api/vn/scenes/${currentScene.id}/generate-image`, null, {
        params: { asset_type: assetType }
      });
      await loadSceneAssets(currentScene.id);
    } catch (error) {
      console.error('Error generating image:', error);
      alert('Image generation is not available. Make sure Stable Diffusion is running.');
    } finally {
      setLoading(false);
    }
  };

  const getBackgroundAsset = () => {
    if (!sceneAssets || sceneAssets.length === 0) return null;
    return sceneAssets.find(asset => asset.asset_type === 'background');
  };

  const getCharacterAsset = () => {
    if (!sceneAssets || sceneAssets.length === 0) return null;
    return sceneAssets.find(asset => asset.asset_type === 'character');
  };

  // Novel Selection View
  if (!currentSession || !currentScene) {
    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5">Visual Novels</Typography>
          {userSessions.length > 0 && (
            <Button
              variant="outlined"
              startIcon={<SaveIcon />}
              onClick={() => setSessionDialogOpen(true)}
            >
              Load Save ({userSessions.length})
            </Button>
          )}
        </Box>

        <Grid container spacing={3}>
          {novels.map((novel) => (
            <Grid item xs={12} md={6} key={novel.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 1 }}>
                    <MenuBookIcon color="primary" />
                    <Typography variant="h6">{novel.title}</Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {novel.description}
                  </Typography>
                  <Box sx={{ mt: 2, mb: 2 }}>
                    <Chip label={novel.genre} size="small" sx={{ mr: 1 }} />
                    <Chip label={`~${novel.estimated_playtime} min`} size="small" variant="outlined" />
                  </Box>
                  <Button
                    variant="contained"
                    startIcon={<PlayArrowIcon />}
                    onClick={() => startNewSession(novel.id)}
                    disabled={loading}
                    fullWidth
                  >
                    Start New Game
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Dialog open={sessionDialogOpen} onClose={() => setSessionDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Load Save</DialogTitle>
          <DialogContent>
            <List>
              {userSessions.map((session) => (
                <ListItem
                  key={session.id}
                  button
                  onClick={() => loadSession(session.id)}
                >
                  <ListItemText
                    primary={session.save_name}
                    secondary={`${session.novel_title} - ${session.playtime_minutes} min played`}
                  />
                </ListItem>
              ))}
            </List>
          </DialogContent>
        </Dialog>
      </Box>
    );
  }

  // Visual Novel Player View
  const backgroundAsset = getBackgroundAsset();
  const characterAsset = getCharacterAsset();

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Visual Novel Display */}
      <Paper
        sx={{
          flexGrow: 1,
          position: 'relative',
          overflow: 'hidden',
          backgroundImage: backgroundAsset
            ? `url(${backgroundAsset.file_url})`
            : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'flex-end',
          minHeight: '500px',
        }}
      >
        {/* Character Sprite (if available) */}
        {characterAsset && (
          <Fade in={true}>
            <Box
              component="img"
              src={characterAsset.file_url}
              sx={{
                position: 'absolute',
                bottom: 0,
                right: '10%',
                maxHeight: '80%',
                objectFit: 'contain',
              }}
            />
          </Fade>
        )}

        {/* Text Box */}
        <Fade in={true}>
          <Paper
            sx={{
              mx: 3,
              mb: 3,
              p: 3,
              backgroundColor: 'rgba(0, 0, 0, 0.85)',
              backdropFilter: 'blur(10px)',
            }}
          >
            {/* Chapter/Scene Info */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="caption" color="primary">
                {currentScene.chapter}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Scene {currentScene.scene_number}
              </Typography>
            </Box>

            {/* Scene Title */}
            {currentScene.title && (
              <Typography variant="h6" gutterBottom color="primary">
                {currentScene.title}
              </Typography>
            )}

            {/* Character Name */}
            {currentScene.character_name && (
              <Typography variant="subtitle2" color="secondary" gutterBottom>
                {currentScene.character_name}
              </Typography>
            )}

            {/* Narrative Text */}
            {currentScene.narrative_text && (
              <Typography variant="body1" paragraph sx={{ whiteSpace: 'pre-wrap' }}>
                {currentScene.narrative_text}
              </Typography>
            )}

            {/* Character Dialogue */}
            {currentScene.character_dialogue && (
              <Typography variant="body1" sx={{ fontStyle: 'italic', whiteSpace: 'pre-wrap' }}>
                "{currentScene.character_dialogue}"
              </Typography>
            )}
          </Paper>
        </Fade>
      </Paper>

      {/* Controls */}
      <Box sx={{ p: 2, display: 'flex', gap: 2, flexDirection: 'column' }}>
        {/* Choices (if choice scene) */}
        {currentScene.scene_type === 'choice' && currentScene.choices && currentScene.choices.length > 0 && (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Typography variant="subtitle2" color="text.secondary">
              Make a choice:
            </Typography>
            {currentScene.choices.map((choice, index) => (
              <Button
                key={index}
                variant="outlined"
                onClick={() => makeChoice(index)}
                disabled={loading}
                fullWidth
                sx={{ justifyContent: 'flex-start', textAlign: 'left' }}
              >
                {choice.text}
              </Button>
            ))}
          </Box>
        )}

        {/* Action Buttons */}
        <ButtonGroup fullWidth>
          {currentScene.scene_type !== 'choice' && !currentScene.is_ending && (
            <Button
              variant="contained"
              onClick={advanceScene}
              disabled={loading}
            >
              Continue
            </Button>
          )}

          {currentScene.is_ending && (
            <Button
              variant="contained"
              onClick={() => {
                setCurrentSession(null);
                setCurrentScene(null);
                setSceneAssets(null);
                loadUserSessions();
              }}
            >
              Return to Menu
            </Button>
          )}

          <Button
            variant="outlined"
            onClick={() => generateSceneImage('background')}
            disabled={loading || !currentScene.background_image_prompt}
          >
            Generate Background
          </Button>

          <Button
            variant="outlined"
            onClick={() => generateSceneImage('character')}
            disabled={loading || !currentScene.character_image_prompt}
          >
            Generate Character
          </Button>
        </ButtonGroup>
      </Box>
    </Box>
  );
}
