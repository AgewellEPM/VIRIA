import os
import json
import time
import logging
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from tenacity import retry, wait_exponential, stop_after_attempt, before_sleep_log, RetryError

# Load environment variables from .env file
load_dotenv()

# Setup logging
# Set to DEBUG to see full API request payloads and detailed retry info
# You can change this to logging.INFO for less verbose output once confirmed working
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Robust OpenAI Call Wrapper ---
@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10), # Wait 4s, 8s, 16s... up to 10s max
    stop=stop_after_attempt(5),                          # Retry 5 times
    before_sleep=before_sleep_log(logger, logging.DEBUG) # Log before sleeping
)
def _call_openai_api_core(model, messages, temperature, max_tokens, response_format=None):
    """Internal function for direct OpenAI API call, decorated with tenacity."""
    logger.debug("📤 Requesting OpenAI API with payload:")
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if response_format:
        payload["response_format"] = response_format # Correctly adds response_format if present
    logger.debug(json.dumps(payload, indent=2))

    return client.chat.completions.create(**payload)


def call_openai_with_retry(model, messages, temperature, max_tokens, response_format=None):
    """
    Wrapper for OpenAI API calls with retry logic, handling RetryError explicitly.
    Also includes a try-except block for immediate error context logging.
    """
    try:
        return _call_openai_api_core(model, messages, temperature, max_tokens, response_format)
    except RetryError as e:
        logger.error(f"OpenAI API call failed after multiple retries: {e}")
        raise ConnectionError("Failed to connect to OpenAI API after multiple retries.") from e
    except Exception as e:
        logger.error(f"❌ OpenAI API call failed with an unexpected error: {e}", exc_info=True)
        logger.error("Failed payload (messages content):")
        try:
            # Attempt to log a readable version of messages
            logger.error(json.dumps(messages, indent=2))
        except TypeError:
            logger.error(f"Messages content could not be serialized to JSON: {messages}")
        raise # Re-raise the exception after logging

# --- Generate Training Phrases ---
def generate_training_phrases(n=10, existing_phrases=None):
    """
    Generates emotionally diverse, real-world phrases for caregivers, friends, or parents.
    Takes a list of existing phrases to avoid repetition.
    The prompt encourages age-diverse, non-clinical, everyday questions.
    """
    if existing_phrases is None:
        existing_phrases = []

    phrases_to_exclude = existing_phrases[-100:] # Use last 100 phrases for exclusion

    past_phrases_instruction = (
        f"Do NOT repeat any of these past phrases: {json.dumps(phrases_to_exclude)}"
        if phrases_to_exclude else ""
    )
    if phrases_to_exclude:
        logging.debug(f"Instructing model to avoid {len(phrases_to_exclude)} past phrases.")

    prompt = f"""
Generate {n} real-life questions a caregiver, friend, or parent might ask a non-verbal person
(child, teen, or adult) in everyday American life.

Be realistic — not clinical. Avoid therapist-style or scripted prompts.
Include a mix of questions appropriate for different age ranges (e.g., questions for young children,
teens, and adults).

Examples of desired tone and content:
- "Wanna go to the mall?" (Social, teen/adult)
- "Do you want pizza or nuggets?" (Food, general)
- "Should we play Roblox or watch YouTube?" (Entertainment, child/teen)
- "Do you need to pee before we leave?" (Daily living, child)
- "Want to come to the store or stay home?" (Choice, general)
- "Can I go to the park with Joey?" (Social, child)
- "Did you see that dumb TikTok?" (Social, teen)
- "Do you wanna skip school today?" (Teen energy, boundary-testing)
- "Can we do Target before lunch?" (Contextual, casual, adult/teen)
- "My head really hurts, can we just chill?" (Emotional, adult/teen)
- "Are you hot or cold?" (Physical comfort, general)
- "Time for your medicine, sweetie." (Daily living, general)

Include a mix of fun, annoying, emotional, social, boring, food-related, hygiene, and messy human moments.
Real life only.

{past_phrases_instruction}

Return ONLY a JSON list of strings like this:
[
    "Want to ride bikes?",
    "Should we skip school today?",
    ...
]
"""
    logging.info(f"Generating {n} training phrases...")
    response = call_openai_with_retry(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=400,
        response_format={"type": "json_object"} # Correct for this model to request JSON
    )

    content = json.loads(response.choices[0].message.content)
    generated = []
    if isinstance(content, list):
        generated = content
    elif isinstance(content, dict):
        if 'phrases' in content and isinstance(content['phrases'], list):
            generated = content['phrases']
        elif 'list' in content and isinstance(content['list'], list):
            generated = content['list']
        else:
            logging.warning(f"Unexpected JSON structure from generate_training_phrases: {content}. Attempting to find a list of strings.")
            for value in content.values():
                if isinstance(value, list) and all(isinstance(item, str) for item in value):
                    generated = value
                    break
            if not generated:
                raise ValueError(f"Could not extract list of phrases from LLM response: {content}")
    else:
        raise ValueError(f"Unexpected top-level JSON format from generate_training_phrases: {content}")

    unique_generated = []
    for phrase in generated:
        normalized_phrase = phrase.strip().lower()
        if normalized_phrase not in [p.strip().lower() for p in existing_phrases] and \
           normalized_phrase not in [p.strip().lower() for p in unique_generated]:
            unique_generated.append(phrase)

    if len(generated) != len(unique_generated):
        logging.info(f"Removed {len(generated) - len(unique_generated)} duplicate/existing phrases from generated list.")

    return unique_generated

# --- Reflection Layer ---
def reflect_on_loop(result_data, user_profile, current_session_context):
    """
    Evaluates a simulated AAC loop turn and provides a comprehensive reflection
    with mood mapping and actionable insights.
    result_data should contain parent_input, full_sentence, tiles, intent, emotion,
    response_type, loop_score_estimate.
    current_session_context includes environmental/physiological factors.
    """
    age_label = user_profile.get("age_label", "unknown age")
    temperament = user_profile.get("temperament", "typical temperament")
    communication_style = user_profile.get("communication_style", "standard for their age group")
    common_emotions = user_profile.get("common_emotions", "varied")

    environment = current_session_context.get("environmental_factors", "typical home environment")
    physiology = current_session_context.get("physiological_state", "comfortable and alert")
    antecedent = current_session_context.get("recent_antecedent_event", "no specific antecedent")

    parsed_intent_for_reflection = result_data.get("intent", "unknown")
    emotion_tone_for_reflection = result_data.get("emotion", "unknown")


    prompt = f"""
Evaluate this AAC-style emotional loop turn in detail, providing a comprehensive reflection with mood mapping and actionable insights.

Parent input: "{result_data['parent_input']}"
User Profile:
- Age: {age_label}
- Temperament: {temperament}
- Communication Style: {communication_style}
- Common Emotions: {', '.join(common_emotions) if isinstance(common_emotions, list) else common_emotions}

Current Session Context:
- Environment: {environment}
- Physiological State: {physiology}
- Recent Antecedent: {antecedent}

User full sentence: "{result_data['full_sentence']}"
Tiles chosen: {result_data['tiles']}
Inferred Intent: {parsed_intent_for_reflection}"
Inferred Emotion: {emotion_tone_for_reflection}"
Expected Response Type: {result_data['response_type']}"
Loop Score Estimate (0-1): {result_data['loop_score_estimate']} (A score closer to 1 indicates a successful communication exchange that advances the conversation or clearly expresses intent. A score closer to 0 indicates a breakdown in communication, confusion, or an unclear response.)

Provide a detailed analysis in JSON format, specifically including:
1.  **emoji**: A single emoji summarizing the overall sentiment of this turn.
2.  **mood_summary**: A concise (1-3 words) description of the user's primary mood during this interaction.
3.  **communication_effectiveness**: Categorize the overall communication success of this turn. Choose from: "Highly Effective", "Mostly Effective", "Partially Effective (some clarity issues)", "Ineffective (breakdown)".
4.  **mood_mapping_detail**: A sentence or two detailing the specific emotional state and needs of the user as inferred from their response, linking to their profile and the current context.
5.  **reflection_analysis**: A narrative analysis of the turn. Explain *why* the communication was effective or not, considering the current context. Comment on the choice of full sentence (text, 1-word, or emoji-centric) and its appropriateness. Discuss the alignment of the full sentence, tiles, intent, and emotion.
6.  **suggested_image_for_aac**: A descriptive suggestion for a visual image or icon that would reinforce the user's communication (e.g., "A child holding a 'no' sign," "A slice of pizza with a happy face").
7.  **suggested_action_for_caregiver**: Actionable advice for the caregiver based on this turn. What should the caregiver do next? How can they best support or respond to the user's communication, given the context? (e.g., "Affirm the choice," "Offer alternatives," "Check for discomfort," "Rephrase the question").
8.  **improvement_opportunities**: If the 'loop_score_estimate' is below 0.9, identify specific areas for improvement in the user's communication or the system's interpretation (e.g., "More specific tiles needed," "Emotion was unclear," "Response was off-topic"), considering the current context.
9.  **why_this_response**: A concise explanation (1-2 sentences) of *why* the user might have chosen to communicate this way (e.g., "Expresses a strong preference visually," "Directly answers the question with minimal effort").
10. **what_user_feels**: A direct statement (1 sentence) about the specific feeling(s) the user is experiencing.
11. **what_user_needs**: A direct statement (1 sentence) about what the user needs or wants from the caregiver at this moment.
12. **is_clear**: Boolean (true/false) indicating if the communication was unambiguous.
13. **clarity_score**: A float from 0.0 to 1.0, where 1.0 is perfectly clear.

Return ONLY this JSON, ensuring all fields are populated:
{{
    "emoji": "...",
    "mood_summary": "...",
    "communication_effectiveness": "...",
    "mood_mapping_detail": "...",
    "reflection_analysis": "...",
    "suggested_image_for_aac": "...",
    "suggested_action_for_caregiver": "...",
    "improvement_opportunities": "...",
    "why_this_response": "...",
    "what_user_feels": "...",
    "what_user_needs": "...",
    "is_clear": true,
    "clarity_score": 0.9
}}
"""
    logging.debug(f"Reflecting on: {result_data['full_sentence']}")
    response = call_openai_with_retry(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "You are an emotionally intelligent and highly analytical AAC loop reflection engine. Provide constructive, insightful, and actionable analysis based on the communication turn, considering the user's profile and current environmental/physiological context."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6,
        max_tokens=600,
        response_format={"type": "json_object"} # Correct for this model to request JSON
    )
    return json.loads(response.choices[0].message.content)

# --- Simulate User Responses ---
def simulate_loop(parent_input, user_profile, current_session_context):
    """
    Simulates user responses based on parent input, a detailed user profile,
    and the current session context.
    Generates 4 distinct responses with a mix of communication styles.
    """
    age = user_profile.get("age_label", "unknown age")
    temperament = user_profile.get("temperament", "typical temperament")
    communication_style = user_profile.get("communication_style", "standard for their age group")
    common_emotions = user_profile.get("common_emotions", "varied")

    environment = current_session_context.get("environmental_factors", "typical home environment")
    physiology = current_session_context.get("physiological_state", "comfortable and alert")
    antecedent = current_session_context.get("recent_antecedent_event", "no specific antecedent")


    PROMPT_TEMPLATE = f"""
You are simulating a loop-aware AAC system for a non-verbal user.

Input from Parent/Therapist: "{parent_input}"

User Profile:
- Age: {age}
- Temperament: {temperament}
- Communication Style: {communication_style}
- Common Emotions: {', '.join(common_emotions) if isinstance(common_emotions, list) else common_emotions}

Current Session Context:
- Environment: {environment}
- Physiological State: {physiology}
- Recent Antecedent Event: {antecedent}

Your Role: Act as the non-verbal user. Consider how the user's profile and the current context would influence their response.

Generate 4 distinct user responses that reflect:
- Emotional variety (e.g., affirm, reject, request, clarify, express a feeling like happiness, sadness, frustration, curiosity, boredom)
- A realistic 'loop_score_estimate' from 0.0 to 1.0, where 1.0 is a perfect, clear communication exchange, and 0.0 is a complete communication breakdown or irrelevant response.
- Adherence to the user's defined communication style and temperament, *and* the current context.

**Crucially, ensure a mix of the following communication styles for the 'full_sentence' field across the 4 responses:**

1.  **Full, Natural Language Sentence:** A complete, textual sentence, similar to how a verbal person might respond.
    * Example: "I want to go to the park now."
2.  **One-Word Response:** A single, clear word that serves as a complete communication.
    * Example: "Yes." or "Hungry." or "No."
3.  **Emoji-Centric Sentence (2-3 examples):** Primarily uses emojis to convey meaning and emotion, with minimal clarifying text. Aim for sequences of 3-7 emojis, potentially with 1-3 words.
    * Example: "🚫🏫 wanna? 🎮📺" (No school? Want to play video games or watch TV?)
    * Example: "🍕 hungry 🤤 yes!" (Pizza? I'm hungry, yes!)
    * Example: "💔 sad 😭 want 🤗" (I'm sad, I want a hug.)

For each response, also provide:
- Short, core tile options for AAC systems (2-5 words, highly relevant to the full sentence, or the single word if it's a one-word response)
- 'intent', 'emotion', and 'response_type', and 'loop_score_estimate' for classification.

Return ONLY this JSON, ensuring 'responses' is a list of exactly 4 dictionaries:
{{
    "responses": [
        {{
            "tiles": ["...", "..."],
            "full_sentence": "...",
            "intent": "...",
            "emotion": "...",
            "response_type": "...",
            "loop_score_estimate": 0.87
        }},
        {{
            "tiles": ["...", "..."],
            "full_sentence": "...",
            "intent": "...",
            "emotion": "...",
            "response_type": "...",
            "loop_score_estimate": 0.5
        }},
        {{
            "tiles": ["...", "..."],
            "full_sentence": "...",
            "intent": "...",
            "emotion": "...",
            "response_type": "...",
            "loop_score_estimate": 0.95
        }},
        {{
            "tiles": ["...", "..."],
            "full_sentence": "...",
            "intent": "...",
            "emotion": "...",
            "response_type": "...",
            "loop_score_estimate": 0.3
        }}
    ]
}}
"""
    logging.info(f"Simulating for parent input: '{parent_input}' and profile: {user_profile.get('profile_name', user_profile.get('age_label', 'unknown'))}")
    response = call_openai_with_retry(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "You are a highly empathetic and realistic non-verbal user language simulation engine. You will produce responses that vary in communication style as requested, reflecting realistic AAC usage, heavily influenced by the user's profile and the provided session context."},
            {"role": "user", "content": PROMPT_TEMPLATE}
        ],
        temperature=0.75,
        max_tokens=800,
        response_format={"type": "json_object"} # Correct for this model to request JSON
    )
    result_list = json.loads(response.choices[0].message.content)["responses"]
    return result_list

# --- GPT-based Selection and Next Turn Generation ---
def gpt_select_best_response(parent_input, child_responses, user_profile, current_session_context):
    """
    Ask GPT to choose the most emotionally appropriate child response from a list of options.
    Returns (chosen_index, {}). The reasoning for non-chosen options is no longer generated here.
    """
    response_options_list = []
    for i, r in enumerate(child_responses):
        full_sentence = r.get("full_sentence", "[Missing Sentence]")
        intent = r.get("intent", "unknown")
        emotion = r.get("emotion", "unknown")
        # Ensure reflection is present before trying to access its keys
        mood_summary = r.get("reflection", {}).get("mood_summary", "N/A")
        effectiveness = r.get("reflection", {}).get("communication_effectiveness", "N/A")
        clarity = r.get("reflection", {}).get("is_clear", "N/A")

        response_options_list.append(
            f"{i+1}. \"{full_sentence}\" (Intent: {intent}, Emotion: {emotion}, Mood: {mood_summary}, Clarity: {clarity}, Effectiveness: {effectiveness})"
        )
    response_options = "\n".join(response_options_list)

    user_profile_str = f"""
    - Age: {user_profile.get('age_label')}
    - Temperament: {user_profile.get('temperament')}
    - Communication Style: {user_profile.get('communication_style')}
    - Common Emotions: {', '.join(user_profile.get('common_emotions', []))}
    """
    context_str = f"""
Current Session Context:
- Environment: {current_session_context.get("environmental_factors", "N/A")}
- Physiological State: {current_session_context.get("physiological_state", "N/A")}
- Recent Antecedent Event: {current_session_context.get("recent_antecedent_event", "N/A")}
"""

    selection_prompt = f"""
You are simulating a caregiver reviewing 4 possible AAC-style child responses.
The parent said: "{parent_input}"

User profile:
{user_profile_str}
{context_str}

Here are the 4 responses:
{response_options}

Pick the most emotionally appropriate and realistic response given the parent's input, the user's profile, and the current session context.
Return ONLY this JSON:
{{
    "chosen_index": 1
}}
"""
    logger.debug("GPT selecting best response...")
    selection_result = call_openai_with_retry(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": selection_prompt}],
        temperature=0.3,
        max_tokens=50,
        response_format={"type": "json_object"} # Correct for this model to request JSON
    )
    chosen_index = json.loads(selection_result.choices[0].message.content).get("chosen_index")
    if chosen_index is None:
        logger.error(f"GPT selection returned no 'chosen_index'. Full response: {selection_result.choices[0].message.content}")
        chosen_index = 1 # Fallback to first option if GPT fails to return index
    chosen_index_0_based = chosen_index - 1

    selection_reasoning = {} # Empty dict as per requirement

    return chosen_index_0_based, selection_reasoning


def generate_next_parent_turn(child_sentence, full_history=None, user_profile=None, current_session_context=None):
    """
    Generates the next parent message based on the child's last response and full conversation history.
    Also suggests updates to the session context.
    """
    messages = [
        {"role": "system", "content": "You are a supportive, empathetic, and realistic caregiver in a real-life conversation. Your responses should advance the conversation naturally and consider the user's profile and the evolving session context. Propose how the session context might subtly shift based on the interaction."},
    ]

    user_profile_str = f"Current User Profile:\n" + \
                       f"- Age: {user_profile.get('age_label')}\n" + \
                       f"- Temperament: {user_profile.get('temperament')}\n" + \
                       f"- Communication Style: {user_profile.get('communication_style')}\n" + \
                       f"- Common Emotions: {', '.join(user_profile.get('common_emotions', []))}"

    context_str = ""
    if current_session_context:
        context_str = f"\nCurrent Session Context:\n" + \
                      f"- Environment: {current_session_context.get('environmental_factors', 'N/A')}\n" + \
                      f"- Physiological State: {current_session_context.get('physiological_state', 'N/A')}\n" + \
                      f"- Recent Antecedent Event: {current_session_context.get('recent_antecedent_event', 'N/A')}\n" + \
                      f"- Child Mood Trend: {current_session_context.get('child_mood_trend', 'N/A')}"

    messages.append({"role": "user", "content": user_profile_str + context_str})

    if full_history:
        for turn in full_history:
            # Use .lower() to handle "Parent", "Child", "System_Consequence" from full_history
            speaker_key = str(turn.get('speaker', '')).strip().lower()

            # Map to OpenAI's required roles
            if speaker_key == "user" or speaker_key == "parent":
                messages.append({"role": "user", "content": turn['text']})
            elif speaker_key == "assistant" or speaker_key == "child":
                messages.append({"role": "assistant", "content": turn['text']})
            elif speaker_key == "system_consequence":
                messages.append({"role": "user", "content": f"(Observation) {turn['text']}"})
            else:
                logger.warning(f"Unexpected or invalid speaker role in history: '{turn.get('speaker')}' (processed as '{speaker_key}'). Mapping to 'user'.")
                messages.append({"role": "user", "content": turn['text']})

    messages.append({"role": "user", "content": f"Child just said: \"{child_sentence}\"\n\nWhat should the caregiver say next? Also, propose a subtle update to the session context based on this turn. For example, if the child expressed tiredness, suggest 'physiological_state': 'more tired'. If they became engaged, suggest 'environmental_factors': 'less distracting'. If a new topic emerged, suggest 'recent_antecedent_event': 'new activity initiated'. Return the next prompt and the updated context in JSON. The JSON must strictly adhere to the following structure:\n\n{{\n  \"next_prompt\": \"[caregiver's next question/statement]\",\n  \"updated_session_context\": {{\n    \"environmental_factors\": \"[updated environment]\",\n    \"physiological_state\": \"[updated physiological state]\",\n    \"recent_antecedent_event\": \"[updated antecedent]\",\n    \"child_mood_trend\": \"[updated mood trend]\"\n  }}\n}}\nEnsure all nested fields within 'updated_session_context' are present, even if their values remain similar to the original context. If a field value in 'updated_session_context' doesn't change, just repeat its current value."})

    # Corrected response_format for models supporting JSON mode
    response_format_config = {
        "type": "json_object"
    }

    logging.debug("GPT generating next parent turn and context update...")
    logging.debug(f"DEBUG: Final messages payload being sent to OpenAI in generate_next_parent_turn:\n{json.dumps(messages, indent=2)}")

    result = call_openai_with_retry(
        model="gpt-3.5-turbo-1106", # This model supports response_format={"type": "json_object"}
        messages=messages,
        temperature=0.6,
        max_tokens=200,
        response_format=response_format_config
    )
    content = json.loads(result.choices[0].message.content)
    # Ensure updated_session_context exists and is a dictionary, default to empty if not
    updated_context = content.get("updated_session_context", {})
    # Ensure all expected keys are present in updated_context, providing defaults if missing
    default_context_keys = ["environmental_factors", "physiological_state", "recent_antecedent_event", "child_mood_trend"]
    for key in default_context_keys:
        if key not in updated_context:
            updated_context[key] = current_session_context.get(key, "N/A") # Fallback to original context or N/A

    return content.get("next_prompt", "Okay."), updated_context

# --- New Function for Dynamic Turn Taking ---
def detect_initiation_shift(child_response: dict, user_profile: dict, current_session_context: dict) -> str:
    """
    Determines who should initiate the next turn based on the child's response,
    user profile, and current session context.
    Returns "parent" (parent asks), "child" (child initiates/asks), or "pause" (break needed).
    """
    full_sentence = child_response.get("full_sentence", "").lower().strip()
    intent = child_response.get("intent", "unknown").lower()
    emotion = child_response.get("emotion", "neutral").lower()
    loop_score = child_response.get("loop_score_estimate", 0.0)

    logger.debug(f"Detecting initiation shift for: '{full_sentence}' (Intent: {intent}, Emotion: {emotion}, Score: {loop_score:.2f})")

    # --- CHILD initiated turn (question or clear request for action) ---
    # Check for explicit questions or clear requests
    question_keywords = ["?", "what", "where", "when", "why", "how", "can i", "do you want", "should we", "want to"]
    if any(keyword in full_sentence for keyword in question_keywords) or \
       intent == "request" or \
       (intent == "inquiry" and loop_score > 0.7): # High confidence inquiry
        logger.info(f"  --> Initiation: CHILD (question/request detected: '{full_sentence}')")
        return "child"

    # --- PAUSE/End of interaction ---
    pause_keywords = ["no more", "done", "finished", "break", "sleep", "not now", "later", "go away", "stop"]
    strong_negative_emotions_for_pause = ["frustrated", "angry", "overwhelmed", "agitated", "distressed", "annoyed"]

    # If child's response is short, clear rejection with low score and negative emotion
    if full_sentence in ["no", "nope", "nah"] and emotion in strong_negative_emotions_for_pause and loop_score < 0.5:
        logger.info(f"  --> Initiation: PAUSE (strong negative rejection: '{full_sentence}')")
        return "pause"

    # If physiological state is already tired/unwell and child expresses discomfort/tiredness
    phys_state = current_session_context.get("physiological_state", "normal").lower()
    if phys_state in ["tired", "unwell", "sick", "hungry", "overwhelmed"] and \
       emotion in ["tired", "uncomfortable", "pain", "hungry", "irritable", "overwhelmed"]:
        logger.info(f"  --> Initiation: PAUSE (physiological state + discomfort/emotion: '{full_sentence}')")
        return "pause"

    # If pause keywords are explicitly used
    if any(keyword in full_sentence for keyword in pause_keywords):
        logger.info(f"  --> Initiation: PAUSE (pause keyword detected: '{full_sentence}')")
        return "pause"

    # If communication is generally ineffective and emotion is negative
    if loop_score < 0.3 and emotion in strong_negative_emotions_for_pause:
        logger.info(f"  --> Initiation: PAUSE (low clarity + strong negative emotion: '{full_sentence}')")
        return "pause"

    # --- PARENT continues (default, or child expresses needs/emotions that need caregiver response) ---
    # This is the default if neither "child" nor "pause" conditions are met.
    # Emotions that typically prompt a caregiver response to continue the conversation.
    needs_caregiver_emotions_to_continue = ["sad", "hungry", "thirsty", "uncomfortable", "pain", "confused", "anxious", "curious", "happy", "excited", "bored"]
    if emotion in needs_caregiver_emotions_to_continue or intent in ["express_feeling", "state_need", "affirmation", "comment"]:
        logger.info(f"  --> Initiation: PARENT (child expressed need/emotion/comment: '{full_sentence}')")
        return "parent"

    # Default to parent continuing if no other clear signal
    logger.info(f"  --> Initiation: PARENT (default: '{full_sentence}')")
    return "parent"


# --- Context & Consequence Generation ---
def generate_initial_session_context(user_profile):
    """
    Generates an initial, realistic session context based on the user profile.
    """
    prompt = f"""
Given the following user profile, generate a realistic initial session context.
User Profile:
- Age: {user_profile.get('age_label')}
- Temperament: {user_profile.get('temperament')}
- Communication Style: {user_profile.get('communication_style')}
- Common Emotions: {', '.join(user_profile.get('common_emotions', []))}

Return ONLY a JSON object with the following fields:
{{
    "environmental_factors": "e.g., quiet living room, noisy classroom, busy playground",
    "physiological_state": "e.g., well-rested, slightly hungry, comfortable, tired",
    "recent_antecedent_event": "e.g., just finished snack, bell rang, caregiver entered room, saw a favorite toy",
    "child_mood_trend": "e.g., neutral, slightly positive, slightly anxious"
}}
"""
    logger.debug("Generating initial session context...")
    try:
        response = call_openai_with_retry(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a context generator for a communication simulation. Provide realistic initial scenarios."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=150,
            response_format={"type": "json_object"} # Correct for this model to request JSON
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Failed to generate initial session context: {e}", exc_info=True)
        return {
            "environmental_factors": "home setting",
            "physiological_state": "normal",
            "recent_antecedent_event": "none specified",
            "child_mood_trend": "neutral"
        }

def analyze_caregiver_input(parent_input, user_profile, current_session_context):
    """
    Analyzes the caregiver's input for clarity, tone, and appropriateness
    given the user profile and current session context.
    """
    prompt = f"""
Analyze the following caregiver input in the context of the user's profile and current session.
Caregiver Input: "{parent_input}"
User Profile:
- Age: {user_profile.get('age_label')}
- Temperament: {user_profile.get('temperament')}
- Communication Style: {user_profile.get('communication_style')}
Current Session Context:
- Environment: {current_session_context.get("environmental_factors", "N/A")}
- Physiological State: {current_session_context.get("physiological_state", "N/A")}
- Recent Antecedent Event: {current_session_context.get("recent_antecedent_event", "N/A")}

Return ONLY a JSON object with these fields:
{{
    "clarity": "e.g., very clear, somewhat ambiguous, unclear",
    "tone": "e.g., calm, enthusiastic, slightly rushed, questioning",
    "appropriateness": "e.g., highly appropriate, generally appropriate, somewhat inappropriate",
    "analysis_text": "A brief explanation (1-2 sentences) of why it was effective or not."
}}
"""
    logger.debug(f"Analyzing caregiver input: '{parent_input}'...")
    try:
        response = call_openai_with_retry(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are an analytical assistant evaluating caregiver communication in an AAC context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=150,
            response_format={"type": "json_object"} # Correct for this model to request JSON
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Failed to analyze caregiver input: {e}", exc_info=True)
        return {"clarity": "N/A", "tone": "N/A", "appropriateness": "N/A", "analysis_text": "Analysis failed."}

def generate_consequence(parent_input, chosen_child_response, next_parent_input, user_profile, current_session_context):
    """
    Generates a realistic consequence of the interaction, detailing the child's reaction
    and any subtle shifts in the situation.
    """
    prompt = f"""
Describe the immediate consequence of the following AAC interaction. Focus on the non-verbal user's reaction (e.g., behavioral, emotional, engagement level) and any subtle shifts in the environment or the interaction's flow.

Parent Input: "{parent_input}"
Child Response: "{chosen_child_response.get('full_sentence', '[Missing Sentence]')}" (Intent: {chosen_child_response.get('intent', 'unknown')}, Emotion: {chosen_child_response.get('emotion', 'unknown')})
Next Parent Action: "{next_parent_input}"

User Profile:
- Age: {user_profile.get('age_label')}
- Temperament: {user_profile.get('temperament')}
- Communication Style: {user_profile.get('communication_style')}
Current Session Context (before this consequence):
- Environment: {current_session_context.get("environmental_factors", "N/A")}
- Physiological State: {current_session_context.get("physiological_state", "N/A")}
- Recent Antecedent Event: {current_session_context.get("recent_antecedent_event", "N/A")}

Return ONLY a JSON object with these fields:
{{
    "child_immediate_reaction": "e.g., smiled and looked at toy, frowned and turned away, reached for caregiver's hand",
    "interaction_flow_change": "e.g., conversation smoothly continued, slight pause, topic shift, user became distracted",
    "consequence_analysis": "A brief explanation (1-2 sentences) of the overall outcome and how it relates to the interaction.",
    "level_of_independence_demonstrated": "e.g., fully independent, partially independent (implied prompt needed), prompted response"
}}
"""
    logger.debug("Generating consequence of interaction...")
    try:
        response = call_openai_with_retry(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are an observer of behavioral interactions. Describe realistic immediate consequences."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200,
            response_format={"type": "json_object"} # Correct for this model to request JSON
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Failed to generate consequence: {e}", exc_info=True)
        return {
            "child_immediate_reaction": "N/A (Error)",
            "interaction_flow_change": "N/A (Error)",
            "consequence_analysis": "Consequence generation failed.",
            "level_of_independence_demonstrated": "N/A"
        }

def predict_emotional_transition(last_child_response, next_parent_input, user_profile, current_session_context):
    """
    Predicts the user's emotional and behavioral shift if the caregiver
    misinterprets or does not respond optimally to the child's last message.
    """
    prompt = f"""
Consider the following interaction between a caregiver and a non-verbal user.

User Profile:
- Age: {user_profile.get('age_label')}
- Temperament: {user_profile.get('temperament')}
- Communication Style: {user_profile.get('communication_style')}
- Common Emotions: {', '.join(user_profile.get('common_emotions', []))}

Current Session Context:
- Environment: {current_session_context.get("environmental_factors", "N/A")}
- Physiological State: {current_session_context.get("physiological_state", "N/A")}
- Recent Antecedent Event: {current_session_context.get("recent_antecedent_event", "N/A")}
- Child Mood Trend: {current_session_context.get("child_mood_trend", "N/A")}

Child's Last Response: "{last_child_response.get('full_sentence', '[Missing Sentence]')}"
Inferred Intent: {last_child_response.get('intent', 'unknown')}
Inferred Emotion: {last_child_response.get('emotion', 'unknown')}
Caregiver's Planned Next Action (as inferred from the next_parent_input): "{next_parent_input}"

If the caregiver's *planned* next action was suboptimal (e.g., they didn't understand, ignored, or responded incorrectly), how might the user's emotional state and behavior shift?
Focus on plausible, realistic reactions given the user's profile and current context.

Return ONLY a JSON object with these fields:
{{
    "predicted_emotional_shift": "e.g., from happy to frustrated, from curious to confused, from neutral to agitated",
    "predicted_behavioral_reaction": "e.g., turned away, vocalized loudly, repeated response, became quiet, sought comfort",
    "reasoning": "A brief explanation (1-2 sentences) of why this shift is likely."
}}
"""
    logging.debug("Predicting emotional transition for suboptimal response...")
    try:
        response = call_openai_with_retry(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a realistic behavior analyst predicting emotional and behavioral shifts in non-verbal individuals based on communication context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200,
            response_format={"type": "json_object"} # Correct for this model to request JSON
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Failed to predict emotional transition: {e}", exc_info=True)
        return {
            "predicted_emotional_shift": "N/A (Error)",
            "predicted_behavioral_reaction": "N/A (Error)",
            "reasoning": "Prediction failed."
        }

# --- ABA Therapist Summary Generator (Multidisciplinary Insights) ---
def generate_final_aba_summary(full_conversation_data):
    """
    Generates a final integrated ABA therapist, Language Pathologist (SLP),
    Occupational Therapist (OT), Physical Therapist (PT), Developmental Psychologist,
    and Special Education Teacher reflection/report for the parent/caregiver
    based on the full conversation turns, including visual prompt suggestions.
    """
    turns = full_conversation_data["conversation_turns"]
    user_profile = full_conversation_data["user_profile"]

    age_label = user_profile.get("age_label", "unknown age")
    temperament = user_profile.get("temperament", "typical temperament")
    communication_style = user_profile.get("communication_style", "standard for their age group")

    transcript_parts = []
    for turn in turns:
        parent_analysis = turn.get("caregiver_input_analysis", {})
        consequence_data = turn.get("consequence_of_interaction", {})
        turn_context = turn.get("initial_context", {})
        chosen_response = turn["chosen_response"]

        transcript_parts.append(f"--- Turn {turn['turn_number']} ---")
        transcript_parts.append(f"Context: Env - {turn_context.get('environmental_factors', 'N/A')}, Phys - {turn_context.get('physiological_state', 'N/A')}, Antecedent - {turn_context.get('recent_antecedent_event', 'N/A')}")
        transcript_parts.append(f"Parent Input: \"{turn['parent_input']}\" (Clarity: {parent_analysis.get('clarity', 'N/A')}, Tone: {parent_analysis.get('tone', 'N/A')})")
        transcript_parts.append(f"Child Response: \"{chosen_response.get('full_sentence', '[Missing Sentence]')}\" (Intent: {chosen_response.get('intent', 'unknown')}, Emotion: {chosen_response.get('emotion', 'unknown')}, Score: {chosen_response.get('loop_score_estimate', 0.0):.2f})")
        transcript_parts.append(f"  Why Response: {chosen_response.get('reflection', {}).get('why_this_response', 'N/A')}")
        transcript_parts.append(f"  User Feels: {chosen_response.get('reflection', {}).get('what_user_feels', 'N/A')}")
        transcript_parts.append(f"  User Needs: {chosen_response.get('reflection', {}).get('what_user_needs', 'N/A')}")
        transcript_parts.append(f"  Is Clear: {chosen_response.get('reflection', {}).get('is_clear', 'N/A')}, Clarity Score: {chosen_response.get('reflection', {}).get('clarity_score', 'N/A'):.2f}")
        transcript_parts.append(f"Consequence: {consequence_data.get('child_immediate_reaction', 'N/A')} | Independence: {consequence_data.get('level_of_independence_demonstrated', 'N/A')}")
        if turn.get("predicted_suboptimal_reaction"):
            transcript_parts.append(f"  Predicted Suboptimal: Shift - {turn['predicted_suboptimal_reaction'].get('predicted_emotional_shift')}, Behavior - {turn['predicted_suboptimal_reaction'].get('predicted_behavioral_reaction')}")
        
        # Add new turn-taking info to summary
        transcript_parts.append(f"  Initiation Mode for Next Turn: {turn.get('initiation_mode_for_next_turn', 'N/A')}")
        transcript_parts.append(f"  Next Parent Prompt (Decided): \"{turn.get('next_parent_prompt_predicted', 'N/A')}\"")
        transcript_parts.append(f"---")

    full_transcript_for_summary = "\n".join(transcript_parts)


    prompt = f"""
You are a highly experienced and collaborative professional team, integrating insights from an ABA therapist, Speech-Language Pathologist (SLP), Occupational Therapist (OT), Physical Therapist (PT), Developmental Psychologist, and Special Education Teacher. Your goal is to provide a comprehensive analysis of the simulated AAC conversation below.

Review the full conversation, focusing on:
- Overall communication effectiveness and patterns.
- Behavioral responses and their context.
- Physical and sensory factors influencing AAC use.
- Cognitive and emotional regulation.
- Generalization of skills and educational implications.

Synthesize these perspectives to provide a holistic understanding of the non-verbal user's interaction.

User Profile:
- Age: {age_label}
- Temperament: {temperament}
- Communication Style: {communication_style}

Full Conversation Transcript with Context and Consequences:
{full_transcript_for_summary}

Provide a comprehensive JSON summary with the following fields, ensuring all are populated based on the entire conversation, reflecting a joint, multidisciplinary perspective:
{{
  "overall_session_summary": "...",
  "communication_analysis_slp_focus": "...",
  "behavioral_analysis_aba_focus": "...",
  "ot_considerations": "...",
  "pt_considerations": "...",
  "cognitive_emotional_insights": "...",
  "educational_implications": "...",
  "emotional_pattern": "...",
  "strengths": "...",
  "support_needs": "...",
  "caregiver_guidance": "...",
  "recommended_visual_aids_and_strategies": "..."
}}
"""
    logging.info(f"Generating final integrated multidisciplinary summary for session {full_conversation_data['session_id']}...")
    try:
        response = call_openai_with_retry(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a professional, empathetic, and insightful team comprising an ABA therapist, Speech-Language Pathologist, Occupational Therapist, Physical Therapist, Developmental Psychologist, and Special Education Teacher, providing comprehensive and actionable integrated summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1200,
            response_format={"type": "json_object"} # Correct for this model to request JSON
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"❌ Failed to generate integrated multidisciplinary summary for session {full_conversation_data['session_id']}: {e}", exc_info=True)
        return {
            "overall_session_summary": "Multidisciplinary summary generation failed.",
            "communication_analysis_slp_focus": "N/A",
            "behavioral_analysis_aba_focus": "N/A",
            "ot_considerations": "N/A",
            "pt_considerations": "N/A",
            "cognitive_emotional_insights": "N/A",
            "educational_implications": "N/A",
            "emotional_pattern": "N/A",
            "strengths": "N/A",
            "support_needs": "N/A",
            "caregiver_guidance": "N/A",
            "recommended_visual_aids_and_strategies": "N/A (Error generating suggestions)"
        }

# --- User Profiles ---
USER_PROFILES = {
    "child_4_7_curious": {
        "profile_name": "Curious Child (4-7)",
        "age_label": "4-7 years",
        "temperament": "curious and energetic",
        "communication_style": "simple sentences, asks 'why' frequently, enjoys exploring",
        "common_emotions": ["happy", "curious", "mildly frustrated", "excited"]
    },
    "child_7_10_shy": {
        "profile_name": "Shy Child (7-10)",
        "age_label": "7-10 years",
        "temperament": "shy and thoughtful",
        "communication_style": "prefers short, direct answers, takes time to respond, avoids confrontation",
        "common_emotions": ["calm", "nervous", "interested", "content"]
    },
    "child_11_15_expressive": {
        "profile_name": "Expressive Teen (11-15)",
        "age_label": "11-15 years",
        "temperament": "expressive and independent",
        "communication_style": "can form complex sentences, strong opinions, sometimes sarcastic",
        "common_emotions": ["confident", "frustrated", "bored", "amused"]
    },
    "teen_16_19_adultlike": {
        "profile_name": "Mature Teen (16-19)",
        "age_label": "16-19 years",
        "temperament": "mature and reflective",
        "communication_style": "detailed responses, considers consequences, seeks understanding",
        "common_emotions": ["thoughtful", "analytical", "occasionally stressed", "determined"]
    },
    "young_adult_20_25_independent": {
        "profile_name": "Independent Young Adult (20-25)",
        "age_label": "20-25 years",
        "temperament": "independent and proactive",
        "communication_style": "clear communication of needs/wants, problem-solving oriented",
        "common_emotions": ["assertive", "busy", "content", "occasionally overwhelmed"]
    },
    "adult_25_60_professional": {
        "profile_name": "Adult (25-60, Professional)",
        "age_label": "25-60 years",
        "temperament": "composed and practical",
        "communication_style": "focused on daily tasks, seeks efficiency, clear and concise",
        "common_emotions": ["neutral", "tired", "focused", "satisfied"]
    },
    "senior_60_90_patient": {
        "profile_name": "Patient Senior (60-90)",
        "age_label": "60-90 years",
        "temperament": "patient and reflective",
        "communication_style": "takes time to process, values clarity, may express physical needs more frequently",
        "common_emotions": ["calm", "content", "minor discomfort", "grateful"]
    }
}

# --- Output Folder & Training Data Files ---
output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

TRAINING_DATA_FILES = {
    "dialogue": os.path.join(output_dir, "training_data_dialogue.jsonl"),
    "intent": os.path.join(output_dir, "training_data_intent.jsonl"),
    "emotion": os.path.join(output_dir, "training_data_emotion.jsonl"),
    "tiles": os.path.join(output_dir, "training_data_tiles.jsonl"),
    "reward": os.path.join(output_dir, "training_data_reward.jsonl"),
    "full_conversations": os.path.join(output_dir, "training_data_full_conversations.jsonl")
}

for file_path in TRAINING_DATA_FILES.values():
    if os.path.exists(file_path):
        pass # Keep existing files; new data will be appended

# Helper function to append to JSONL files
def append_training_data(full_conversation_data, turn_data):
    dialogue_entry = {
        "session_id": full_conversation_data["session_id"],
        "turn_number": turn_data["turn_number"],
        "parent_input": turn_data["parent_input"],
        "child_full_sentence": turn_data["chosen_response"]["full_sentence"],
        "user_profile_key": full_conversation_data["user_profile_key"],
        "initial_context": turn_data["initial_context"]
    }
    if "updated_session_context_from_parent_turn_gen" in turn_data:
        dialogue_entry["updated_context_at_turn_end"] = turn_data["updated_session_context_from_parent_turn_gen"]
    if "initiation_mode_for_next_turn" in turn_data:
        dialogue_entry["initiation_mode_for_next_turn"] = turn_data["initiation_mode_for_next_turn"]
    if "next_parent_prompt_predicted" in turn_data:
        dialogue_entry["next_parent_prompt_predicted"] = turn_data["next_parent_prompt_predicted"]

    with open(TRAINING_DATA_FILES["dialogue"], "a") as f:
        f.write(json.dumps(dialogue_entry) + "\n")

    intent_entry = {
        "session_id": full_conversation_data["session_id"],
        "turn_number": turn_data["turn_number"],
        "parent_input": turn_data["parent_input"],
        "child_full_sentence": turn_data["chosen_response"]["full_sentence"],
        "intent": turn_data["chosen_response"]["intent"]
    }
    with open(TRAINING_DATA_FILES["intent"], "a") as f:
        f.write(json.dumps(intent_entry) + "\n")

    emotion_entry = {
        "session_id": full_conversation_data["session_id"],
        "turn_number": turn_data["turn_number"],
        "parent_input": turn_data["parent_input"],
        "child_full_sentence": turn_data["chosen_response"]["full_sentence"],
        "emotion": turn_data["chosen_response"]["emotion"]
    }
    with open(TRAINING_DATA_FILES["emotion"], "a") as f:
        f.write(json.dumps(emotion_entry) + "\n")

    tiles_entry = {
        "session_id": full_conversation_data["session_id"],
        "turn_number": turn_data["turn_number"],
        "parent_input": turn_data["parent_input"],
        "child_full_sentence": turn_data["chosen_response"]["full_sentence"],
        "tiles": turn_data["chosen_response"]["tiles"]
    }
    with open(TRAINING_DATA_FILES["tiles"], "a") as f:
        f.write(json.dumps(tiles_entry) + "\n")

    reward_entry = {
        "session_id": full_conversation_data["session_id"],
        "turn_number": turn_data["turn_number"],
        "parent_input": turn_data["parent_input"],
        "child_full_sentence": turn_data["chosen_response"]["full_sentence"],
        "loop_score_estimate": turn_data["chosen_response"]["loop_score_estimate"]
    }
    with open(TRAINING_DATA_FILES["reward"], "a") as f:
        f.write(json.dumps(reward_entry) + "\n")

# --- Begin Autonomous Loop for Data Generation ---
num_training_phrases_per_batch = 10
total_desired_initial_phrases = 20
MAX_CONVERSATION_TURNS = 5 # Maximum turns per conversation before generating summary

all_generated_initial_phrases = []

logging.info(f"Starting data generation. Aiming for {total_desired_initial_phrases} unique conversation starting phrases.")

while len(all_generated_initial_phrases) < total_desired_initial_phrases:
    logging.info(f"Generating a new batch of {num_training_phrases_per_batch} initial phrases. Total unique initial phrases so far: {len(all_generated_initial_phrases)}")

    try:
        new_phrases_batch = generate_training_phrases(n=num_training_phrases_per_batch, existing_phrases=all_generated_initial_phrases)
    except ConnectionError as e:
        logging.error(f"Failed to generate new initial phrases due to API connection error: {e}. Retrying in 10 seconds...", exc_info=True)
        time.sleep(10)
        continue
    except Exception as e:
        logging.error(f"An unexpected error occurred during phrase generation: {e}. Retrying in 10 seconds...", exc_info=True)
        time.sleep(10)
        continue

    initial_all_generated_count = len(all_generated_initial_phrases)
    for phrase in new_phrases_batch:
        normalized_phrase = phrase.strip().lower()
        if normalized_phrase not in [p.strip().lower() for p in all_generated_initial_phrases]:
            all_generated_initial_phrases.append(phrase)

    if len(all_generated_initial_phrases) == initial_all_generated_count:
        logging.warning("No new unique initial phrases were generated in this batch. This might indicate exhaustion of unique phrases or difficulty with LLM constraints.")
        if len(all_generated_initial_phrases) < total_desired_initial_phrases:
            logging.warning(f"Could not reach {total_desired_initial_phrases} unique initial phrases. Stopping phrase generation early at {len(all_generated_initial_phrases)}.")
        break # Exit if no new unique phrases are generated to prevent infinite loop if LLM gets stuck

    logging.info(f"Generated batch. Current total unique initial phrases: {len(all_generated_initial_phrases)}")
    time.sleep(2)

logging.info(f"Proceeding to simulate {len(all_generated_initial_phrases)} multi-turn conversations across all user profiles.")

for phrase_idx, initial_parent_phrase in enumerate(all_generated_initial_phrases):
    logging.info(f"Starting conversation {phrase_idx + 1}/{len(all_generated_initial_phrases)} with initial phrase: '{initial_parent_phrase}'")

    for profile_key, user_profile in USER_PROFILES.items():
        logging.info(f"  Simulating for profile: {user_profile['profile_name']}")

        session_id = f"conv_{int(time.time() * 1000)}_{profile_key}_{phrase_idx}"
        full_conversation_data = {
            "session_id": session_id,
            "user_profile_key": profile_key,
            "user_profile": user_profile,
            "conversation_turns": [],
            "generation_metadata": {
                "script_version": "3.5.3", # Incremented for initiation_mode logic
                "run_timestamp": datetime.now().isoformat(),
                "base_model": "gpt-3.5-turbo-0125 / gpt-3.5-turbo-1106 mixed"
            }
        }

        current_session_context = generate_initial_session_context(user_profile)
        logging.info(f"  Initial Context: Env: {current_session_context.get('environmental_factors')}, Phys: {current_session_context.get('physiological_state')}, Ante: {current_session_context.get('recent_antecedent_event')}")

        current_parent_input = initial_parent_phrase # The first parent input
        conversation_history_for_gpt = [] # This accumulates history for generate_next_parent_turn

        for turn_number in range(1, MAX_CONVERSATION_TURNS + 1):
            logging.info(f"    Turn {turn_number}/{MAX_CONVERSATION_TURNS} - Parent: '{current_parent_input}'")

            try:
                caregiver_input_analysis = analyze_caregiver_input(current_parent_input, user_profile, current_session_context)
                logging.info(f"      Caregiver Input Analysis: Clarity: {caregiver_input_analysis.get('clarity')}, Tone: {caregiver_input_analysis.get('tone')}")

                candidate_responses = simulate_loop(current_parent_input, user_profile, current_session_context)

                if not candidate_responses:
                    logging.warning(f"      No candidate responses generated for Turn {turn_number}. Ending conversation early.")
                    break

                logging.info("      Reflecting on ALL Generated Options:")
                for i, option in enumerate(candidate_responses):
                    try:
                        option_for_reflection = {
                            "parent_input": current_parent_input,
                            "full_sentence": option.get("full_sentence", '[Missing Sentence]'),
                            "tiles": option.get("tiles", []),
                            "intent": option.get("intent", "unknown"),
                            "emotion": option.get("emotion", "neutral"),
                            "response_type": option.get("response_type", "unknown"),
                            "loop_score_estimate": option.get("loop_score_estimate", 0.0),
                        }
                        option["reflection"] = reflect_on_loop(
                            option_for_reflection,
                            user_profile,
                            current_session_context
                        )
                    except Exception as e:
                        logger.error(f"Failed to reflect on option {i+1} for turn {turn_number}: {e}", exc_info=True)
                        option["reflection"] = {
                            "emoji": "❌", "mood_summary": "Reflection Failed",
                            "communication_effectiveness": "N/A", "mood_mapping_detail": "Error during reflection generation.",
                            "reflection_analysis": str(e), "suggested_image_for_aac": "Error",
                            "suggested_action_for_caregiver": "Error", "improvement_opportunities": "Reflection could not be generated.",
                            "why_this_response": "Error", "what_user_feels": "Error", "what_user_needs": "Error",
                            "is_clear": False, "clarity_score": 0.0
                        }

                    logging.info(f"        Option {i+1}: \"{option.get('full_sentence', '[Missing Sentence]')}\" (Intent: {option.get('intent', 'unknown')}, Emotion: {option.get('emotion', 'unknown')}, Score: {option.get('loop_score_estimate', 0.0):.2f}) - Mood: {option['reflection'].get('mood_summary', 'N/A')} ({option['reflection'].get('communication_effectiveness', 'N/A')})")


                chosen_index, selection_reasoning = gpt_select_best_response(current_parent_input, candidate_responses, user_profile, current_session_context)
                chosen_response = candidate_responses[chosen_index]


                logging.info(f"      Chosen: Option {chosen_index + 1} → \"{chosen_response.get('full_sentence', '[Missing Sentence]')}\"")
                logging.info(f"        Why chosen response: {chosen_response.get('reflection', {}).get('why_this_response', 'N/A')}")
                logging.info(f"        User feels: {chosen_response.get('reflection', {}).get('what_user_feels', 'N/A')}")
                logging.info(f"        User needs: {chosen_response.get('reflection', {}).get('what_user_needs', 'N/A')}")


                rejected_count = 0
                for i, option in enumerate(candidate_responses):
                    if i != chosen_index:
                        if rejected_count == 0:
                            logging.info("      Rejected Options:")
                        logging.info(f"        ❌ Option {i+1}: \"{option.get('full_sentence', '[Missing Sentence]')}\"")
                        rejected_count += 1
                if rejected_count == 0 and len(candidate_responses) == 1:
                    logging.info("      No rejected options (only one candidate generated and chosen).")
                elif rejected_count == 0 and len(candidate_responses) > 1:
                    logging.warning("      No specific rejected options identified, but multiple candidates were present.")


                # Determine who initiates the next turn
                initiation_mode = detect_initiation_shift(chosen_response, user_profile, current_session_context)

                # Initialize variables for the next turn
                next_parent_prompt = ""
                updated_context_from_parent_turn_gen = current_session_context.copy() # Start with current context

                if initiation_mode == "child":
                    # Parent acknowledges child's lead and prompts for their question/topic
                    logger.info("--> Next Turn Initiation: CHILD. Parent will respond to child's lead.")
                    next_parent_prompt = f"Okay, you lead! What's next? What do you want to tell me or ask?"
                    # Context update is handled by the general update after consequence
                    
                elif initiation_mode == "pause":
                    logger.info("--> Next Turn Initiation: PAUSE. Child requested break or expressed strong negative emotion.")
                    next_parent_prompt = f"Okay, I understand. Let's take a break. What do you need right now?"
                    # Force context update to reflect the pause/calm down
                    updated_context_from_parent_turn_gen["environmental_factors"] = "transitioning to low-stimulation or quiet area"
                    updated_context_from_parent_turn_gen["physiological_state"] = "resting, calming down, or attending to need"
                    updated_context_from_parent_turn_gen["recent_antecedent_event"] = "communication break initiated by child"
                    updated_context_from_parent_turn_gen["child_mood_trend"] = "stabilizing or calming"

                elif initiation_mode == "parent":
                    logger.info("--> Next Turn Initiation: PARENT. Parent will generate the next prompt.")
                    next_parent_prompt_generated, updated_context_from_parent_turn_gen = generate_next_parent_turn(
                        chosen_response.get("full_sentence", '[Missing Sentence]'),
                        full_history=conversation_history_for_gpt, # Pass the accumulated history so far
                        user_profile=user_profile,
                        current_session_context=current_session_context # Pass the current context
                    )
                    next_parent_prompt = next_parent_prompt_generated

                # Generate consequence and suboptimal prediction using the determined next_parent_prompt
                consequence_data = generate_consequence(
                    current_parent_input,
                    chosen_response,
                    next_parent_prompt, # Use the determined next_parent_prompt
                    user_profile,
                    current_session_context
                )
                
                predicted_suboptimal_reaction = predict_emotional_transition(
                    chosen_response,
                    next_parent_prompt, # Use the determined next_parent_prompt
                    user_profile,
                    current_session_context
                )

                # Now that all turn_data is complete, structure it and append it to full_conversation_data
                turn_data = {
                    "turn_number": turn_number,
                    "initial_context": current_session_context.copy(),
                    "parent_input": current_parent_input,
                    "caregiver_input_analysis": caregiver_input_analysis,
                    "all_child_candidates": candidate_responses,
                    "chosen_response": chosen_response,
                    "chosen_response_index": chosen_index,
                    "selection_reasoning": selection_reasoning, # Empty dict as per requirement
                    "consequence_of_interaction": consequence_data,
                    "predicted_suboptimal_reaction": predicted_suboptimal_reaction,
                    "initiation_mode_for_next_turn": initiation_mode, # Save the decision
                    "next_parent_prompt_predicted": next_parent_prompt # Save what the parent will say next
                }
                # The updated_session_context from parent_turn_gen is specifically when Parent-LLM generates it.
                # If child or pause mode, we construct it manually, so use the one set above.
                turn_data["updated_session_context_from_parent_turn_gen"] = updated_context_from_parent_turn_gen.copy()
                full_conversation_data["conversation_turns"].append(turn_data)

                # Append this turn's structured data to the various JSONL training files
                append_training_data(full_conversation_data, turn_data)

                # Update conversation_history_for_gpt *after* all data for the current turn is collected.
                # Use OpenAI's standard roles directly here for simplicity and clarity.
                conversation_history_for_gpt.append({"speaker": "user", "text": current_parent_input}) # Parent's input is a user message
                conversation_history_for_gpt.append({"speaker": "assistant", "text": chosen_response.get("full_sentence", '[Missing Sentence]')}) # Child's response is an assistant message
                conversation_history_for_gpt.append({"speaker": "system_consequence", "text": consequence_data.get('consequence_analysis', '')}) # System observations can be part of user's context in history

                # Update the main session context for the *next* turn's processing
                current_session_context.update(updated_context_from_parent_turn_gen)
                logging.info(f"      Context Updated: Env: {current_session_context.get('environmental_factors')}, Phys: {current_session_context.get('physiological_state')}, Ante: {current_session_context.get('recent_antecedent_event')}, Mood Trend: {current_session_context.get('child_mood_trend', 'N/A')}")
                
                # Set up the parent input for the *next* iteration of the loop
                current_parent_input = next_parent_prompt

                # If the initiation mode for the *next* turn was 'pause', end the current conversation here.
                if initiation_mode == "pause":
                    logging.info(f"Conversation for session {session_id} ended early at turn {turn_number} due to 'pause' initiation mode.")
                    break # Exit the inner turn loop

                time.sleep(1.5) # Short pause before the next API call (between turns)

            except ConnectionError as e:
                logging.error(f"❌ API Connection Error during Turn {turn_number} for '{current_parent_input}' ({user_profile.get('profile_name', 'unknown profile')}) → {e}. Ending conversation early.", exc_info=True)
                break
            except Exception as e:
                logging.error(f"❌ Unhandled ERROR during Turn {turn_number} for '{current_parent_input}' ({user_profile.get('profile_name', 'unknown profile')}) → {e}. Ending conversation early.", exc_info=True)
                break

            time.sleep(1.0) # Pause between turns for readability and API rate limits (outer loop)

        # Check if conversation ended early for this specific session due to max turns not reached
        if len(full_conversation_data["conversation_turns"]) < MAX_CONVERSATION_TURNS and turn_number == MAX_CONVERSATION_TURNS:
             logging.warning(f"⚠️ Conversation ended early at turn {len(full_conversation_data['conversation_turns'])}/{MAX_CONVERSATION_TURNS} for session {session_id} - likely due to API error or no candidate responses.")


        try:
            final_multidisciplinary_summary = generate_final_aba_summary(full_conversation_data)
            full_conversation_data["final_reflection"] = final_multidisciplinary_summary
            logging.info("\n--- Final Multidisciplinary Summary for Session ---")
            logging.info(json.dumps(final_multidisciplinary_summary, indent=2))
            logging.info("-----------------------------------------------\n")
        except Exception as e:
            logging.error(f"❌ Failed to generate multidisciplinary summary for session {session_id}: {e}", exc_info=True)

        full_conversation_filename = os.path.join(output_dir, f"{session_id}_conversation.json")
        with open(full_conversation_filename, "w") as f:
            json.dump(full_conversation_data, f, indent=2)

        with open(TRAINING_DATA_FILES["full_conversations"], "a") as f:
            f.write(json.dumps(full_conversation_data) + "\n")

        logging.info(f"✅ Saved full conversation data for session {session_id}\n")
        time.sleep(2.0) # Pause before starting the next profile/conversation

logging.info("All data generation complete!")
