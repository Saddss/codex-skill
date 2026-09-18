---
name: perf-analysis
description: >
  Performance analysis coordination workflow. Guides profiling delegation,
  bottleneck classification (compute / memory / launch / communication / sync),
  and structured report generation. Use when the user asks to analyze
  performance, profile a workload, check MFU / SOL, diagnose bottlenecks,
  understand why a vLLM / SGLang / TRT-LLM serve / lmdeploy run is slower
  than expected, or interpret an existing .nsys-rep against an SLO. Triggers
  also include "分析性能瓶颈" / "MFU 多少" / "瓶颈是 compute 还是 memory" /
  "诊断推理慢"
license: Apache-2.0
metadata:
  tags: [analysis, profiling, bottleneck]
  author: NVIDIA Corporation
  upstream: https://github.com/NVIDIA/TensorRT-LLM/tree/main/.claude/skills/perf-analysis
  adapted_for: Codex global skills (capability-based profiling; task-scoped reports)
---

> **Adapted from [NVIDIA/TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM/tree/main/.claude/skills/perf-analysis) under Apache-2.0.** Uses capability-based profiling and task-scoped reports. NVIDIA's copyright + license header is preserved in this fork's `LICENSE-Apache-2.0.txt`.
>
> **In this fork "delegate to perf-profiling-specialist" means: delegate to `perf-nsight-systems` for nsys timeline work, `perf-nsight-compute-analysis` for ncu kernel analysis, or `model-perf-binary-search` for QPS-vs-SLO binary search.**

# Performance Analysis

## Principles

1. **Use available profiling capabilities.** Read the relevant tool skill and run measurements directly, or delegate when an appropriate subagent is available and authorized. Specialist names in this document identify responsibilities, not required installed agents; routing examples also apply to direct execution.
2. **Metrics from tools, never invented.** All performance numbers must come
   from profiling tool output. Never fabricate metrics.
3. **Classify before recommending.** Identify the bottleneck type before
   suggesting optimizations. The wrong classification leads to wasted effort.
4. **Task-scoped reports.** Present requested metrics and evidence-backed findings. Include recommendations only when requested or needed to answer the question; do not apply optimizations during a diagnosis-only task.

## Key Performance Metrics

- **Throughput**: samples/sec, tokens/sec, iterations/sec
- **Latency**: end-to-end time, kernel time, communication time
- **MFU (Model FLOPs Utilization)**: actual FLOPs / theoretical peak FLOPs
- **% of SOL (Speed of Light)**: current perf / hardware peak perf
- **GPU Utilization**: SM occupancy, tensor core usage
- **Memory Bandwidth**: DRAM bandwidth utilization vs peak

## Analysis Workflow

1. **Understand**: Clarify what metrics the user needs (MFU, SOL, latency, etc.)
2. **Plan**: Plan your profiling and analysis steps before starting
3. **Profile**: Delegate to **perf-profiling-specialist** for actual measurements
4. **Measure**: Extract requested metrics from profiling results
5. **Classify**: If diagnosing issues, determine primary bottleneck type
6. **Report**: Generate performance analysis report with findings

## Bottleneck Classification

When diagnosing performance issues, classify the primary bottleneck:

| Type | Indicator | Description |
|------|-----------|-------------|
| **Compute-bound** | High GPU utilization, low memory bandwidth usage | Limited by compute capacity (FLOPs) |
| **Memory-bound** | High memory bandwidth, low compute utilization | Limited by DRAM throughput |
| **Launch-overhead** | Many small kernels, high CPU time | CPU becoming bottleneck from kernel launch overhead |
| **Communication-bound** | Significant time in collective operations | Limited by inter-GPU or inter-node communication |
| **Sync-bound** | Excessive CPU-GPU synchronization points | Stalls from unnecessary synchronization |

## Delegation Guidelines

When delegating to specialists, describe the **desired outcome** -- not the
tool methodology.

**DO include:**
- The workload: file path, code snippet, or command to profile
- Problem context: dimensions, dtypes, FLOPs calculations, batch sizes
- Desired metrics: SOL%, MFU, throughput, occupancy, bottleneck classification
- Any constraints: specific kernel to target, profiling region markers

**DO NOT include:**
- Specific tool flags or command patterns (e.g., `--set=full`, `--section SpeedOfLight`)
- Step-by-step tool usage instructions
- Fallback strategies for tool failures
- Example commands
- Unrelated artifact locations; provide the user's required output directory and resource boundaries

Specialists have their own skills that encode best practices for tool usage
and their own workspace artifacts for output. Prescribing commands in the
delegation overrides their skills and may lead to suboptimal profiling
strategies (e.g., collecting 8000+ metrics with `--set=full` when a targeted
section analysis would be faster and more surgical).

### Good Example

```
Profile the batched GEMM kernel in bmm_workload.py with NCU.
The workload uses cudaProfilerStart/Stop markers to isolate the region of interest.
Collect kernel-level metrics: SOL%, compute/memory throughput, DRAM bandwidth,
tensor core utilization, occupancy, warp stall reasons, and roofline classification.
The batched GEMM performs 68.72 GFLOP per call (B=32, M=512, N=1024, K=2048, FP16).
Calculate MFU against the GPU's peak FP16 tensor core TFLOP/s.
```

### Bad Example

```
Run NCU with --set=full --profile-from-start off --target-processes all.
If --set=full fails, try --set=detailed. Parse the CSV output for
sm__throughput.avg.pct_of_peak_sustained_elapsed.
Save raw NCU output to /workspace/.../ncu_output.txt.
```

### Remote Profiling

When profiling on a remote SLURM cluster, include the
**Remote Execution Context** block in the delegation prompt with the SSH+srun
wrapper for the target cluster. The perf-profiling-specialist will prefix its
commands (nsys, ncu, nvidia-smi) with this wrapper.

The perf-profiling-specialist does not need the `remote-slurm` skill — the
context block provides everything it needs to execute remotely.

## Available Specialists

Delegate profiling and domain-specific analysis to these specialists:

- **perf-profiling-specialist**: Runs nvidia-smi, nsys, ncu, torch.profiler. Use for ALL profiling tasks.
- **perf-torch-cuda-graph-specialist**: Analyzes CUDA Graph compatibility and applies capture workflows

## Report Format

Report the requested metrics with measurement conditions and source artifacts. Put technical context beside each finding and disclose unmeasured behavior. Follow the user's presentation requirements; the example below is illustrative and does not require summary sections or a separate document.

### Example Report

```
## Summary
Training at 42% MFU, memory-bound due to large attention tensors.

## Metrics
- Throughput: 1,247 samples/sec
- MFU: 42% (vs 65% theoretical for this model)
- % of SOL: 58% (room for 1.7x improvement)
- GPU Utilization: 45%
- Memory Bandwidth: 850 GB/s (89% of peak)
- Kernel Count: 1,247 per iteration

## Findings
1. Self-attention consumes 60% of memory bandwidth
2. Optimizer step has 3 unnecessary synchronizations
3. Batch size could be increased by 2x

## Recommendations
1. Enable FlashAttention (expected: +15% MFU)
2. Remove synchronizations in optimizer (expected: +5% throughput)
3. Increase batch size to improve GPU utilization
```
