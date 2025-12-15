import { Box, Typography, Paper, Switch, FormControlLabel } from '@mui/material';

export default function Settings() {
  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>Settings</Typography>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>Features</Typography>
        <FormControlLabel
          control={<Switch defaultChecked />}
          label="Enable Memory System"
        />
        <FormControlLabel
          control={<Switch defaultChecked />}
          label="Enable Web Search"
        />
        <FormControlLabel
          control={<Switch defaultChecked />}
          label="Enable Image Generation"
        />

        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>System Information</Typography>
        <Typography variant="body2">Version: 1.0.0</Typography>
        <Typography variant="body2">LLM: Dolphin Mistral</Typography>
        <Typography variant="body2">Image Model: Stable Diffusion XL</Typography>
      </Paper>
    </Box>
  );
}
