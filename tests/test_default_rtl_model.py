from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRESETS = (
    "qwen36-27b",
    "qwen36-35b-a3b",
    "qwen3-coder-30b-a3b",
    "qwen25-coder-32b",
    "deepseek-coder-v2-lite",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_qwen36_27b_is_the_documented_and_configured_default() -> None:
    decision = read("docs/default-rtl-model.md")
    preset_script = read("lanta/scripts/submit-preset.sh")
    swap_guide = read("HOW_TO_SWAP.md")

    assert "Use `qwen36-27b` as the default daily model" in decision
    assert "http://127.0.0.1:8000/v1" in decision
    assert "Only one model is served" in decision
    assert 'const DEFAULT_MODEL = "qwen36-27b"' in read("cli/qwen-chat-cli.mjs")
    assert "VLLM_MODEL_ID=openai/qwen36-27b" in read("litellm/.env.example")
    assert "active-lanta-model" in read("litellm/config.yaml")
    for preset in PRESETS:
        assert f"  {preset})" in preset_script
        assert preset in swap_guide
