from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel, load_tool, tool
import datetime
import requests
import pytz
import yaml
from tools.final_answer import FinalAnswerTool

from Gradio_UI import GradioUI


@tool
def get_spotify_now_playing() -> str:
    """Fetches the currently playing song from Parker's Spotify account.
    Returns a formatted string with the song details or a message
    if nothing is playing.
    """
    try:
        response = requests.get(
            'https://prowe.ca/api/spotify/now-playing.json')
        response.raise_for_status()
        data = response.json()

        if data.get('isPlaying'):
            return (f"🎵 Now Playing: {data['title']}\n"
                    f"👤 Artist: {data['artist']}\n"
                    f"💿 Album: {data['album']}\n"
                    f"🔗 Listen on Spotify: {data['songUrl']}")
        else:
            return "Nothing is currently playing on Spotify."

    except requests.RequestException as e:
        return f"Error fetching Spotify data: {str(e)}"


@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """A tool that fetches the current local time in a specified timezone.
    Args:
        timezone: A string representing a valid timezone
        (e.g., 'America/New_York').
    """
    try:
        # Create timezone object
        tz = pytz.timezone(timezone)
        # Get current time in that timezone
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"The current local time in {timezone} is: {local_time}"
    except Exception as e:
        return f"Error fetching time for timezone '{timezone}': {str(e)}"


model = HfApiModel(
    max_tokens=2096,
    temperature=0.5,
    model_id='Qwen/Qwen2.5-Coder-32B-Instruct',
    custom_role_conversions=None,
)


# Import tool from Hub
image_generation_tool = load_tool(
    "agents-course/text-to-image", trust_remote_code=True)

with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)

agent = CodeAgent(
    model=model,
    # add your tools here (don't remove final_answer)
    tools=[FinalAnswerTool(), DuckDuckGoSearchTool(),
           get_spotify_now_playing],
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)


GradioUI(agent).launch()
