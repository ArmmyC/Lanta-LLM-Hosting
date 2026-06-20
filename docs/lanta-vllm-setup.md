# Lanta vLLM Setup

The supported scripts live in `lanta/scripts/`.

Download a model:

```bash
bash scripts/download-model.sh Qwen/Qwen3.6-27B Qwen3.6-27B
```

Submit a configured preset:

```bash
bash scripts/submit-preset.sh qwen36-27b
```

Inspect the queue and logs:

```bash
squeue -u ub127
tail -f logs/vllm-<job-id>.out
```

Qwen 3.5/3.6 presets enable the `qwen3` reasoning parser. Submission exports
all model settings explicitly to the Slurm job.
