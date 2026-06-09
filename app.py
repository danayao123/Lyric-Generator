"""
app.py
Streamlit UI for the R&B Lyric Generator.
Supports English, Chinese, and Bilingual modes.

Run with:
    streamlit run app.py
"""

import streamlit as st
from dotenv import load_dotenv
from lyric_generator import generate_lyrics

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="R&B Lyric Generator",
    page_icon="🎵",
    layout="centered",
)

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🎵 R&B Lyric Generator")
st.caption("Powered by GPT-4 · Double rhyme & Triple rhyme · 双押 & 三押")

st.divider()

# ── Language selector ──────────────────────────────────────────────────────────
language = st.radio(
    "Language / 语言",
    options=["English", "中文", "双语 Bilingual"],
    horizontal=True,
    help="Choose the language for the generated lyrics.",
)

st.divider()

# ── Inputs ─────────────────────────────────────────────────────────────────────
title_label = "Song Title / 歌曲名 *" if language != "English" else "Song Title *"
title_placeholder = {
    "English": "e.g. Midnight Feelings",
    "中文": "例如：午夜心情",
    "双语 Bilingual": "e.g. Midnight Feelings / 午夜心情",
}[language]

song_title = st.text_input(
    title_label,
    placeholder=title_placeholder,
    help="Required. This becomes the emotional anchor of the song.",
)

col1, col2 = st.columns(2)

with col1:
    rhyme_placeholder = {
        "English": "e.g. forever, together, night",
        "中文": "例如：情、命、定（-ing韵）",
        "双语 Bilingual": "e.g. forever / 永远 (-ing/-uan)",
    }[language]
    rhyme_label = "Rhyme Words / 押韵词 (optional)" if language != "English" else "Rhyme Words / Sounds (optional)"

    rhyme_words = st.text_input(
        rhyme_label,
        placeholder=rhyme_placeholder,
        help="Words or syllable sounds you want rhymed. For Chinese, you can specify 韵母 like -ing, -an, -ao.",
    )

with col2:
    temperature = st.slider(
        "Creativity / 创意度",
        min_value=0.5,
        max_value=1.0,
        value=0.85,
        step=0.05,
        help="Higher = more creative. Lower = more predictable.",
    )

template_placeholder = {
    "English": (
        "e.g. The song is about losing someone you love but still seeing them in everyday things. "
        "Chorus should feel like a release. Bridge should be reflective."
    ),
    "中文": "例如：这首歌讲述在雨天思念旧爱，副歌情绪爆发，桥段回归平静。",
    "双语 Bilingual": (
        "e.g. Rainy night, missing someone who left. "
        "Chorus is an emotional climax. Bridge is quiet and introspective. / "
        "雨夜思念离开的人，副歌情绪爆发，桥段回归平静。"
    ),
}[language]

lyric_template = st.text_area(
    "Lyric Template / Theme Hints (optional)" if language != "中文" else "主题/结构提示（选填）",
    placeholder=template_placeholder,
    height=120,
    help="Describe the theme, mood, or paste a rough structural outline.",
)

st.divider()

# ── Generate button ────────────────────────────────────────────────────────────
btn_label = {
    "English": "✨ Generate Lyrics",
    "中文": "✨ 生成歌词",
    "双语 Bilingual": "✨ Generate / 生成双语歌词",
}[language]

generate_clicked = st.button(
    btn_label,
    type="primary",
    disabled=not song_title.strip(),
    use_container_width=True,
)

if not song_title.strip():
    hint = "Enter a song title to get started." if language == "English" else "请输入歌曲名称。"
    st.info(hint)

# ── Generation & output ────────────────────────────────────────────────────────
if generate_clicked and song_title.strip():
    spinner_msg = {
        "English": "Writing your lyrics…",
        "中文": "正在创作歌词…",
        "双语 Bilingual": "Writing bilingual lyrics… 正在创作双语歌词…",
    }[language]

    with st.spinner(spinner_msg):
        try:
            lyrics = generate_lyrics(
                title=song_title.strip(),
                rhyme_words=rhyme_words.strip(),
                template=lyric_template.strip(),
                language=language,
                temperature=temperature,
            )

            success_msg = {
                "English": "Lyrics generated!",
                "中文": "歌词生成完成！",
                "双语 Bilingual": "Bilingual lyrics generated! / 双语歌词生成完成！",
            }[language]
            st.success(success_msg)
            st.divider()

            st.subheader(f'"{song_title}"')

            # For bilingual, split and show in two tabs
            if language == "双语 Bilingual" and "── 中文版 ──" in lyrics:
                parts = lyrics.split("── 中文版 ──", 1)
                tab_en, tab_zh = st.tabs(["🇬🇧 English", "🇨🇳 中文"])
                with tab_en:
                    st.markdown(
                        f"<pre style='white-space: pre-wrap; font-family: Georgia, serif; "
                        f"font-size: 15px; line-height: 1.9;'>{parts[0].strip()}</pre>",
                        unsafe_allow_html=True,
                    )
                with tab_zh:
                    st.markdown(
                        f"<pre style='white-space: pre-wrap; font-family: PingFang SC, Microsoft YaHei, serif; "
                        f"font-size: 15px; line-height: 1.9;'>{parts[1].strip()}</pre>",
                        unsafe_allow_html=True,
                    )
            else:
                font = (
                    "PingFang SC, Microsoft YaHei, serif"
                    if language == "中文"
                    else "Georgia, serif"
                )
                st.markdown(
                    f"<pre style='white-space: pre-wrap; font-family: {font}; "
                    f"font-size: 15px; line-height: 1.9;'>{lyrics}</pre>",
                    unsafe_allow_html=True,
                )

            st.divider()
            with st.expander("📋 Copy raw text / 复制原文"):
                st.code(lyrics, language=None)

        except ValueError as e:
            st.error(f"Configuration error: {e}")
        except Exception as e:
            st.error(f"Something went wrong: {e}")

# ── Sidebar legend ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📖 Legend / 说明")

    st.markdown("### 🇬🇧 English")
    st.markdown(
        """
**`(DR)`** — Double Rhyme
Last **2 syllables** rhyme across lines.
> *"I've been wait**-ING** / heart is break**-ING**"*

**`(TR)`** — Triple Rhyme
Last **3 syllables** rhyme across lines.
> *"I can't be-**LIEVE it** / hard to con-**CEIVE it**"*
        """
    )

    st.divider()

    st.markdown("### 🇨🇳 中文")
    st.markdown(
        """
**`（双押）`** — 双押
一句歌词中有 **2个** 押韵点，基于**韵母**相同或相近。
> *「让我心**疼**(-eng) / 刻骨铭**心**(-ing)」*

**`（三押）`** — 三押
一句或连续三行末尾使用**相同韵母**。
> *「声**音**(-in) / 门**庭**(-ing) / 这份**情**(-ing)」*

常见押韵组合：
- `-ing / -in / -eng` 互押
- `-an / -ian / -uan` 互押
- `-ao / -iao` 互押
        """
    )

    st.divider()
    st.markdown("**Tips:**")
    st.markdown(
        "- 双语模式会生成完整英文版 + 完整中文版\n"
        "- 押韵词可以输入韵母，例如 `-ing` 或 `-an`\n"
        "- 调高创意度可得到更意外的押韵"
    )
    st.divider()
    st.caption("Built with Streamlit + OpenAI GPT-4")
