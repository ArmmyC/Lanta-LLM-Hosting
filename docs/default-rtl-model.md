# Default RTL Model

## Decision

Use `qwen36-27b` as the default daily model for RTL, Verilog, and SystemVerilog work.

This is a recommendation for general functional RTL generation. It is not a claim that the model produces the best final silicon power, performance, or area.

## Benchmark Evidence

The decision is based on the registered public functional RTL results in RLT-Benchmark Baseline v0.1:

| Functional benchmark | qwen36-27b | qwen36-35b-a3b |
|---|---:|---:|
| VerilogEval v2 pass@1 | 0.6154 | 0.5705 |
| VerilogEval v2 pass@5 | 0.7756 | 0.7308 |
| RTLLM 2.0 pass@1 | 0.6000 | 0.6000 |

The registered runs used matched settings within each benchmark mode. On this evidence, `qwen36-27b` is the strongest overall functional RTL generation baseline and remains the quality reference for daily work.

Source: [ArmmyC/RLTBench](https://github.com/ArmmyC/RLTBench).

## Alternatives

- `qwen36-35b-a3b` is the secondary practical serving candidate when GPU memory, throughput, or long-context serving stability matters more than the small functional benchmark gap.
- `deepseek-coder-v2-lite` remains useful for RTL-OPT equivalence comparison. It had the highest registered RTL-OPT equivalence pass rate, but that specialized result does not make it the default general RTL generator.
- `qwen3-coder-30b-a3b` and `qwen25-coder-32b` remain available for comparison and workload-specific testing.

## Serving Contract

Only one model is served by vLLM on port `8000` at a time. The local vLLM endpoint remains stable across swaps:

```text
http://127.0.0.1:8000/v1
```

OpenWebUI and normal API clients should continue using the LiteLLM alias:

```text
active-lanta-model
```

The alias is backed by `qwen36-27b` by default, but it must remain swappable. After changing the served model, update `VLLM_MODEL_ID` when necessary; do not hardcode clients to a backend model name.

## Daily Operational Checklist

1. Start the default preset:

   ```powershell
   ssh lanta "cd /project/zz992000-zdevb/zz992005/ub127/SiliconCraft && bash scripts/submit-preset.sh qwen36-27b"
   ```

2. Restart or check the local tunnel if needed:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\windows\tunnel\start-lanta-vllm-tunnel.ps1
   powershell -ExecutionPolicy Bypass -File .\windows\tunnel\status-lanta-vllm-tunnel.ps1
   ```

3. Confirm the active model:

   ```powershell
   curl.exe http://127.0.0.1:8000/v1/models
   ```

4. Run a tiny RTL smoke prompt:

   ```powershell
   curl.exe http://127.0.0.1:8000/v1/chat/completions `
     -H "Content-Type: application/json" `
     -d '{"model":"qwen36-27b","messages":[{"role":"user","content":"Return only synthesizable SystemVerilog for module rtl_smoke(input logic a, b, output logic y); assign y = a & b."}],"temperature":0,"max_tokens":128}'
   ```

5. Use OpenWebUI or the API normally. Clients should keep using `active-lanta-model` through LiteLLM.
