# Troubleshooting Guide

Common issues and solutions for AI Companion System.

## Installation Issues

### Python Not Found

**Problem**: `python: command not found`

**Solution**:
1. Install Python 3.10 or 3.11 from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Restart terminal
4. Verify: `python --version`

### Node.js Not Found

**Problem**: `node: command not found`

**Solution**:
1. Install Node.js 18+ from [nodejs.org](https://nodejs.org/)
2. Restart terminal
3. Verify: `node --version` and `npm --version`

### Permission Errors on Windows

**Problem**: PowerShell script execution blocked

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## LLM Issues

### Ollama Not Running

**Problem**: `Connection refused to localhost:11434`

**Solution**:
```bash
# Start Ollama service
ollama serve

# Or on Windows, Ollama should start automatically
# Check Task Manager for "ollama" process
```

### Model Not Found

**Problem**: `Model dolphin-mistral:7b-v2.8 not found`

**Solution**:
```bash
# List available models
ollama list

# Download the model
ollama pull dolphin-mistral:7b-v2.8

# Verify it's downloaded
ollama list
```

### Slow Response Times

**Problem**: LLM takes too long to respond

**Solution**:
1. Use smaller quantized model (Q4_K_M)
2. Reduce `LLM_MAX_TOKENS` in config
3. Close other GPU applications
4. Check CPU/RAM usage

## Image Generation Issues

### Stable Diffusion API Not Available

**Problem**: `SD API not available` or connection errors

**Solution**:
1. Make sure SD WebUI is running: `http://127.0.0.1:7860`
2. Check `webui-user.bat` has `--api` flag
3. Restart SD WebUI
4. Verify in backend logs

### Out of Memory (OOM) Errors

**Problem**: CUDA out of memory during image generation

**Solution**:
1. **Use --xformers**: Add to `webui-user.bat`: `--xformers`
2. **Reduce resolution**: Use 768x768 instead of 1024x1024
3. **Reduce steps**: Try 20-25 instead of 30
4. **Close other GPU apps**: Chrome, games, etc.
5. **Enable VAE optimization**: Add `--no-half-vae` flag

### Images Are Low Quality

**Problem**: Generated images look bad

**Solution**:
1. **Increase steps**: Try 30-40 steps
2. **Use better prompts**: Be more descriptive
3. **Check model**: Make sure SDXL base is loaded
4. **Adjust CFG scale**: Try 7-9
5. **Use LoRAs**: Download quality LoRAs from Civitai
6. **Enable enhancer**: Set `enhance_prompt=True`

### Wrong Model Loaded

**Problem**: SD generates wrong style images

**Solution**:
1. Check current model in SD WebUI
2. Set correct model in `config.py`: `SD_MODEL`
3. Restart backend after config change
4. Verify model in `http://127.0.0.1:7860`

## Database Issues

### Database Locked

**Problem**: `database is locked` error

**Solution**:
1. Close all backend instances
2. Delete `companions.db-shm` and `companions.db-wal` files
3. Restart backend

### Missing Tables

**Problem**: Table doesn't exist errors

**Solution**:
```bash
cd backend
.\venv\Scripts\activate
python database/db.py
```

## Memory System Issues

### ChromaDB Errors

**Problem**: ChromaDB collection errors

**Solution**:
1. Delete ChromaDB folder: `data/chromadb`
2. Restart backend (will recreate)
3. Check disk space
4. Verify sentence-transformers is installed

### Memory Not Working

**Problem**: Character doesn't remember conversations

**Solution**:
1. Check `MEMORY_ENABLED=true` in config
2. Verify ChromaDB is working in logs
3. Test with explicit memory: Use character memories endpoint
4. Restart backend

## Frontend Issues

### Blank Page

**Problem**: Frontend shows blank page

**Solution**:
1. Check browser console (F12) for errors
2. Verify backend is running: `http://localhost:8000/health`
3. Clear browser cache
4. Try incognito mode
5. Check frontend logs in terminal

### Images Not Displaying

**Problem**: Generated images don't show

**Solution**:
1. Check image URLs in browser Network tab
2. Verify images exist in `data/images/`
3. Check file permissions
4. Restart backend

### WebSocket Errors

**Problem**: Real-time features not working

**Solution**:
1. Use regular polling instead of WebSocket (already implemented)
2. Check CORS settings in backend
3. Verify proxy configuration in `vite.config.js`

## Performance Issues

### High CPU Usage

**Problem**: Backend uses too much CPU

**Solution**:
1. Close unused characters/chats
2. Reduce conversation history limit
3. Disable web search if not needed
4. Check for memory leaks in logs

### High RAM Usage

**Problem**: System uses too much RAM

**Solution**:
1. Reduce ChromaDB cache size
2. Limit image cache
3. Use smaller LLM model
4. Close other applications

### GPU Not Being Used

**Problem**: Everything runs on CPU

**Solution**:
1. Verify NVIDIA drivers: `nvidia-smi`
2. Check CUDA installation
3. Reinstall PyTorch with CUDA support:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```
4. Restart system

## Network Issues

### API Connection Errors

**Problem**: Frontend can't connect to backend

**Solution**:
1. Check backend is running: `http://localhost:8000`
2. Check firewall settings
3. Verify ports 8000 and 5173 are available
4. Try different port in config

### CORS Errors

**Problem**: CORS policy blocking requests

**Solution**:
1. Verify frontend URL in backend `CORS_ORIGINS`
2. Add your URL to `config.py`
3. Restart backend
4. Clear browser cache

## Web Search Issues

### DuckDuckGo Not Working

**Problem**: Web search returns no results

**Solution**:
1. Check internet connection
2. Verify `ENABLE_WEB_SEARCH=true`
3. Test with simple query
4. Check rate limiting
5. Try alternative search provider

## Character Issues

### Character Not Responding Correctly

**Problem**: Character doesn't match personality

**Solution**:
1. Review character settings
2. Make personality description detailed
3. Add more to backstory
4. Adjust speaking style
5. Test with different prompts

### Image Generation Not Matching Character

**Problem**: Generated images don't look like character description

**Solution**:
1. Improve `appearance_description`
2. Be very specific (hair color, clothing, features)
3. Use style-specific keywords
4. Test prompts in SD WebUI directly
5. Consider using character-specific LoRAs

## Getting More Help

### Check Logs

**Backend logs**: Terminal running backend
**Frontend logs**: Browser console (F12)
**SD logs**: Terminal running WebUI
**Ollama logs**: Check Ollama terminal

### Diagnostic Commands

```bash
# Check GPU
nvidia-smi

# Check Ollama
ollama list
ollama ps

# Check backend health
curl http://localhost:8000/health

# Check SD WebUI
curl http://127.0.0.1:7860/sdapi/v1/sd-models
```

### System Information

Collect this info when reporting issues:
- Windows version
- GPU model and VRAM
- Python version
- Node.js version
- Ollama version
- Error messages
- Logs

### Common Error Messages

#### "CUDA out of memory"
- Close other GPU applications
- Reduce batch size
- Use --xformers
- Lower resolution

#### "Model not found"
- Download the model with ollama pull
- Check model name in config

#### "Connection refused"
- Start the required service (Ollama/SD)
- Check firewall
- Verify ports

#### "Module not found"
- Install requirements: `pip install -r requirements.txt`
- Activate virtual environment
- Check Python path

## Still Having Issues?

1. Check GitHub Issues
2. Review documentation again
3. Search error message online
4. Check Ollama/SD WebUI documentation
5. Create detailed issue report with:
   - Steps to reproduce
   - Error messages
   - System information
   - Logs
