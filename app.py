# Pollinations BYOP Demo - Hugging Face Space
# QUEST #17249: A Hugging Face Space people duplicate to build with Pollinations

import os
import gradio as gr
import requests
import json

# Pollinations API endpoint
POLLINATIONS_API = "https://gen.pollinations.ai"

def get_models():
    """Fetch available models from Pollinations."""
    try:
        resp = requests.get(f"{POLLINATIONS_API}/v1/models?source=official&limit=20", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return [m.get('id') for m in data.get('data', [])]
    except Exception as e:
        print(f"Error fetching models: {e}")
    return [
        "openai/gpt-5.4-nano",
        "black-forest-labs/flux.1-schnell", 
        "openai/tts-1",
        "google/veo-3.1-fast"
    ]

def generate_text(prompt, model, api_key):
    """Generate text using Pollinations."""
    if not api_key:
        return "Error: Please enter your Pollinations API key (sk_...)"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        resp = requests.post(
            f"{POLLINATIONS_API}/v1/chat/completions",
            headers=headers,
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            },
            timeout=30
        )
        if resp.status_code == 200:
            data = resp.json()
            return data['choices'][0]['message']['content']
        else:
            err = resp.json()
            return f"Error: {err.get('error', {}).get('message', 'Unknown error')}"
    except Exception as e:
        return f"Request failed: {str(e)}"

def generate_image(prompt, model, api_key):
    """Generate image using Pollinations."""
    if not api_key:
        return None, "Error: Please enter your Pollinations API key (sk_...)"
    
    try:
        encoded = requests.utils.quote(prompt)
        url = f"{POLLINATIONS_API}/image/{encoded}?model={model}&key={api_key}"
        resp = requests.get(url, timeout=60)
        
        if resp.status_code == 200:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f:
                f.write(resp.content)
                return f.name, "Image generated!"
        else:
            err = resp.json()
            return None, f"Error: {err.get('error', {}).get('message', 'Unknown error')}"
    except Exception as e:
        return None, f"Request failed: {str(e)}"

def generate_audio(text, model, voice, api_key):
    """Generate audio using Pollinations."""
    if not api_key:
        return None, "Error: Please enter your Pollinations API key (sk_...)"
    
    try:
        encoded = requests.utils.quote(text)
        url = f"{POLLINATIONS_API}/audio/{encoded}?model={model}&voice={voice}&key={api_key}"
        resp = requests.get(url, timeout=30)
        
        if resp.status_code == 200:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                f.write(resp.content)
                return f.name, "Audio generated!"
        else:
            err = resp.json()
            return None, f"Error: {err.get('error', {}).get('message', 'Unknown error')}"
    except Exception as e:
        return None, f"Request failed: {str(e)}"

def check_balance(api_key):
    """Check Pollinations balance."""
    if not api_key:
        return "Error: Please enter your Pollinations API key (sk_...)"
    
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        resp = requests.get(f"{POLLINATIONS_API}/account/balance", headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return f"Balance: {data.get('balance', 0)} Pollen | Account: {data.get('accountBalance', {}).get('total', 0)} total"
        else:
            return f"Error: {resp.status_code}"
    except Exception as e:
        return f"Request failed: {str(e)}"

# Gradio Interface
with gr.Blocks(title="Pollinations BYOP Demo", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # Pollinations BYOP Demo
    **QUEST #17249** - A Hugging Face Space people duplicate to build with Pollinations
    
    This Space demonstrates **Bring Your Own Pollen (BYOP)** - users sign in and pay with their own Pollen.
    
    ### How to use:
    1. Get a Pollinations API key from [enter.pollinations.ai/keys](https://enter.pollinations.ai/keys)
    2. Enter your key below (starts with sk_...)
    3. Try text, image, and audio generation!
    
    ---
    **Built for Pollinations QUEST #17249** - Duplicate this Space and make it your own!
    """)
    
    with gr.Row():
        api_key = gr.Textbox(
            label="Pollinations API Key (sk_...)",
            type="password",
            placeholder="sk_xxxxxxxxxxxxxxxx",
            info="Get yours at enter.pollinations.ai/keys"
        )
        balance_btn = gr.Button("Check Balance", variant="secondary")
        balance_out = gr.Textbox(label="Balance", interactive=False)
    
    balance_btn.click(check_balance, inputs=[api_key], outputs=[balance_out])
    
    gr.Markdown("---")
    
    with gr.Tab("Text Generation"):
        text_model = gr.Dropdown(
            choices=[m for m in get_models() if 'text' in m.lower() or 'gpt' in m.lower() or 'claude' in m.lower() or 'gemini' in m.lower() or 'llama' in m.lower() or 'mistral' in m.lower() or 'qwen' in m.lower()],
            value="openai/gpt-5.4-nano",
            label="Model"
        )
        text_prompt = gr.Textbox(
            label="Prompt",
            placeholder="Write a haiku about AI",
            lines=3
        )
        text_btn = gr.Button("Generate Text", variant="primary")
        text_out = gr.Textbox(label="Result", lines=10, interactive=False)
        text_btn.click(generate_text, inputs=[text_prompt, text_model, api_key], outputs=[text_out])
    
    with gr.Tab("Image Generation"):
        image_model = gr.Dropdown(
            choices=[m for m in get_models() if 'flux' in m.lower() or 'image' in m.lower() or 'dall' in m.lower() or 'gpt-image' in m.lower() or 'ideogram' in m.lower() or 'recraft' in m.lower()],
            value="black-forest-labs/flux.1-schnell",
            label="Model"
        )
        image_prompt = gr.Textbox(
            label="Prompt",
            placeholder="A cyberpunk city at sunset, neon lights, rain",
            lines=2
        )
        image_btn = gr.Button("Generate Image", variant="primary")
        image_out = gr.Image(label="Result")
        image_status = gr.Textbox(label="Status", interactive=False)
        image_btn.click(generate_image, inputs=[image_prompt, image_model, api_key], outputs=[image_out, image_status])
    
    with gr.Tab("Audio Generation"):
        audio_model = gr.Dropdown(
            choices=["openai/tts-1", "openai/tts-1-hd", "elevenlabs/eleven-flash-v2.5", "microsoft/mai-voice-2.1-flash"],
            value="openai/tts-1",
            label="Model"
        )
        audio_voice = gr.Dropdown(
            choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
            value="nova",
            label="Voice"
        )
        audio_text = gr.Textbox(
            label="Text to speak",
            placeholder="Hello! This is a demo of Pollinations audio generation.",
            lines=3
        )
        audio_btn = gr.Button("Generate Audio", variant="primary")
        audio_out = gr.Audio(label="Result", type="filepath")
        audio_status = gr.Textbox(label="Status", interactive=False)
        audio_btn.click(generate_audio, inputs=[audio_text, audio_model, audio_voice, api_key], outputs=[audio_out, audio_status])
    
    gr.Markdown("""
    ---
    ## Duplicate This Space
    
    Click **Duplicate this Space** (top right) to create your own copy!
    
    Then customize:
    - Add your own App Key for BYOP OAuth flow
    - Build your own demo (voice character, comic generator, narrated images, etc.)
    - Add MCP server mode for agent integration
    
    ## Resources
    - [Pollinations API Docs](https://gen.pollinations.ai/docs)
    - [BYOP Guide](https://github.com/pollinations/pollinations/blob/main/BRING_YOUR_OWN_POLLEN.md)
    - [Model Lists](https://gen.pollinations.ai/v1/models)
    - [Quest #17249](https://github.com/pollinations/pollinations/issues/17249)
    """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)