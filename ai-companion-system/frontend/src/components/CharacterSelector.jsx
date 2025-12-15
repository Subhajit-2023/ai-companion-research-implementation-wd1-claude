import { useState, useEffect } from 'react';
import {
  Box, Grid, Card, CardContent, CardActions, Typography, Button,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField, MenuItem,
  IconButton, Tooltip
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import axios from 'axios';

export default function CharacterSelector({ onCharacterSelect }) {
  const [characters, setCharacters] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [characterToDelete, setCharacterToDelete] = useState(null);
  const [presets, setPresets] = useState([]);
  const [newCharacter, setNewCharacter] = useState({
    name: '',
    persona_type: 'custom',
    personality: '',
    backstory: '',
    interests: '',
    speaking_style: '',
    appearance_description: '',
  });

  useEffect(() => {
    loadCharacters();
    loadPresets();
  }, []);

  const loadCharacters = async () => {
    try {
      const response = await axios.get('/api/characters/', { params: { user_id: 1 } });
      setCharacters(response.data.characters || []);
    } catch (error) {
      console.error('Error loading characters:', error);
    }
  };

  const loadPresets = async () => {
    try {
      const response = await axios.get('/api/characters/presets/list');
      setPresets(response.data.presets || []);
    } catch (error) {
      console.error('Error loading presets:', error);
    }
  };

  const handleCreateCharacter = async () => {
    try {
      const characterData = {
        ...newCharacter,
        interests: newCharacter.interests.split(',').map(i => i.trim()).filter(i => i),
        user_id: 1,
      };

      await axios.post('/api/characters/', characterData);
      setOpenDialog(false);
      loadCharacters();
      setNewCharacter({
        name: '',
        persona_type: 'custom',
        personality: '',
        backstory: '',
        interests: '',
        speaking_style: '',
        appearance_description: '',
      });
    } catch (error) {
      console.error('Error creating character:', error);
    }
  };

  const handlePresetChange = (presetType) => {
    const preset = presets.find(p => p.type === presetType);
    if (preset) {
      setNewCharacter({
        ...newCharacter,
        name: preset.name,
        persona_type: preset.type,
        personality: preset.personality,
        backstory: preset.backstory,
        interests: preset.interests.join(', '),
      });
    }
  };

  const handleDeleteClick = (character) => {
    setCharacterToDelete(character);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!characterToDelete) return;

    try {
      await axios.delete(`/api/characters/${characterToDelete.id}`);
      setDeleteDialogOpen(false);
      setCharacterToDelete(null);
      loadCharacters();
    } catch (error) {
      console.error('Error deleting character:', error);
      alert('Failed to delete character');
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h5">Your Characters</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Create Character
        </Button>
      </Box>

      <Grid container spacing={3}>
        {characters.map((character) => (
          <Grid item xs={12} sm={6} md={4} key={character.id}>
            <Card>
              <CardContent>
                <Typography variant="h6">{character.name}</Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {character.persona_type}
                </Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  {character.personality}
                </Typography>
              </CardContent>
              <CardActions sx={{ justifyContent: 'space-between' }}>
                <Button size="small" onClick={() => onCharacterSelect(character)}>
                  Chat
                </Button>
                <Box>
                  <Tooltip title="Delete character">
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDeleteClick(character)}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Character</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              select
              label="Preset"
              value={newCharacter.persona_type}
              onChange={(e) => {
                setNewCharacter({ ...newCharacter, persona_type: e.target.value });
                handlePresetChange(e.target.value);
              }}
            >
              <MenuItem value="custom">Custom</MenuItem>
              <MenuItem value="girlfriend">Girlfriend</MenuItem>
              <MenuItem value="therapist">Therapist</MenuItem>
              <MenuItem value="friend">Friend</MenuItem>
              <MenuItem value="creative_muse">Creative Muse</MenuItem>
            </TextField>

            <TextField
              label="Name"
              value={newCharacter.name}
              onChange={(e) => setNewCharacter({ ...newCharacter, name: e.target.value })}
            />

            <TextField
              label="Personality"
              multiline
              rows={2}
              value={newCharacter.personality}
              onChange={(e) => setNewCharacter({ ...newCharacter, personality: e.target.value })}
            />

            <TextField
              label="Backstory"
              multiline
              rows={3}
              value={newCharacter.backstory}
              onChange={(e) => setNewCharacter({ ...newCharacter, backstory: e.target.value })}
            />

            <TextField
              label="Interests (comma separated)"
              value={newCharacter.interests}
              onChange={(e) => setNewCharacter({ ...newCharacter, interests: e.target.value })}
            />

            <TextField
              label="Speaking Style"
              value={newCharacter.speaking_style}
              onChange={(e) => setNewCharacter({ ...newCharacter, speaking_style: e.target.value })}
            />

            <TextField
              label="Appearance Description (for image generation)"
              multiline
              rows={2}
              value={newCharacter.appearance_description}
              onChange={(e) => setNewCharacter({ ...newCharacter, appearance_description: e.target.value })}
              helperText="Describe how this character looks for AI image generation"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateCharacter} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Character</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{characterToDelete?.name}"? This action cannot be undone.
            All chat history and memories will be permanently deleted.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
