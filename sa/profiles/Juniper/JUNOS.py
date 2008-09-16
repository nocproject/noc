from noc.sa.profiles import BaseProfile

class Profile(BaseProfile):
    pattern_prompt="^({master}\n)?\S*>"
    pattern_more=r"^---\(more.*?\)---"
    command_more=" "