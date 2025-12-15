import { useState, useEffect } from 'react';
import {
  Box, Grid, Card, CardMedia, TextField, Button, MenuItem, Typography, CircularProgress
} from '@mui/material';
import axios from 'axios';

export default function ImageGeneration() {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [prompt, setPrompt] = useState('');
  const [style, setStyle] = useState('realistic');
  const [styles, setStyles] = useState(['realistic', 'anime', 'manga', 'artistic']);

  useEffect(() => {
    loadImages();
    loadStyles();
  }, []);

  const loadImages = async () => {
    try {
      const response = await axios.get('/api/images/history', {
        params: { user_id: 1, limit: 20 }
      });
      setImages(response.data.images || []);
    } catch (error) {
      console.error('Error loading images:', error);
    }
  };

  const loadStyles = async () => {
    try {
      const response = await axios.get('/api/images/styles');
      setStyles(response.data.styles || ['realistic', 'anime', 'manga', 'artistic']);
    } catch (error) {
      console.error('Error loading styles:', error);
    }
  };

  const generateImage = async () => {
    if (!prompt.trim() || loading) return;

    setLoading(true);
    try {
      const response = await axios.post('/api/images/generate', {
        prompt: prompt,
        style: style,
        user_id: 1,
        enhance_prompt: true,
      });

      setImages(prev => [response.data, ...prev]);
      setPrompt('');
    } catch (error) {
      console.error('Error generating image:', error);
      alert('Failed to generate image. Make sure Stable Diffusion WebUI is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>Image Generation</Typography>

      <Box sx={{ mb: 4, display: 'flex', gap: 2 }}>
        <TextField
          fullWidth
          multiline
          rows={2}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe the image you want to generate..."
          disabled={loading}
        />
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, minWidth: 200 }}>
          <TextField
            select
            label="Style"
            value={style}
            onChange={(e) => setStyle(e.target.value)}
            disabled={loading}
          >
            {styles.map((s) => (
              <MenuItem key={s} value={s}>{s}</MenuItem>
            ))}
          </TextField>
          <Button
            variant="contained"
            onClick={generateImage}
            disabled={!prompt.trim() || loading}
            fullWidth
          >
            {loading ? <CircularProgress size={24} /> : 'Generate'}
          </Button>
        </Box>
      </Box>

      <Grid container spacing={2}>
        {images.map((image) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={image.id}>
            <Card>
              <CardMedia
                component="img"
                image={image.file_url}
                alt={image.prompt}
                sx={{ height: 300, objectFit: 'cover' }}
              />
              <Box sx={{ p: 1 }}>
                <Typography variant="caption" color="text.secondary" noWrap>
                  {image.prompt}
                </Typography>
              </Box>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
