"""
lyric_generator.py
Core logic for generating R&B lyrics with double/triple rhyme using Google Gemini.
Supports English, Chinese, and Bilingual modes.
"""

from google import genai
import os


# ── System prompts ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT_EN = """You are an expert R&B songwriter specializing in double rhyme and triple rhyme schemes.

RHYME DEFINITIONS:
- Double rhyme (DR): the last TWO syllables of a line rhyme with the last two syllables of another line.
  Example: "I've been wait-ING / heart is break-ING"
- Triple rhyme (TR): the last THREE syllables of a line rhyme with the last three syllables of another line.
  Example: "I can't be-LIEVE it / hard to con-CEIVE it"

RULES:
1. Every verse and chorus must contain at least one double rhyme or triple rhyme pair.
2. Prioritize triple rhymes in the chorus for emotional punch.
3. Write in a smooth, soulful R&B style — emotive, intimate, and melodic.
4. Structure: [Verse 1] → [Pre-Chorus] → [Chorus] → [Verse 2] → [Pre-Chorus] → [Chorus] → [Bridge] → [Chorus (Outro)]
5. Label each section clearly.
6. Mark double rhymes with (DR) and triple rhymes with (TR) at the end of the rhyming lines.
"""

SYSTEM_PROMPT_ZH = """你是一位专精中文R&B歌词创作的词人，擅长双押和三押技巧。

押韵定义（基于汉语拼音韵母）：
- 双押：一句歌词中出现 2 个押韵点，可以是句内押韵 + 句尾押韵，或连续两行的行尾韵脚相同。
  例：「你的眼神让我心疼（-eng）/ 那段记忆刻骨铭心（-ing）」
- 三押：一句歌词中出现 3 个押韵点，或连续三行行尾使用相同韵母。
  例：「想念你的声音（-ing）/ 徘徊在你门庭（-ing）/ 爱你没有理由放弃这份情（-ing）」

押韵规则：
1. 押韵基于韵母相同或相近（如 -ing/-eng 可互押，-an/-ian/-uan 可互押）。
2. 每个段落（主歌、副歌、桥段）都必须包含双押或三押。
3. 副歌优先使用三押，情感要强烈。
4. 风格：流畅、感性、R&B腔调，语言口语化且有画面感。
5. 结构：[主歌一] → [预副歌] → [副歌] → [主歌二] → [预副歌] → [副歌] → [桥段] → [副歌（尾声）]
6. 在押韵的行末标注（双押）或（三押）。
"""

SYSTEM_PROMPT_BILINGUAL = """You are an expert bilingual R&B songwriter fluent in both English and Chinese.
You specialize in double rhyme and triple rhyme in BOTH languages.

ENGLISH RHYME DEFINITIONS:
- Double rhyme (DR): last TWO syllables rhyme across lines. E.g. "wait-ING / break-ING"
- Triple rhyme (TR): last THREE syllables rhyme across lines. E.g. "be-LIEVE it / con-CEIVE it"

CHINESE RHYME DEFINITIONS (based on 韵母):
- 双押: 2 rhyme points in one line or consecutive lines sharing the same 韵母.
- 三押: 3 rhyme points, e.g. three line-endings all using -ing finals.

OUTPUT FORMAT — write the song TWICE:
1. Full English version with sections labelled [Verse 1], [Chorus], etc. Mark rhymes with (DR) / (TR).
2. A separator line: ── 中文版 ──
3. Full Chinese version with sections labelled [主歌一], [副歌], etc. Mark rhymes with（双押）/（三押）.

Both versions share the same theme and emotional arc, written in a smooth, soulful R&B style.
Structure: Verse 1 → Pre-Chorus → Chorus → Verse 2 → Pre-Chorus → Chorus → Bridge → Outro Chorus
"""


# ── Prompt builders ────────────────────────────────────────────────────────────

def get_system_prompt(language: str) -> str:
    return {
        "English": SYSTEM_PROMPT_EN,
        "中文": SYSTEM_PROMPT_ZH,
        "双语 Bilingual": SYSTEM_PROMPT_BILINGUAL,
    }[language]


def build_user_prompt(
    title: str,
    rhyme_words: str = "",
    template: str = "",
    language: str = "English",
) -> str:
    if language == "中文":
        parts = [f'请为一首名为《{title}》的R&B歌曲创作完整歌词。']
        if rhyme_words.strip():
            parts.append(f"请押以下文字/韵母的韵：{rhyme_words}。")
        if template.strip():
            parts.append(f"主题/结构提示：\n{template}")
        parts.append("每个段落都必须包含双押或三押，并在行末标注（双押）或（三押）。")
    elif language == "双语 Bilingual":
        parts = [f'Write complete bilingual R&B lyrics for a song titled "{title}" / 《{title}》.']
        if rhyme_words.strip():
            parts.append(f"Incorporate rhymes with: {rhyme_words}.")
        if template.strip():
            parts.append(f"Theme / structure hints:\n{template}")
        parts.append(
            "Write the full English version first, then the separator ── 中文版 ──, "
            "then the full Chinese version. Label all rhymes."
        )
    else:
        parts = [f'Write complete R&B lyrics for a song titled "{title}".']
        if rhyme_words.strip():
            parts.append(f"Incorporate or rhyme with: {rhyme_words}.")
        if template.strip():
            parts.append(f"Structure / theme hints:\n{template}")
        parts.append(
            "Ensure most sections contain double rhyme (DR) or triple rhyme (TR), labelled inline."
        )

    return "\n\n".join(parts)


# ── Main generation function ───────────────────────────────────────────────────

def generate_lyrics(
    title: str,
    rhyme_words: str = "",
    template: str = "",
    language: str = "English",
    model: str = "gemini-2.0-flash-lite",
    temperature: float = 0.85,
) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")

    client = genai.Client(api_key=api_key)

    # Combine system prompt + user prompt into one message (works across all API versions)
    full_prompt = (
        get_system_prompt(language)
        + "\n\n---\n\n"
        + build_user_prompt(title, rhyme_words, template, language)
    )

    response = client.models.generate_content(
        model=model,
        contents=full_prompt,
    )

    return response.text