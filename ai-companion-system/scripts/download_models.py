"""
Model Downloader Script
Downloads and sets up AI models for the companion system
"""
import subprocess
import sys
import os
from pathlib import Path

def check_ollama():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def download_llm_model(model_name="dolphin-mistral:7b-v2.8"):
    """Download LLM model using Ollama"""
    print(f"\n{'='*50}")
    print(f"Downloading LLM: {model_name}")
    print(f"{'='*50}\n")

    if not check_ollama():
        print("ERROR: Ollama not found!")
        print("Please install Ollama from: https://ollama.ai/download")
        return False

    print("Checking available models...")
    subprocess.run(["ollama", "list"])

    print(f"\nDownloading {model_name}...")
    print("This may take a while depending on your internet speed...")

    result = subprocess.run(["ollama", "pull", model_name])

    if result.returncode == 0:
        print(f"\n✓ Successfully downloaded {model_name}")
        return True
    else:
        print(f"\n✗ Failed to download {model_name}")
        return False

def test_llm_model(model_name="dolphin-mistral:7b-v2.8"):
    """Test if LLM model works"""
    print(f"\nTesting {model_name}...")

    result = subprocess.run(
        ["ollama", "run", model_name, "Say hello!"],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode == 0:
        print(f"✓ Model test successful!")
        print(f"Response: {result.stdout[:100]}...")
        return True
    else:
        print(f"✗ Model test failed")
        return False

def setup_stable_diffusion():
    """Instructions for Stable Diffusion setup"""
    print(f"\n{'='*50}")
    print("Stable Diffusion WebUI Setup")
    print(f"{'='*50}\n")

    print("Follow these steps to set up Stable Diffusion:\n")

    print("1. Clone Automatic1111 WebUI:")
    print("   git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git sd-webui")
    print("   cd sd-webui\n")

    print("2. Download Stable Diffusion XL model:")
    print("   Download from: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0")
    print("   Place in: sd-webui/models/Stable-diffusion/\n")

    print("3. (Optional) Download NSFW-capable LoRAs from Civitai:")
    print("   https://civitai.com")
    print("   Place in: sd-webui/models/Lora/\n")

    print("4. Launch WebUI with API enabled:")
    print("   Edit webui-user.bat and add: --api --xformers")
    print("   Then run: webui-user.bat\n")

    print("5. Verify WebUI is running at: http://127.0.0.1:7860")

def main():
    """Main setup function"""
    print("="*50)
    print("AI Companion System - Model Downloader")
    print("="*50)

    recommended_models = [
        "dolphin-mistral:7b-v2.8",
        "dolphin2.9-mistral-nemo:12b",
    ]

    print("\nRecommended LLM models for RTX 4060:")
    for i, model in enumerate(recommended_models, 1):
        print(f"  {i}. {model}")

    print("\nSelect model to download:")
    print("1. Dolphin Mistral 7B (Recommended, faster)")
    print("2. Dolphin Mistral Nemo 12B (Better quality, slower)")
    print("3. Both")
    print("4. Skip LLM download")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        download_llm_model(recommended_models[0])
        test_llm_model(recommended_models[0])
    elif choice == "2":
        download_llm_model(recommended_models[1])
        test_llm_model(recommended_models[1])
    elif choice == "3":
        for model in recommended_models:
            download_llm_model(model)
    elif choice == "4":
        print("Skipping LLM download...")
    else:
        print("Invalid choice")
        return

    setup_stable_diffusion()

    print("\n" + "="*50)
    print("Setup Complete!")
    print("="*50)
    print("\nNext steps:")
    print("1. Configure models in backend/config.py")
    print("2. Start Ollama service")
    print("3. Start Stable Diffusion WebUI with --api flag")
    print("4. Run the backend server")
    print("5. Run the frontend")

if __name__ == "__main__":
    main()
