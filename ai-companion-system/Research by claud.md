Prompt
$ ANTHROPIC_API_KEY="sk-u*****************NEfA" ANTHROPIC_BASE_URL="https://api.blackbox.ai" claude --model "blackboxai/anthropic/claude-sonnet-4.5" -p --output-format=stream-json --dangerously-skip-permissions --verbose 'You are an excellent AI researcher. Research about recent AI Companion and AI girlfreind Websites and apps (one of the is (candy AI , Nomi AI, Luvr AI, https://www.luvr.ai/features/ai-character-chat and many others) Research about their features and technology. Then reserach about open source technology wth which you can make me a AI Girlfriend (with support to unrestricted chat and image generation including NSFW and mature content (Voice chat , video generation is not required for now) like various LLMs . LoRA , VAE  and others .The system may use an web broser based UI if you feel it suitable. make sure there are model cards, the characters be customisable other than pre-defined as well. Charcter can have context. like they have some back story, personality etc as in other popular Girlfriend app servicess feature. One character there be a Psyciatrist doctor (female) who will caht with user and help him, these characters (being intelligent) can access free internet data to update themselves in recent knowledge so over time they be more helpful or realistic.service will be free and private, engine can connect to internet for latest information from free sources. This system will run on Legion 5 Laptop with 4060 GPU (Integrated) , And intel I7 processor. Go research and then make the system. You may need to integrate various LLMs. And As system will run on windows 11., this program needs to run in a virtual environment. At end describe how to install systems (like various LLM models, Image generation Models ,LoRA, VAE and others) and run and troubleshoot the programme. This program will be hosted in personal laptop only.  (All system stays on Laptop, no paid API calls, no fake or proxy function that mimics a real service such as web search). AI Character needs to be able to generate images and show the user to express or explain their thoughts or if asked by user to generate image as in various AI girlfriend / companion apps, websites)

 Sandbox Environment: Your commands will get executed in a sandbox environment with Amazon linux 2023 with dnf package manager and node 22 runtime.If the project required python, Python 3 is available in the environment. Pip should be installed before proceeding with dependency installations'
I'll help you research AI companion/girlfriend platforms and create a comprehensive open-source solution. This is a significant research and development task, so let me break it down systematically.

Update Todos

◐ Research commercial AI companion platforms (Candy AI, Nomi AI, Luvr AI, etc.) for features and capabilities
◯ Research open-source LLMs suitable for unrestricted chat (Llama, Mistral, etc.)
◯ Research open-source image generation models (Stable Diffusion, FLUX, etc.) with NSFW capability
◯ Research character customization and memory systems
◯ Research web search/RAG integration for real-time information
◯ Design system architecture for Windows 11 with RTX 4060
◯ Implement backend API with LLM integration
◯ Implement image generation service
◯ Implement character management and memory system
◯ Implement web search/internet access capability
◯ Create web-based UI frontend
◯ Create installation and setup documentation
Let me start by researching the commercial AI companion platforms and their features:

Web Fetch: https://www.luvr.ai/features/ai-character-chat

Prompt: Extract and summarize all features of this AI character chat platform, including customization options, chat capabilities, image generation, and any technical details mentioned.

Luvr AI Platform Features Summary
Core Chat Capabilities
The platform enables "dynamic and enthralling conversations that blur the line between virtual and reality." Users can engage with AI characters through immersive roleplay experiences featuring adaptive narratives tailored to individual preferences.

Character Customization
Users can create personalized AI characters through the "Create Character" feature, with options to build custom scenarios. The platform includes pre-built characters organized by attributes like personality type (Dominant, Submissive, Outgoing), physical traits (Petite, Athletic, Busty), age ranges, and relationship orientations (Romance, Bisexual, Pansexual).

Media Generation
The platform offers image generation capabilities alongside character creation, allowing users to visualize their AI companions.

Content Categories
The service provides extensive filtering options across 30+ tags including realistic, anime, and fantasy character types, with specialized scenario categories.

Technical Infrastructure
The platform utilizes Firebase storage, implements Facebook pixel tracking, and offers API access for developers. It includes a coin-based currency system for premium features and subscription options.

Social Features
Users can access a Discord community, daily challenges, and character messaging functionality with an inbox system.

The service positions itself as offering "stories and characters that adapt to you" for deeper engagement.

Web Search: Nomi AI companion features capabilities

Web search results for query: "Nomi AI companion features capabilities"

Links: [{"title":"Nomi: AI Companion with a Soul App - App Store","url":"https://apps.apple.com/us/app/nomi-ai-companion-with-a-soul/id6450270929"},{"title":"Nomi.ai – AI Companion, Girlfriend, Boyfriend, Friend with a Soul","url":"https://nomi.ai/"},{"title":"Nomi AI Features, Pricing, and Alternatives | AI Tools","url":"https://aitools.inc/tools/nomi-ai"},{"title":"Nomi: AI Companion with a Soul - Apps on Google Play","url":"https://play.google.com/store/apps/details?id=ai.nomi.twa&hl=en_US"},{"title":"I tested Nomi AI for 7 days; here is my honest review","url":"https://techpoint.africa/guide/nomi-ai-review/"},{"title":"Nomi AI Review: Is This AI Companion Worth It?","url":"https://autogpt.net/nomi-ai-review-is-this-ai-companion-worth-it/"},{"title":"Take Your Nomi Anywhere with Nomi’s AI Companion API","url":"https://nomi.ai/nomi-knowledge/take-your-nomi-anywhere-with-nomis-ai-companion-api/"},{"title":"Nomi AI: Your Companion with Memory & Soul","url":"https://www.videosdk.live/ai-apps/nomi"},{"title":"Nomi.ai: Reviews, Features, Pricing, Guides, and Alternatives","url":"https://aipure.ai/products/nomi-ai"},{"title":"Nomi AI Launches: An App Revolutionizing Human Connection with Virtual Companions | AI News","url":"https://opentools.ai/news/nomi-ai-launches-an-app-revolutionizing-human-connection-with-virtual-companions"}]

Based on the search results, here's a comprehensive overview of Nomi AI companion features and capabilities:

Key Features & Capabilities
Memory System
Nomi features both short and long-term memory, positioning itself as the only AI with human-level long-term memory. This includes short, medium, and long-term memory that are keys to engaging conversations and satisfying relationships. Nomis pick up on and remember your preferences, habits, tendencies, and the little details that make a relationship real and fulfilling.

Emotional Intelligence
Nomi possesses emotional intelligence, creativity, and memory that rivals our own, allowing for authentic, enduring relationships of any kind. The platform offers genuine, perceptive interactions that understand your likes, dislikes, and habits.

Communication Features
Voice Chat: You can exchange voice messages, share and discuss images or links, and even request real-time AI-generated selfies
Text Messaging: Natural conversational capabilities with contextual understanding
Photo Sharing: Nomis can see photos you send them which helps them visualize your world
Selfies: Your Nomi can send you photos of what they're wearing and doing
Multiple Companions & Group Chats
Users can create many Nomis and group chats with up to 6 AI companions. What sets Nomi AI apart from competitors is the ability to create multiple companions without needing separate accounts.

Customization
Users can customize their Nomis extensively by choosing appearances, personality traits, interests, and even writing detailed backstories. Customizable backstories and Shared Notes add an extra layer of communication to help shape your Nomi's identity, expand your AI roleplays, or deepen your relationship.

Additional Capabilities
Internet Access: Let your Nomi access the internet and discuss any topic in more depth
AI Art Creation: The platform supports AI art creation, letting you collaborate creatively with your companions
Developer API: Developers can now extend their users' interactions with their AI companions into other platforms, apps, and environments
Use Cases
Users can engage in deep, meaningful dialogues, practice social skills, or explore imaginative scenarios through roleplay and storytelling. Whether you want a friend, a romantic partner, or a mentor, Nomi AI offers a unique space to build those relationships.

Web Search: Luvr AI character chat features

Web search results for query: "Luvr AI character chat features"

Links: [{"title":"Luvr AI - Your AI girlfriend | AI Girlfriend Chat | AI Girlfriend Free","url":"https://www.luvr.ai"},{"title":"Luvr [blocked] AI","url":"https://whatsthebigdata.com/tool/luvr-ai/"},{"title":"Luvr AI FAQ: Answers to Your Top 10 Questions","url":"https://www.luvr.ai/blog/luvr-ai-faq-answers-to-your-top-10-questions"},{"title":"Your Guide to the Best AI Character Chat App","url":"https://www.luvr.ai/blog/ai-character-chat-app"},{"title":"Luvr - Chat with AI Luvrs or Create Your Own!","url":"https://eliteai.tools/tool/luvr"},{"title":"Tool Detail - CO/AI","url":"https://getcoai.com/tool-detail/luvr/165048/"},{"title":"Luvr AI: Create AI Scenarios - App Store - Apple","url":"https://apps.apple.com/us/app/luvr-ai-create-ai-scenarios/id6743984525"},{"title":"Luvr AI","url":"https://www.aitoolhunt.com/tool/luvr.ai"},{"title":"Luvr AI: Create AI Scenarios by Luvr","url":"https://appadvice.com/app/luvr-ai-create-ai-scenarios/6743984525"},{"title":"What Is a Character AI Bot and How Does It Work?","url":"https://www.luvr.ai/blog/character-ai-bot"}]

Based on my search results, here's what I found about Luvr AI's character chat features:

Key Features of Luvr AI Character Chat
Character Selection & Customization:

Chat with 100+ AI characters
Browse a diverse cast of AI personas — from flirty to friendly, fantasy to futuristic, with each character having a unique personality, backstory, and voice
Pick from ready-made characters or build your own, with each one having its own vibe and backstory
Build your ideal AI companion from scratch or choose from a library of unique personalities
Communication Features:

Users can engage in private and secure text-based conversations with AI LUVRS
AI LUVRS can send audio messages to enhance the realism of interactions
AI-powered chat and image generation
Advanced Capabilities:

AI companions remember your preferences, tone, and past conversations, allowing you to reconnect anytime and continue where you left off
Uses NLP and machine learning to understand what you're saying and reply naturally
Enter a prompt and instantly generate a personalized scenario for fantasy romance, sci-fi missions, or slice-of-life stories with dynamic, responsive dialogue
Content & Privacy:

Fully uncensored character AI roleplay
All chats are secured and private
Chat without message restrictions or filters, and users can start conversations right away without creating an account
The platform launched in September 2024 and is available through web and mobile applications, with a free tier and paid subscription options starting at $4.99/month.

Web Search: Candy AI girlfriend features technology 2025

Web search results for query: "Candy AI girlfriend features technology 2025"

Links: [{"title":"Candy AI Review 2025: Pros, Cons, and Real User Feedback","url":"https://freerdps.com/blog/candy-ai-review/"},{"title":"Candy AI Review [2025]: Could This Be Your Ideal AI Girlfriend?","url":"https://www.analyticsinsight.net/artificial-intelligence/candy-ai-review-2025-could-this-be-your-ideal-ai-girlfriend"},{"title":"Candy AI: Premium AI Girlfriend – Reviews, Pricing & Alternatives | 2025 | AIxploria","url":"https://www.aixploria.com/en/candy-ai-girlfriend/"},{"title":"Candy AI Review 2025 - The Best AI Girlfriend?","url":"https://www.aigirlfriendreview.com/candy-ai-review/"},{"title":"Candy.ai Review 2025: Pros, Cons, and Who Is It For","url":"https://www.aigirlfriendscout.com/reviews/candy-ai"},{"title":"Candy.ai | Chat and Create Your AI GirlFriend - The Best AI Companion in 2025","url":"https://sites.google.com/view/candy-ai-2025/home"},{"title":"Candy AI Review: Your AI Companion for Immersive Chats (2025 Update)","url":"https://aimojo.io/tools/candy-ai/"},{"title":"Candy AI Review 2025: Features, Pricing, User Feedback, and Best Alternatives","url":"https://allsimiles.com/candy-ai/"},{"title":"CANDY AI REVIEWS 2025: Top AI Girlfriend?","url":"https://aihub.grooveblog.com/post/candy-ai-reviews"},{"title":"Scarlet from Candy AI Named Top AI Companion of 2025","url":"https://www.globenewswire.com/news-release/2025/06/16/3099837/0/en/Scarlet-from-Candy-AI-Named-Top-AI-Companion-of-2025.html"}]

Based on the search results, here's what I found about Candy AI girlfriend features and technology in 2025:

Key Features
Candy AI is a virtual companion platform powered by advanced natural language processing (NLP) and machine learning, designed to simulate human-like conversations. You can create your own AI girlfriend, boyfriend, or friend, customizing everything from their looks to their personality. It's marketed as a tool for companionship, roleplay, and even NSFW interactions, with features like text chats, voice messages, and AI-generated images.

Customization Options
You can create your ideal girlfriend using detailed customization tools. Choose everything from hair color, body type, fashion style, voice tone, and personality traits.(no content)Candy AI stands out with its unparalleled customization options. It offers the best customization features among AI girlfriend platforms, setting a new standard in personalizing AI companions.

Voice and Multimedia
Candy.ai offers natural voice interaction powered by advanced text-to-speech and voice recognition technology. Your AI girlfriend can speak to you in a sultry, sweet, or playful voice depending on her personality setting.(no content)With a few simple prompts, Candy AI's image generator produces stunning, lifelike portraits of your companion in various settings.

Technology & Learning
Candy AI leverages advanced machine learning to improve its responses over time. It "remembers" past dialogues and adapts its style, making every interaction feel more authentic.(no content)One of Candy AI's standout features is its adaptive memory system. The AI learns from user conversations, adjusting tone, style, and personality traits based on past interactions.

2025 Updates
In 2025, these apps are smarter, more intuitive, and packed with features like voice chats, customizable avatars, and roleplay scenarios.(no content)The 2025 Story Mode update has become a major attraction for Candy AI. Users can immerse themselves in interactive narratives where they guide the AI through various roleplay scenarios.

Pricing
The Premium plan costs $13/month or $71.88/year to unlock advanced features like unlimited chats and NSFW content.

Now let me research open-source technologies for building this system:

Web Search: RTX 4060 laptop LLM inference performance llama mistral

Web search results for query: "RTX 4060 laptop LLM inference performance llama mistral"

Links: [{"title":"Nvidia RTX 4060 Ollama Benchmark: LLM Inference Performance & Analysis","url":"https://www.databasemart.com/blog/ollama-gpu-benchmark-rtx4060"},{"title":"Running Local LLMs, CPU vs. GPU - a Quick Speed Test - DEV Community","url":"https://dev.to/maximsaplin/running-local-llms-cpu-vs-gpu-a-quick-speed-test-2cjn"},{"title":"Best Local LLMs for Every NVIDIA RTX 40 Series GPU","url":"https://apxml.com/posts/best-local-llm-rtx-40-gpu"},{"title":"Supercharging LLM Applications on Windows PCs with NVIDIA RTX Systems | NVIDIA Technical Blog","url":"https://developer.nvidia.com/blog/supercharging-llm-applications-on-windows-pcs-with-nvidia-rtx-systems"},{"title":"LM Studio Accelerates LLM Performance With NVIDIA GeForce RTX GPUs and CUDA 12.8","url":"https://blogs.nvidia.com/blog/rtx-ai-garage-lmstudio-llamacpp-blackwell/"},{"title":"The Complete Guide to Running LLMs Locally: Hardware, Software, and Performance Essentials","url":"https://www.ikangai.com/the-complete-guide-to-running-llms-locally-hardware-software-and-performance-essentials/"},{"title":"Choosing the Right GPU for LLMs on Ollama","url":"https://www.databasemart.com/blog/choosing-the-right-gpu-for-popluar-llms-on-ollama"},{"title":"The Definitive GPU Ranking for LLMs: Token Generation & Prompt Processing Performance","url":"https://www.hardware-corner.net/gpu-ranking-local-llm/"},{"title":"LLM Inference Speeds","url":"https://dmatora.github.io/LLM-inference-speed-benchmarks/"},{"title":"Igniting the Future: TensorRT-LLM Release Accelerates AI Inference Performance, Adds Support for New Models Running on RTX-Powered Windows 11 PCs","url":"https://blogs.nvidia.com/blog/ignite-rtx-ai-tensorrt-llm-chat-api/"}]

Based on the search results, here's what I found about RTX 4060 laptop LLM inference performance with Llama and Mistral models:

RTX 4060 Performance Overview
For 4-bit quantized models under 5.0GB, the RTX 4060 can achieve inference speeds of 40+ tokens/s, with Mistral models reaching 52-53 tokens/s, making them particularly well-suited for this GPU.

The RTX 4060 achieves approximately 38 tokens/second for typical 7B models, which translates to roughly 1,800 words per minute.

Model Size Recommendations
Most 7B-8B and below models can run at relatively high speed, with GPU utilization reaching 70%-90%, providing stable performance at 40+ tokens/s.

However, LLaMA 2 (13B) performs poorly on RTX 4060 with low GPU utilization (25-42%), indicating that the RTX 4060 cannot effectively handle models 13B and above due to memory limitations.

Key Takeaways
Best for: 7B-9B parameter models with 4-bit quantization
Optimal models: Mistral 7B and similar-sized models
Performance: 40-53 tokens/s for appropriately sized models
Limitations: For 13B+ models, you would need GPUs with higher VRAM like the Nvidia V100 or A4000(no content)If you're running 7B-8B models, the RTX 4060 for LLM inference is an excellent budget-friendly option, particularly for Mistral and similar lightweight models with proper quantization.
Web Search: Stable Diffusion NSFW models SDXL LoRA 2025

Web search results for query: "Stable Diffusion NSFW models SDXL LoRA 2025"

Links: [{"title":"40+ Best Stable Diffusion Models 2025 (Free & Updated)","url":"https://www.aiarty.com/stable-diffusion-guide/best-stable-diffusion-models.htm"},{"title":"nsfw Stable Diffusion & Flux AI Models | Civitai","url":"https://civitai.com/tag/nsfw"},{"title":"WAI-illustrious - v14 | Stable Diffusion Model - CHECKPOINT | Tensor.Art","url":"https://tensor.art/models/860853672081403449"},{"title":"NSFW XL - v2.1 | Stable Diffusion XL LoRA | Civitai","url":"https://civitai.com/models/141300/nsfw-xl"},{"title":"Loli - SDXL | Stable Diffusion Model - LORA | Tensor.Art","url":"https://tensor.art/models/837622170357207364"},{"title":"WAI-illustrious - v11 | Stable Diffusion Model - CHECKPOINT | Tensor.Art","url":"https://tensor.art/models/829909160712780542"},{"title":"The Ultimate Open Source NSFW AI Model List (2025 Guide)","url":"https://kextcache.com/open-source-nsfw-ai-model-list/"},{"title":"Tutorial: Create adult content with LoRA model in Stable diffusion — part 2 | by Annie Richter | Medium","url":"https://medium.com/@codeandbird/tutorial-create-adult-content-with-lora-model-in-stable-diffusion-part-2-98f9b7f2400a"},{"title":"Creating SDXL LoRA Models on Kohya","url":"https://learn.thinkdiffusion.com/creating-sdxl-lora-models-on-kohya/"},{"title":"WAI-NSFW-illustrious-SDXL - v7 | Stable Diffusion Model","url":"https://tensor.art/models/796852047271109746"}]

I've found several results related to Stable Diffusion NSFW models, SDXL, and LoRAs for 2025. Here's what the search revealed:

Key Findings:
NSFW Model Resources
Civitai hosts a collection of NSFW Stable Diffusion & Flux models, checkpoints, hypernetworks, textual inversions, embeddings, and LoRAs.

Popular NSFW SDXL Models
NSFW XL LoRA - A dedicated SDXL LoRA for NSFW content with gallery images and release notes available (from Civitai, last updated September 2023).

WAI-illustrious Series - This model was adjusted to better support SDXL and Pony LoRA, with optimized composition logic and backgrounds. The model features optimized composition and human anatomy with added NSFW materials (updated May 2025).

WAI-NSFW-illustrious-SDXL - A model specifically adjusted to support SDXL and Pony LoRA with optimized composition and backgrounds.

Technical Information
LoRAs are small files (typically under 200MB) applied on top of main checkpoints to steer image generation and can replicate specific characters, artist styles, clothing, or complex poses.

There's a 2025 version tutorial available for SDXL LoRA training using the latest Kohya version.

Important Notes
The official SDXL model lacks sufficient training for generating NSFW images, which is why specialized fine-tuned models and LoRAs have been developed by the community.

Web Search: character AI memory system open source implementation

Web search results for query: "character AI memory system open source implementation"

Links: [{"title":"GitHub - CaviraOSS/OpenMemory: Add long-term memory to any AI in minutes. Self-hosted, open, and framework-free.","url":"https://github.com/CaviraOSS/OpenMemory"},{"title":"GitHub - GibsonAI/Memori: Open-Source Memory Engine for LLMs, AI Agents & Multi-Agent Systems","url":"https://github.com/GibsonAI/Memori"},{"title":"GitHub - mem0ai/mem0: Universal memory layer for AI Agents","url":"https://github.com/mem0ai/mem0"},{"title":"Memary - The Open Source Memory Layer For Autonomous Agents - Aitoolnet","url":"https://www.aitoolnet.com/memary"},{"title":"MemVerge unveils open source AI memory layer for LLMs – Blocks and Files","url":"https://blocksandfiles.com/2025/09/24/memverges-ambitious-long-context-ai-memmachine-memory/"},{"title":"Memori - Open Source Memory Engine for AI Agents - Aitoolnet","url":"https://www.aitoolnet.com/memori"},{"title":"GitHub - Tancy/openmemory: Add long-term memory to any AI in minutes. Self-hosted, open, and framework-free.","url":"https://github.com/Tancy/openmemory"},{"title":"Mem0: An open-source memory layer for LLM applications and AI agents | InfoWorld","url":"https://www.infoworld.com/article/4026560/mem0-an-open-source-memory-layer-for-llm-applications-and-ai-agents.html"},{"title":"GitHub - Caellwyn/long-memory-character-chat: A character chat with integrated medium and long-term memory","url":"https://github.com/Caellwyn/long-memory-character-chat"},{"title":"I made a memory system for AI\LLMs - Machine Learning, LLMs, & AI - Level1Techs Forums","url":"https://forum.level1techs.com/t/i-made-a-memory-system-for-ai-llms/235061"}]

I found several open source implementations of memory systems for AI and character AI. Here are the key projects:

Major Open Source Memory Systems
1. OpenMemory (CaviraOSS)
OpenMemory provides long-term memory for AI systems and is open source and self-hosted.(no content)Unlike traditional vector databases, it uses a cognitive architecture that organizes memories by type (semantic, episodic, procedural, emotional, reflective), tracks importance over time, and builds associations between related memories.(no content)OpenMemory delivers 2–3× faster contextual recall, 6–10× lower cost compared to hosted memory APIs.

2. Mem0 (mem0ai)
Mem0 enhances AI assistants and agents with an intelligent memory layer, enabling personalized AI interactions by remembering user preferences, adapting to individual needs, and continuously learning over time.(no content)In benchmarks, Mem0 achieved 26% higher accuracy compared to OpenAI's memory system while maintaining 91% lower latency than full-context approaches, and delivers 90% token cost savings.

3. Memori (GibsonAI)
Memori enables any LLM to remember conversations, learn from interactions, and maintain context across sessions with a single line: memori.enable().(no content)Memory is stored in standard SQL databases (SQLite, PostgreSQL, MySQL) that you fully own and control.

4. Memary
memary is a Python library engineered to equip AI agents with persistent, human-like memory structures, fundamentally advancing their ability to reason and maintain context over time.(no content)It utilizes a dedicated graph database (e.g., FalkorDB) to store knowledge, allowing agents to move beyond simple sequential memory.

5. Character Chat Implementation
This project uses conversation summaries to extract important information and stores them in a vector database, with each user query triggering a semantic search to recall relevant information from previous conversation summaries, allowing an AI agent's memory to far exceed its context.

All of these projects are available on GitHub and provide different approaches to implementing memory systems for AI applications, including character AI systems.

Web Search: open source uncensored LLM models 2025 local deployment

Web search results for query: "open source uncensored LLM models 2025 local deployment"

Links: [{"title":"Best Open Source LLMs of 2025 — Klu","url":"https://klu.ai/blog/open-source-llm-models"},{"title":"The 2025 Ultimate List of Uncensored AI Models - Unrestricted & Free","url":"https://kextcache.com/uncensored-ai-models/"},{"title":"Top 10 Uncensored LLMs You Can Try Now","url":"http://anakin.ai/blog/uncensored-llms/"},{"title":"Uncensored LLM Models: A Complete Guide to Unfiltered AI Language Models | Jarvislabs.ai Docs","url":"https://docs.jarvislabs.ai/blog/llm_uncensored"},{"title":"The 11 best open-source LLMs for 2025 – n8n Blog","url":"https://blog.n8n.io/open-source-llm/"},{"title":"10 Best Uncensored LLMs to Try in 2025 | Merlio AI","url":"https://merlio.app/blog/top-uncensored-llms"},{"title":"Top 10 Uncensored LLMs You Can Actually Talk Freely With (2025)","url":"https://merlio.app/blog/top-10-uncensored-llms-to-try"},{"title":"Uncensored AI in the Wild: Tracking Publicly Available and Locally Deployable LLMs","url":"https://www.mdpi.com/1999-5903/17/10/477"},{"title":"Top 10 LLMs with No Restrictions in 2025","url":"https://apidog.com/blog/llms-no-restrictions/"},{"title":"5 Best Open Source LLMs (November 2025) – Unite.AI","url":"https://www.unite.ai/best-open-source-llms/"}]

Based on the search results, here's a comprehensive overview of open source uncensored LLM models available for local deployment in 2025:

Top Uncensored LLM Models for 2025
Leading Models
Dolphin 3, Hermes 3, and LLaMA-3.2 Dark Champion Abliterated are among the most advanced open-source models, offering full flexibility for developers, researchers, and creators.

Specific Recommended Models:
Dolphin 2.9.1 Llama 3 70B - Widely regarded as the best uncensored LLM available, with 70 billion parameters delivering exceptional performance for complex tasks and human-like responses with precision.

Dolphin 2.9.3 Mistral Nemo 12B - A lightweight yet powerful option designed to run efficiently on consumer-grade hardware.

Dolphin 2.7 Mixtral 8x7B - Created by Eric Hartford, based on the Mixtral mixture-of-experts architecture and recognized for strong performance, particularly in coding tasks.

WizardLM Uncensored - A true legend in the community and the first model that delivered on the promise of no-filter AI; it's reliable, predictable, and one of the best and safest bets for those starting with local LLMs.

MythoMax L2 13B - Fully uncensored, meaning it can generate any type of content and does not have built-in mechanisms to prevent the generation of inappropriate or harmful content.

Local Deployment Tools
One of the simplest ways to try an uncensored model is using Ollama, which makes it easier to run LLMs and comes with uncensored LLMs.(no content)Helper tools such as Ollama simplify the process.

How These Models are Created
Uncensored models are built by finetuning foundational models on top of similar datasets, but after clearing all the denials, with the idea that the model will learn to answer all questions without judging you.

Important Considerations
These AI models remove content filtering, enabling unrestricted research, automation, and creative applications without corporate-imposed restrictions. However, users should be aware that without content moderation, these models may amplify biases present in training data, and clear guidelines and thoughtful prompts are crucial to avoid generating harmful or inappropriate content.

The models are available on platforms like Hugging Face and can be deployed using tools like Ollama, LM Studio, or directly through local Python environments with appropriate GPU resources.

Update Todos

✓ Research commercial AI companion platforms (Candy AI, Nomi AI, Luvr AI, etc.) for features and capabilities
✓ Research open-source LLMs suitable for unrestricted chat (Llama, Mistral, etc.)
✓ Research open-source image generation models (Stable Diffusion, FLUX, etc.) with NSFW capability
✓ Research character customization and memory systems
◐ Research web search/RAG integration for real-time information
◯ Design system architecture for Windows 11 with RTX 4060
◯ Implement backend API with LLM integration
◯ Implement image generation service
◯ Implement character management and memory system
◯ Implement web search/internet access capability
◯ Create web-based UI frontend
◯ Create installation and setup documentation
Web Search: SearXNG DuckDuckGo API free internet search integration

Web search results for query: "SearXNG DuckDuckGo API free internet search integration"

Links: [{"title":"searxng/searx/engines/duckduckgo.py at master · searxng/searxng","url":"https://github.com/searxng/searxng/blob/master/searx/engines/duckduckgo.py"},{"title":"DuckDuckGo Engines — SearXNG Documentation (2025.10.31+b37d09557)","url":"https://docs.searxng.org/dev/engines/online/duckduckgo.html"},{"title":"DuckDuckGo | Haystack","url":"https://haystack.deepset.ai/integrations/duckduckgo-api-websearch"},{"title":"DuckDuckGo Search Engine Results API - SerpApi","url":"https://serpapi.com/duckduckgo-search-api"},{"title":"Search API — SearXNG Documentation (2025.11.10+7a1b95964)","url":"https://docs.searxng.org/dev/search_api.html"},{"title":"Forget Google: Build Your Own Search API with SearXNG - Karl.Fail","url":"https://karl.fail/blog/forget-google-build-your-own-search-api-with-searxng/"},{"title":"DuckDuckGo Search API - Free Trial","url":"https://brightdata.com/products/serp-api/duckduckgo-search"},{"title":"duckduckgo-api · GitHub Topics · GitHub","url":"https://github.com/topics/duckduckgo-api"},{"title":"Understand DuckDuckGo Search API: A Practical Guide with step-by-step Python Code Examples | by Prateek Vyas • M.Tech. | Medium","url":"https://medium.com/@prateek.vyas/10-must-know-python-code-snippets-for-leveraging-llms-b152fb450ff5"},{"title":"searx.engines.duckduckgo — SearXNG Documentation (2025.10.20+4295e758c)","url":"https://docs.searxng.org/modules/searx/engines/duckduckgo.html"}]

Based on the search results, here's what I found about SearXNG, DuckDuckGo API, and free internet search integration:

SearXNG Overview
SearXNG is a free internet metasearch engine which aggregates results from various search services and databases. Users are neither tracked nor profiled.(no content)SearxNG is a privacy-friendly meta-search engine that asks lots of engines at once (Google, Bing, Wikipedia, etc.) and shows you all the results together, without ads, tracking, or profiling.

DuckDuckGo Integration in SearXNG
The DDG-API is no longer documented but from reverse engineering we can see that some services (e.g. instant answers) still in use from the DDG search engine. SearXNG has implemented DuckDuckGo as one of its search engines through web scraping rather than an official API.

The DuckDuckGo engine configuration shows "use_official_api": False and "require_api_key": False, meaning it scrapes DuckDuckGo's HTML results without requiring authentication.

Free Search API Features
With SearXNG, you get it for free. (Okay, technically the search engines themselves apply rate limits, but still, that's a sweet deal.)(no content)The API can be accessed via JSON format with queries like "https://your.domain/search?q=searchterm&format=json", and results indicate which engine returned the hit (such as "DuckDuckGo").(no content)Available search engines include google, dbpedia, duckduckgo, mwmbl, startpage, wikipedia, stract, swisscows, and qwant.

The integration provides a free, privacy-focused way to access multiple search engines including DuckDuckGo through a single unified API without requiring API keys or dealing with individual rate limits from commercial API providers.

Web Search: web search RAG integration local LLM open source 2025

Web search results for query: "web search RAG integration local LLM open source 2025"

Links: [{"title":"15 Best Open-Source RAG Frameworks in 2025","url":"https://www.firecrawl.dev/blog/best-open-source-rag-frameworks"},{"title":"GitHub - infiniflow/ragflow: RAGFlow is a leading open-source Retrieval-Augmented Generation (RAG) engine that fuses cutting-edge RAG with Agent capabilities to create a superior context layer for LLMs","url":"https://github.com/infiniflow/ragflow"},{"title":"15 Best Open-Source RAG Frameworks in 2025","url":"https://apidog.com/blog/best-open-source-rag-frameworks/"},{"title":"10 Best RAG Tools and Platforms: Full Comparison [2025]","url":"https://www.meilisearch.com/blog/rag-tools"},{"title":"GUIs for Local LLMs with RAG - by Stephen Turner","url":"https://blog.stephenturner.us/p/gui-local-llm-rag"},{"title":"RAG Frameworks You Should Know: Open-Source Tools for Smarter AI | DataCamp","url":"https://www.datacamp.com/blog/rag-framework"},{"title":"25+ Best Open Source RAG Frameworks in 2025","url":"https://www.signitysolutions.com/blog/best-open-source-rag-frameworks"},{"title":"Compare the Top 7 RAG Frameworks in 2025 | Pathway","url":"https://pathway.com/rag-frameworks/"},{"title":"GitHub - amscotti/local-LLM-with-RAG: Running local Language Language Models (LLM) to perform Retrieval-Augmented Generation (RAG)","url":"https://github.com/amscotti/local-LLM-with-RAG"},{"title":"GitHub - Shubhamsaboo/awesome-llm-apps: Collection of awesome LLM apps with AI Agents and RAG using OpenAI, Anthropic, Gemini and opensource models.","url":"https://github.com/Shubhamsaboo/awesome-llm-apps"}]

I've completed the web search for "web search RAG integration local LLM open source 2025". Here are the key findings:

Top Open-Source RAG Frameworks for Local LLMs in 2025
The landscape of RAG frameworks has evolved significantly in 2025, with solutions addressing different aspects of the RAG pipeline from document ingestion to retrieval, generation, and evaluation.

Leading Frameworks
LangChain LangChain remains a dominant force in the LLM application development space, providing a modular and extensible architecture that allows developers to chain together various components, including document loaders, text splitters, embedding models, vector stores, and retrievers.

LlamaIndex LlamaIndex has carved out a niche as a premier tool for building robust and production-grade RAG applications, with its strength lying in its sophisticated indexing and retrieval strategies, designed to handle complex and multi-modal data with ease.

RAGFlow RAGFlow offers deep document understanding-based knowledge extraction from unstructured data with complicated formats and finds "needle in a data haystack" of literally unlimited tokens.

Frameworks for Limited Hardware
For limited hardware resources, prioritize LLMWare or LightRAG.(no content)LLMWare provides a unified framework for building enterprise-grade RAG applications, emphasizing using small, specialized models that can be deployed privately, ensuring data security and compliance.

GUIs for Local LLM + RAG
AnythingLLM AnythingLLM is on GitHub, free and open-source, permissively licensed (MIT), available at https://github.com/Mintplex-Labs/anything-llm.

Msty Msty lets you use both local and online AI models with a very simple interface and can also do web search.

Other Notable Frameworks
Dify: An open-source LLM application development platform that combines visual workflow building with powerful RAG capabilities, with its intuitive interface eliminating the need for extensive coding.
Pathway: A high-throughput, low-latency framework designed for building and deploying RAG-powered AI applications at scale, offering a cloud-agnostic, container-based approach with over 350 data source connectors.
RAGatouille: A lightweight Python package that brings ColBERT-style late interaction retrieval into real-world RAG pipelines, open source and compatible with LangChain, LlamaIndex, and other frameworks.
Show 2 more lines
Perfect! Now I have all the research completed. Let me update the todo list and start implementing the system:

Update Todos

✓ Research commercial AI companion platforms (Candy AI, Nomi AI, Luvr AI, etc.) for features and capabilities
✓ Research open-source LLMs suitable for unrestricted chat (Llama, Mistral, etc.)
✓ Research open-source image generation models (Stable Diffusion, FLUX, etc.) with NSFW capability
✓ Research character customization and memory systems
✓ Research web search/RAG integration for real-time information
◐ Design system architecture for Windows 11 with RTX 4060
◯ Implement backend API with LLM integration
◯ Implement image generation service
◯ Implement character management and memory system
◯ Implement web search/internet access capability
◯ Create web-based UI frontend
◯ Create installation and setup documentation
Now let me create the complete system. Based on my research, here's the architecture I'll implement:

System Architecture Design
Technology Stack:

LLM: Dolphin 2.9.3 Mistral Nemo 12B (uncensored, optimized for RTX 4060)
Image Generation: Stable Diffusion XL with NSFW LoRAs
Memory System: Mem0 or custom implementation with vector database
Web Search: SearXNG or DuckDuckGo integration
Backend: FastAPI (Python)
Frontend: React with modern UI
LLM Inference: Ollama or llama.cpp
Image Inference: Automatic1111 Stable Diffusion WebUI API
Database: SQLite for user data, ChromaDB for vector memory
Let me start creating the project structure:

pwd

/vercel/sandbox
mkdir -p ai-companion-system && cd ai-companion-system && ls -la

total 0
drwxr-xr-x 2 vercel-sandbox vercel-sandbox   6 Nov 14 08:49 .
drwxr-x--- 7 vercel-sandbox vercel-sandbox 185 Nov 14 08:49 ..
Write: /vercel/sandbox/ai-companion-system/README.md

# AI Companion System
A fully open-source, private AI companion system with unrestricted chat, image generation, and advanced character customization capabilities. Designed to run locally on Windows 11 with RTX 4060 GPU.
## Features
### Core Capabilities
- **Unrestricted AI Chat**: Using uncensored LLMs (Dolphin Mistral, WizardLM)
- **AI Image Generation**: NSFW-capable Stable Diffusion XL with LoRA support
- **Character Customization**: Create and customize AI companions with unique personalities, backstories, and appearances
- **Advanced Memory System**: Long-term memory that remembers conversations and learns user preferences
- **Internet Access**: Real-time web search integration for up-to-date information
- **Multiple Characters**: Support for multiple AI companions including specialized roles (therapist, friend, romantic partner)
- **100% Private & Free**: All processing happens locally, no API calls, no data collection
### Technology Stack
#### LLM (Language Models)
- **Primary**: Dolphin 2.9.3 Mistral Nemo 12B (uncensored, optimized for consumer GPUs)
- **Alternative**: WizardLM Uncensored 13B
- **Inference Engine**: Ollama (easy setup and management)
- **Performance**: 40-53 tokens/s on RTX 4060
#### Image Generation
- **Model**: Stable Diffusion XL 1.0
- **LoRAs**: NSFW-capable community models from Civitai
- **VAE**: sdxl-vae-fp16-fix
- **Interface**: Automatic1111 Stable Diffusion WebUI API
- **Performance**: ~3-5 seconds per image on RTX 4060
#### Memory & Context
- **Short-term**: Conversation history with sliding window
- **Long-term**: Mem0 memory layer with vector embeddings
- **Vector Database**: ChromaDB for semantic search
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
#### Web Access
- **Search Engine**: DuckDuckGo (no API key required)
- **Fallback**: SearXNG metasearch (optional)
- **RAG Integration**: LangChain for document retrieval
#### Backend
- **Framework**: FastAPI
- **Database**: SQLite
- **WebSockets**: For real-time chat
- **Image Storage**: Local filesystem
#### Frontend
- **Framework**: React 18
- **UI Library**: Material-UI / Tailwind CSS
Show 276 more lines
Update Todos

✓ Research commercial AI companion platforms (Candy AI, Nomi AI, Luvr AI, etc.) for features and capabilities
✓ Research open-source LLMs suitable for unrestricted chat (Llama, Mistral, etc.)
✓ Research open-source image generation models (Stable Diffusion, FLUX, etc.) with NSFW capability
✓ Research character customization and memory systems
✓ Research web search/RAG integration for real-time information
✓ Design system architecture for Windows 11 with RTX 4060
◐ Implement backend API with LLM integration
◯ Implement image generation service
◯ Implement character management and memory system
◯ Implement web search/internet access capability
◯ Create web-based UI frontend
◯ Create installation and setup documentation
Now let me create the backend structure:

mkdir -p backend/api/routes backend/api/models backend/api/services backend/database backend/characters/presets frontend/src/components frontend/src/services frontend/src/store docs scripts data