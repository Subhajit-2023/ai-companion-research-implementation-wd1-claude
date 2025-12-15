"""
Initialize sample Visual Novel stories
Creates demo stories similar to famous visual novels
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from database.db import init_db, async_session_maker
from api.models_vn import VisualNovel, VNScene


async def create_sample_story_mystery():
    """Create a mystery/thriller visual novel similar to Steins;Gate"""
    async with async_session_maker() as session:
        # Create the visual novel
        novel = VisualNovel(
            title="Echoes of Time",
            description="A thrilling mystery about time loops and difficult choices. You discover the ability to send messages to the past. Can you prevent a tragedy while keeping your sanity intact?",
            author="AI Companion System",
            genre="Mystery, Sci-Fi, Thriller",
            total_scenes=10,
            estimated_playtime=30,
            metadata={
                "tags": ["time travel", "mystery", "choices matter", "multiple endings"],
                "content_warning": "Contains themes of death and psychological tension",
            },
        )
        session.add(novel)
        await session.flush()

        # Scene 1: Opening
        scene1 = VNScene(
            visual_novel_id=novel.id,
            scene_number=1,
            chapter="Prologue",
            title="The Lab",
            narrative_text="You wake up in a dimly lit laboratory. The hum of machines fills the air. Your head throbs with a splitting headache.",
            character_dialogue="What... happened? I was just... Where am I?",
            character_name="You",
            background_image_prompt="dark laboratory with glowing monitors, sci-fi setting, mysterious atmosphere, anime style",
            scene_type="narrative",
        )
        session.add(scene1)
        await session.flush()

        # Scene 2: Discovery
        scene2 = VNScene(
            visual_novel_id=novel.id,
            scene_number=2,
            chapter="Prologue",
            title="Strange Device",
            narrative_text="On the desk, you notice a peculiar device. It looks like a modified microwave with electronic components attached. There's a note next to it.",
            character_dialogue="'Temporal Message Device - DO NOT USE' ...What is this supposed to mean?",
            character_name="You",
            background_image_prompt="close-up of mysterious electronic device, microwave with modifications, glowing display, anime style",
            scene_type="narrative",
        )
        scene2.next_scene_id = scene1.id + 2  # Will be scene 3
        session.add(scene2)
        await session.flush()

        # Update scene1 next_scene_id
        scene1.next_scene_id = scene2.id

        # Scene 3: The Call
        scene3 = VNScene(
            visual_novel_id=novel.id,
            scene_number=3,
            chapter="Chapter 1",
            title="The Phone Call",
            narrative_text="Your phone rings. It's your friend Yuki. Her voice sounds panicked.",
            character_dialogue="You need to come to the rooftop! Something terrible is about to happen! Hurry!",
            character_name="Yuki",
            background_image_prompt="worried anime girl with long dark hair, frightened expression, holding phone, detailed anime art",
            scene_type="choice",
            choices=[
                {
                    "text": "Rush to the rooftop immediately",
                    "next_scene_id": None,  # Will be set to scene 4a
                    "flags": {"rushed": True},
                },
                {
                    "text": "Ask what's happening first",
                    "next_scene_id": None,  # Will be set to scene 4b
                    "flags": {"careful": True},
                },
            ],
        )
        session.add(scene3)
        await session.flush()

        # Update scene2
        scene2.next_scene_id = scene3.id

        # Scene 4a: Rush Ending (Bad)
        scene4a = VNScene(
            visual_novel_id=novel.id,
            scene_number=4,
            chapter="Chapter 1",
            title="Too Late",
            narrative_text="You run as fast as you can, but when you arrive at the rooftop, you're too late. Yuki is standing at the edge, tears streaming down her face.",
            character_dialogue="I'm sorry... I couldn't wait any longer...",
            character_name="Yuki",
            background_image_prompt="rooftop at sunset, dramatic lighting, anime girl at edge, melancholic atmosphere",
            scene_type="narrative",
            is_ending=True,
            metadata={"ending_name": "Too Late - Bad Ending"},
        )
        session.add(scene4a)

        # Scene 4b: Careful Approach
        scene4b = VNScene(
            visual_novel_id=novel.id,
            scene_number=5,
            chapter="Chapter 1",
            title="Understanding",
            narrative_text="You ask Yuki to explain. She tells you about strange messages she's been receiving from someone claiming to be from the future.",
            character_dialogue="They keep warning me about today. They say something terrible will happen if I go to the rooftop alone.",
            character_name="Yuki",
            background_image_prompt="anime girl with concerned expression, holding phone, indoor setting, warm lighting",
            scene_type="narrative",
        )
        session.add(scene4b)
        await session.flush()

        # Scene 5: Realization
        scene5 = VNScene(
            visual_novel_id=novel.id,
            scene_number=6,
            chapter="Chapter 2",
            title="The Time Loop",
            narrative_text="Suddenly, everything clicks. The device in the lab... the messages... You've been living the same day over and over, trying to save Yuki.",
            character_dialogue="I remember now! I've done this before! The device can send messages to the past!",
            character_name="You",
            background_image_prompt="character having revelation, memories flooding back, ethereal effect, dramatic anime style",
            scene_type="choice",
            choices=[
                {
                    "text": "Use the device to prevent the tragedy",
                    "next_scene_id": None,  # Will be scene 6a
                    "flags": {"used_device": True},
                },
                {
                    "text": "Try to convince Yuki directly",
                    "next_scene_id": None,  # Will be scene 6b
                    "flags": {"direct_approach": True},
                },
            ],
        )
        session.add(scene5)
        await session.flush()

        scene4b.next_scene_id = scene5.id

        # Scene 6a: Device Ending (True Ending)
        scene6a = VNScene(
            visual_novel_id=novel.id,
            scene_number=7,
            chapter="Chapter 2",
            title="Breaking the Loop",
            narrative_text="You rush back to the lab and use the device to send a message to yourself in the past. The message contains everything you've learned. The timeline shifts, and suddenly, you're back at the beginning... but this time, armed with knowledge.",
            character_dialogue="This time... this time I'll save everyone!",
            character_name="You",
            background_image_prompt="character using time device, glowing effects, determination in eyes, heroic pose, anime style",
            is_ending=True,
            scene_type="narrative",
            metadata={"ending_name": "True Ending - Timeline Restored"},
        )
        session.add(scene6a)

        # Scene 6b: Direct Ending (Good Ending)
        scene6b = VNScene(
            visual_novel_id=novel.id,
            scene_number=8,
            chapter="Chapter 2",
            title="Trust",
            narrative_text="You tell Yuki everything - about the loops, the device, all of it. At first, she doesn't believe you, but the details you know convince her. Together, you find another way.",
            character_dialogue="Thank you... for never giving up on me.",
            character_name="Yuki",
            background_image_prompt="two friends embracing, sunset background, emotional moment, beautiful anime art",
            is_ending=True,
            scene_type="narrative",
            metadata={"ending_name": "Good Ending - Power of Trust"},
        )
        session.add(scene6b)

        # Update choice scene next_scene_ids
        scene3.choices[0]["next_scene_id"] = scene4a.id
        scene3.choices[1]["next_scene_id"] = scene4b.id
        scene5.choices[0]["next_scene_id"] = scene6a.id
        scene5.choices[1]["next_scene_id"] = scene6b.id

        await session.commit()

        print(f"✓ Created sample visual novel: {novel.title}")
        print(f"  - {novel.total_scenes} scenes")
        print(f"  - Multiple endings")
        print(f"  - Genre: {novel.genre}")


async def main():
    """Initialize sample stories"""
    print("="*50)
    print("Visual Novel Story Initialization")
    print("="*50)
    print()

    await init_db()

    print("\nCreating sample stories...")
    await create_sample_story_mystery()

    print()
    print("="*50)
    print("Sample stories created successfully!")
    print("="*50)
    print()
    print("You can now play these visual novels through the frontend.")


if __name__ == "__main__":
    asyncio.run(main())
