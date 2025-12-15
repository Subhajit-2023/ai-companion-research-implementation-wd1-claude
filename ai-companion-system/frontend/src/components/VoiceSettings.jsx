import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Switch,
  FormControlLabel,
  Select,
  MenuItem,
  Slider,
  Button,
  Chip,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
  Grid,
  Paper,
  Divider
} from '@mui/material';
import {
  VolumeUp,
  Mic,
  PlayArrow,
  Stop,
  Settings as SettingsIcon,
  CheckCircle,
  Error as ErrorIcon,
  Download
} from '@mui/icons-material';
import axios from 'axios';

export default function VoiceSettings({ character, onUpdate }) {
  const [voiceSettings, setVoiceSettings] = useState({
    voice_enabled: false,
    voice_id: '',
    voice_speed: 1.0
  });
  const [availableVoices, setAvailableVoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [ttsStatus, setTtsStatus] = useState(null);
  const [sttStatus, setSttStatus] = useState(null);
  const [testAudioPlaying, setTestAudioPlaying] = useState(false);
  const [testAudio, setTestAudio] = useState(null);

  useEffect(() => {
    loadVoiceSettings();
    checkVoiceServices();
    loadAvailableVoices();
  }, [character]);

  const loadVoiceSettings = async () => {
    if (!character) return;

    try {
      const response = await axios.get(`/api/voice/characters/${character.id}/voice`);
      setVoiceSettings(response.data.voice_settings);
    } catch (error) {
      console.error('Error loading voice settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAvailableVoices = async () => {
    try {
      const response = await axios.get('/api/voice/tts/voices');
      setAvailableVoices(response.data);
    } catch (error) {
      console.error('Error loading voices:', error);
    }
  };

  const checkVoiceServices = async () => {
    try {
      const [ttsResponse, sttResponse] = await Promise.all([
        axios.get('/api/voice/tts/check'),
        axios.get('/api/voice/stt/check')
      ]);
      setTtsStatus(ttsResponse.data);
      setSttStatus(sttResponse.data);
    } catch (error) {
      console.error('Error checking voice services:', error);
    }
  };

  const handleVoiceToggle = async (enabled) => {
    const updated = { ...voiceSettings, voice_enabled: enabled };
    await saveVoiceSettings(updated);
  };

  const handleVoiceSelect = async (voiceId) => {
    const updated = { ...voiceSettings, voice_id: voiceId };
    await saveVoiceSettings(updated);
  };

  const handleSpeedChange = async (speed) => {
    const updated = { ...voiceSettings, voice_speed: speed };
    setVoiceSettings(updated);
  };

  const handleSpeedCommit = async () => {
    await saveVoiceSettings(voiceSettings);
  };

  const saveVoiceSettings = async (settings) => {
    try {
      await axios.put(`/api/voice/characters/${character.id}/voice`, settings);
      setVoiceSettings(settings);
      if (onUpdate) onUpdate(settings);
    } catch (error) {
      console.error('Error saving voice settings:', error);
    }
  };

  const testVoice = async () => {
    if (!voiceSettings.voice_id) return;

    setTestAudioPlaying(true);
    try {
      const response = await axios.post('/api/voice/tts/synthesize', {
        text: `Hello! I'm ${character.name}. This is how my voice sounds.`,
        voice_id: voiceSettings.voice_id,
        speed: voiceSettings.voice_speed
      });

      // Play audio
      const audio = new Audio(response.data.audio_url);
      setTestAudio(audio);

      audio.onended = () => {
        setTestAudioPlaying(false);
      };

      audio.play();
    } catch (error) {
      console.error('Error testing voice:', error);
      setTestAudioPlaying(false);
    }
  };

  const stopTestVoice = () => {
    if (testAudio) {
      testAudio.pause();
      testAudio.currentTime = 0;
      setTestAudioPlaying(false);
    }
  };

  const getVoiceInfo = (voiceId) => {
    return availableVoices.find(v => v.voice_id === voiceId);
  };

  const selectedVoiceInfo = voiceSettings.voice_id ? getVoiceInfo(voiceSettings.voice_id) : null;

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <VolumeUp /> Voice Settings
      </Typography>

      {/* Service Status */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Voice Services Status
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Box display="flex" alignItems="center" gap={1}>
              {ttsStatus?.available ? (
                <CheckCircle color="success" fontSize="small" />
              ) : (
                <ErrorIcon color="error" fontSize="small" />
              )}
              <Typography variant="body2">
                TTS: {ttsStatus?.available ? 'Available' : 'Not Available'}
              </Typography>
            </Box>
            {ttsStatus && (
              <Typography variant="caption" color="text.secondary">
                {ttsStatus.models_downloaded} voice models installed
              </Typography>
            )}
          </Grid>
          <Grid item xs={6}>
            <Box display="flex" alignItems="center" gap={1}>
              {sttStatus?.available ? (
                <CheckCircle color="success" fontSize="small" />
              ) : (
                <ErrorIcon color="error" fontSize="small" />
              )}
              <Typography variant="body2">
                STT: {sttStatus?.available ? 'Available' : 'Not Available'}
              </Typography>
            </Box>
            {sttStatus?.model_info && (
              <Typography variant="caption" color="text.secondary">
                Model: {sttStatus.model_info.model_size}
              </Typography>
            )}
          </Grid>
        </Grid>
      </Paper>

      {!ttsStatus?.available && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          TTS not available. Install Piper and download voice models.
          <Button size="small" href="https://github.com/rhasspy/piper" target="_blank" sx={{ ml: 1 }}>
            Learn More
          </Button>
        </Alert>
      )}

      {/* Voice Enable Toggle */}
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <FormControlLabel
            control={
              <Switch
                checked={voiceSettings.voice_enabled}
                onChange={(e) => handleVoiceToggle(e.target.checked)}
                disabled={!ttsStatus?.available}
              />
            }
            label={
              <Box>
                <Typography variant="body1">Enable Voice</Typography>
                <Typography variant="caption" color="text.secondary">
                  Character will speak responses out loud
                </Typography>
              </Box>
            }
          />
        </CardContent>
      </Card>

      {/* Voice Selection */}
      {voiceSettings.voice_enabled && (
        <>
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="subtitle2" gutterBottom>
                Select Voice
              </Typography>
              <Select
                fullWidth
                value={voiceSettings.voice_id || ''}
                onChange={(e) => handleVoiceSelect(e.target.value)}
                disabled={!ttsStatus?.available}
              >
                {availableVoices.map((voice) => (
                  <MenuItem key={voice.voice_id} value={voice.voice_id}>
                    <Box display="flex" alignItems="center" justifyContent="space-between" width="100%">
                      <Box>
                        <Typography variant="body2">{voice.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {voice.description}
                        </Typography>
                      </Box>
                      {voice.installed ? (
                        <Chip label="Installed" size="small" color="success" />
                      ) : (
                        <Chip label="Not Installed" size="small" icon={<Download />} />
                      )}
                    </Box>
                  </MenuItem>
                ))}
              </Select>

              {selectedVoiceInfo && (
                <Box mt={2}>
                  <Typography variant="caption" color="text.secondary">
                    Gender: {selectedVoiceInfo.gender} | Language: {selectedVoiceInfo.language} | Quality: {selectedVoiceInfo.quality}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>

          {/* Voice Speed */}
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="subtitle2" gutterBottom>
                Speech Speed: {voiceSettings.voice_speed.toFixed(1)}x
              </Typography>
              <Slider
                value={voiceSettings.voice_speed}
                onChange={(e, value) => handleSpeedChange(value)}
                onChangeCommitted={handleSpeedCommit}
                min={0.5}
                max={2.0}
                step={0.1}
                marks={[
                  { value: 0.5, label: '0.5x' },
                  { value: 1.0, label: '1.0x' },
                  { value: 1.5, label: '1.5x' },
                  { value: 2.0, label: '2.0x' }
                ]}
                disabled={!ttsStatus?.available}
              />
            </CardContent>
          </Card>

          {/* Test Voice */}
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Typography variant="subtitle2">Test Voice</Typography>
                <Button
                  variant="contained"
                  startIcon={testAudioPlaying ? <Stop /> : <PlayArrow />}
                  onClick={testAudioPlaying ? stopTestVoice : testVoice}
                  disabled={!voiceSettings.voice_id || !ttsStatus?.available}
                >
                  {testAudioPlaying ? 'Stop' : 'Test Voice'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </>
      )}

      {/* Voice Installation Help */}
      {ttsStatus && !ttsStatus.available && (
        <Alert severity="info">
          <Typography variant="subtitle2" gutterBottom>
            To enable voice features:
          </Typography>
          <ol style={{ marginLeft: -20 }}>
            <li>Install Piper TTS</li>
            <li>Download voice models</li>
            <li>Place models in the correct directory</li>
          </ol>
          <Typography variant="caption">
            See documentation for detailed instructions
          </Typography>
        </Alert>
      )}
    </Box>
  );
}
