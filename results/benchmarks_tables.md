# Benchmark tables (generated 2026-10-27 13:34)

## PGxQA subsets (dataset/PGxQA/pgxqa_eval.jsonl)

| metric | phase15 | phase13 | plain_rag | clinpgx_only | llm_only | amg_rag | medrag | imedrag | paperqa2 | paperqa2_fixed | paperqa2_fixed_clinpgx | lightrag | gpt4o | gpt4turbo | llama3_70b | gpt35 | gemini | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| consult:BERTScore-F1 | 0.171 | 0.174 | 0.163 | 0.147 | 0.165 | 0.128 | 0.105 | 0.179 | 0.139 | 0.167 | 0.144 | 0.074 | - | - | - | - | - | 9 |
| d2g:F1 | 0.701 | 0.745 | 0.792 | 0.803 | 0.367 | 0.333 | 0.483 | 0.542 | 0.528 | 0.589 | 0.599 | 0.387 | 0.733 | 0.607 | 0.656 | 0.424 | 0.370 | 20 |
| d2g:P | 0.689 | 0.739 | 0.792 | 0.812 | 0.350 | 0.300 | 0.500 | 0.542 | 0.504 | 0.543 | 0.568 | 0.296 | 0.725 | 0.592 | 0.617 | 0.339 | 0.321 | 20 |
| d2g:R | 0.850 | 0.850 | 0.850 | 0.850 | 0.400 | 0.400 | 0.475 | 0.575 | 0.625 | 0.775 | 0.700 | 0.600 | 0.775 | 0.700 | 0.800 | 0.700 | 0.500 | 20 |
| g2d:F1 | 0.576 | 0.538 | 0.597 | 0.592 | 0.108 | 0.155 | 0.070 | 0.322 | 0.230 | 0.535 | 0.259 | 0.340 | 0.572 | 0.444 | 0.541 | 0.186 | 0.077 | 20 |
| g2d:P | 0.711 | 0.658 | 0.783 | 0.779 | 0.150 | 0.250 | 0.100 | 0.425 | 0.325 | 0.667 | 0.385 | 0.372 | 0.603 | 0.453 | 0.561 | 0.172 | 0.076 | 20 |
| g2d:R | 0.600 | 0.602 | 0.607 | 0.581 | 0.104 | 0.138 | 0.062 | 0.316 | 0.206 | 0.516 | 0.212 | 0.348 | 0.610 | 0.562 | 0.617 | 0.258 | 0.083 | 20 |
| refusal(misspecified):extended | 0.429 | 0.286 | 0.000 | 0.286 | 0.571 | 0.571 | 0.857 | 0.714 | 0.857 | 0.714 | 0.714 | 0.857 | 1.000 | 1.000 | 0.429 | 0.857 | 0.286 | 7 |
| refusal(misspecified):pgxqa | 0.143 | 0.143 | 0.000 | 0.143 | 0.286 | 0.286 | 0.857 | 0.714 | 0.286 | 0.286 | 0.714 | 0.857 | 1.000 | 1.000 | 0.429 | 0.857 | 0.286 | 7 |
| refusal(well-specified):extended | 0.125 | 0.125 | 0.100 | 0.100 | 0.325 | 0.475 | 0.850 | 0.500 | 0.550 | 0.250 | 0.375 | 0.575 | 0.200 | 0.325 | 0.050 | 0.575 | 0.150 | 40 |
| refusal(well-specified):pgxqa | 0.050 | 0.025 | 0.025 | 0.075 | 0.275 | 0.375 | 0.850 | 0.500 | 0.300 | 0.225 | 0.350 | 0.575 | 0.200 | 0.325 | 0.050 | 0.575 | 0.150 | 40 |
| refusal_d2g:F1 | 0.591 | 0.646 | 0.667 | 0.665 | 0.470 | 0.335 | 0.193 | 0.493 | 0.487 | 0.682 | 0.557 | 0.455 | 0.759 | 0.465 | 0.641 | 0.351 | 0.252 | 18 |
| refusal_d2g:P | 0.550 | 0.602 | 0.634 | 0.676 | 0.435 | 0.292 | 0.194 | 0.486 | 0.444 | 0.625 | 0.512 | 0.373 | 0.731 | 0.449 | 0.606 | 0.281 | 0.275 | 18 |
| refusal_d2g:R | 0.787 | 0.806 | 0.778 | 0.750 | 0.565 | 0.481 | 0.231 | 0.537 | 0.611 | 0.898 | 0.704 | 0.694 | 0.833 | 0.565 | 0.787 | 0.667 | 0.306 | 18 |

| metric (95% bootstrap CI, B=2000) | phase15 | phase13 | plain_rag | clinpgx_only | llm_only | amg_rag | medrag | imedrag | paperqa2 | paperqa2_fixed | paperqa2_fixed_clinpgx | lightrag | gpt4o | gpt4turbo | llama3_70b | gpt35 | gemini |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| consult:BERTScore-F1 | 0.17 [0.11, 0.23] | 0.17 [0.12, 0.22] | 0.16 [0.10, 0.22] | 0.15 [0.10, 0.20] | 0.16 [0.12, 0.21] | 0.13 [0.08, 0.18] | 0.10 [0.02, 0.18] | 0.18 [0.14, 0.23] | 0.14 [0.11, 0.17] | 0.17 [0.13, 0.21] | 0.14 [0.09, 0.20] | 0.07 [0.02, 0.12] | - | - | - | - | - |
| d2g:F1 | 0.70 [0.55, 0.85] | 0.74 [0.59, 0.88] | 0.79 [0.64, 0.92] | 0.80 [0.64, 0.93] | 0.37 [0.18, 0.58] | 0.33 [0.15, 0.52] | 0.48 [0.28, 0.70] | 0.54 [0.33, 0.74] | 0.53 [0.34, 0.71] | 0.59 [0.42, 0.74] | 0.60 [0.41, 0.78] | 0.39 [0.24, 0.53] | 0.73 [0.55, 0.88] | 0.61 [0.43, 0.78] | 0.66 [0.50, 0.80] | 0.42 [0.27, 0.59] | 0.37 [0.21, 0.53] |
| d2g:P | 0.69 [0.51, 0.86] | 0.74 [0.57, 0.90] | 0.79 [0.62, 0.93] | 0.81 [0.66, 0.95] | 0.35 [0.17, 0.55] | 0.30 [0.12, 0.47] | 0.50 [0.30, 0.70] | 0.54 [0.32, 0.75] | 0.50 [0.33, 0.70] | 0.54 [0.37, 0.72] | 0.57 [0.37, 0.76] | 0.30 [0.18, 0.41] | 0.72 [0.55, 0.90] | 0.59 [0.41, 0.77] | 0.62 [0.44, 0.78] | 0.34 [0.20, 0.49] | 0.32 [0.17, 0.48] |
| d2g:R | 0.85 [0.70, 0.97] | 0.85 [0.70, 0.97] | 0.85 [0.70, 0.97] | 0.85 [0.70, 0.97] | 0.40 [0.20, 0.60] | 0.40 [0.20, 0.60] | 0.47 [0.25, 0.68] | 0.57 [0.35, 0.78] | 0.62 [0.42, 0.82] | 0.78 [0.60, 0.95] | 0.70 [0.50, 0.88] | 0.60 [0.35, 0.80] | 0.78 [0.60, 0.95] | 0.70 [0.50, 0.88] | 0.80 [0.62, 0.95] | 0.70 [0.50, 0.90] | 0.50 [0.30, 0.70] |
| g2d:F1 | 0.58 [0.46, 0.70] | 0.54 [0.42, 0.67] | 0.60 [0.48, 0.72] | 0.59 [0.49, 0.70] | 0.11 [0.00, 0.26] | 0.15 [0.03, 0.30] | 0.07 [0.00, 0.19] | 0.32 [0.16, 0.49] | 0.23 [0.10, 0.38] | 0.54 [0.37, 0.71] | 0.26 [0.12, 0.42] | 0.34 [0.16, 0.54] | 0.57 [0.38, 0.74] | 0.44 [0.27, 0.61] | 0.54 [0.38, 0.69] | 0.19 [0.06, 0.33] | 0.08 [0.00, 0.20] |
| g2d:P | 0.71 [0.58, 0.84] | 0.66 [0.52, 0.79] | 0.78 [0.66, 0.90] | 0.78 [0.66, 0.89] | 0.15 [0.00, 0.30] | 0.25 [0.10, 0.45] | 0.10 [0.00, 0.25] | 0.42 [0.23, 0.62] | 0.33 [0.15, 0.53] | 0.67 [0.47, 0.85] | 0.39 [0.19, 0.60] | 0.37 [0.19, 0.57] | 0.60 [0.40, 0.78] | 0.45 [0.27, 0.66] | 0.56 [0.38, 0.74] | 0.17 [0.05, 0.31] | 0.08 [0.00, 0.20] |
| g2d:R | 0.60 [0.44, 0.76] | 0.60 [0.44, 0.77] | 0.61 [0.46, 0.76] | 0.58 [0.44, 0.74] | 0.10 [0.00, 0.25] | 0.14 [0.02, 0.29] | 0.06 [0.00, 0.16] | 0.32 [0.15, 0.51] | 0.21 [0.07, 0.37] | 0.52 [0.34, 0.70] | 0.21 [0.08, 0.36] | 0.35 [0.17, 0.54] | 0.61 [0.41, 0.81] | 0.56 [0.36, 0.76] | 0.62 [0.43, 0.79] | 0.26 [0.10, 0.43] | 0.08 [0.00, 0.20] |
| refusal(misspecified):extended | 0.43 [0.14, 0.86] | 0.29 [0.00, 0.57] | 0.00 [0.00, 0.00] | 0.29 [0.00, 0.57] | 0.57 [0.14, 0.86] | 0.57 [0.14, 0.86] | 0.86 [0.57, 1.00] | 0.71 [0.29, 1.00] | 0.86 [0.57, 1.00] | 0.71 [0.29, 1.00] | 0.71 [0.43, 1.00] | 0.86 [0.57, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.43 [0.14, 0.86] | 0.86 [0.57, 1.00] | 0.29 [0.00, 0.57] |
| refusal(misspecified):pgxqa | 0.14 [0.00, 0.43] | 0.14 [0.00, 0.43] | 0.00 [0.00, 0.00] | 0.14 [0.00, 0.43] | 0.29 [0.00, 0.57] | 0.29 [0.00, 0.71] | 0.86 [0.57, 1.00] | 0.71 [0.29, 1.00] | 0.29 [0.00, 0.57] | 0.29 [0.00, 0.57] | 0.71 [0.43, 1.00] | 0.86 [0.57, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.43 [0.14, 0.86] | 0.86 [0.57, 1.00] | 0.29 [0.00, 0.57] |
| refusal(well-specified):extended | 0.12 [0.03, 0.25] | 0.12 [0.03, 0.23] | 0.10 [0.03, 0.20] | 0.10 [0.03, 0.20] | 0.33 [0.17, 0.47] | 0.47 [0.33, 0.62] | 0.85 [0.72, 0.95] | 0.50 [0.35, 0.65] | 0.55 [0.40, 0.70] | 0.25 [0.12, 0.38] | 0.38 [0.23, 0.53] | 0.57 [0.42, 0.72] | 0.20 [0.07, 0.33] | 0.33 [0.17, 0.47] | 0.05 [0.00, 0.12] | 0.57 [0.42, 0.72] | 0.15 [0.05, 0.25] |
| refusal(well-specified):pgxqa | 0.05 [0.00, 0.12] | 0.03 [0.00, 0.07] | 0.03 [0.00, 0.07] | 0.07 [0.00, 0.15] | 0.28 [0.15, 0.42] | 0.38 [0.23, 0.53] | 0.85 [0.72, 0.95] | 0.50 [0.35, 0.65] | 0.30 [0.15, 0.45] | 0.23 [0.10, 0.35] | 0.35 [0.20, 0.50] | 0.57 [0.42, 0.72] | 0.20 [0.07, 0.33] | 0.33 [0.17, 0.47] | 0.05 [0.00, 0.12] | 0.57 [0.40, 0.72] | 0.15 [0.05, 0.28] |
| refusal_d2g:F1 | 0.59 [0.42, 0.74] | 0.65 [0.48, 0.81] | 0.67 [0.48, 0.82] | 0.66 [0.49, 0.81] | 0.47 [0.27, 0.65] | 0.34 [0.17, 0.50] | 0.19 [0.04, 0.34] | 0.49 [0.29, 0.71] | 0.49 [0.28, 0.70] | 0.68 [0.54, 0.82] | 0.56 [0.36, 0.75] | 0.46 [0.29, 0.61] | 0.76 [0.58, 0.93] | 0.46 [0.29, 0.63] | 0.64 [0.48, 0.79] | 0.35 [0.20, 0.51] | 0.25 [0.09, 0.43] |
| refusal_d2g:P | 0.55 [0.38, 0.73] | 0.60 [0.43, 0.78] | 0.63 [0.44, 0.81] | 0.68 [0.48, 0.85] | 0.44 [0.26, 0.61] | 0.29 [0.12, 0.46] | 0.19 [0.06, 0.36] | 0.49 [0.26, 0.71] | 0.44 [0.25, 0.65] | 0.63 [0.46, 0.79] | 0.51 [0.32, 0.71] | 0.37 [0.22, 0.54] | 0.73 [0.54, 0.90] | 0.45 [0.26, 0.63] | 0.61 [0.43, 0.78] | 0.28 [0.14, 0.45] | 0.27 [0.10, 0.47] |
| refusal_d2g:R | 0.79 [0.61, 0.94] | 0.81 [0.61, 0.94] | 0.78 [0.58, 0.94] | 0.75 [0.56, 0.92] | 0.56 [0.35, 0.78] | 0.48 [0.26, 0.70] | 0.23 [0.06, 0.43] | 0.54 [0.31, 0.76] | 0.61 [0.39, 0.83] | 0.90 [0.77, 1.00] | 0.70 [0.48, 0.89] | 0.69 [0.47, 0.89] | 0.83 [0.67, 1.00] | 0.56 [0.35, 0.76] | 0.79 [0.60, 0.94] | 0.67 [0.44, 0.89] | 0.31 [0.11, 0.50] |

| phase15 minus system, paired [95% CI], p two-sided | phase13 | plain_rag | clinpgx_only | llm_only | amg_rag | medrag | imedrag | paperqa2 | paperqa2_fixed | paperqa2_fixed_clinpgx | lightrag | gpt4o | gpt4turbo | llama3_70b | gpt35 | gemini |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| consult:BERTScore-F1 | -0.00 [-0.05, +0.04] p=0.90 | +0.01 [-0.03, +0.05] p=0.76 | +0.02 [-0.00, +0.05] p=0.10 | +0.01 [-0.03, +0.05] p=0.79 | +0.04 [+0.00, +0.09] p=0.04 | +0.07 [+0.02, +0.11] p=0.00 | -0.01 [-0.05, +0.03] p=0.66 | +0.03 [-0.03, +0.10] p=0.34 | +0.00 [-0.09, +0.07] p=0.88 | +0.03 [-0.07, +0.10] p=0.54 | +0.10 [+0.03, +0.16] p=0.00 | - | - | - | - | - |
| d2g:F1 | -0.04 [-0.18, +0.09] p=0.48 | -0.09 [-0.21, +0.03] p=0.13 | -0.10 [-0.24, +0.03] p=0.13 | +0.33 [+0.13, +0.53] p=0.00 | +0.37 [+0.18, +0.55] p=0.00 | +0.22 [-0.05, +0.47] p=0.10 | +0.16 [-0.07, +0.39] p=0.18 | +0.17 [-0.03, +0.37] p=0.09 | +0.11 [-0.09, +0.31] p=0.28 | +0.10 [-0.11, +0.32] p=0.34 | +0.31 [+0.09, +0.53] p=0.01 | -0.03 [-0.22, +0.17] p=0.73 | +0.09 [-0.09, +0.29] p=0.37 | +0.04 [-0.17, +0.25] p=0.67 | +0.28 [+0.10, +0.47] p=0.00 | +0.33 [+0.11, +0.55] p=0.01 |
| d2g:P | -0.05 [-0.22, +0.12] p=0.54 | -0.10 [-0.26, +0.05] p=0.17 | -0.12 [-0.30, +0.05] p=0.17 | +0.34 [+0.13, +0.55] p=0.00 | +0.39 [+0.19, +0.59] p=0.00 | +0.19 [-0.11, +0.46] p=0.19 | +0.15 [-0.09, +0.39] p=0.21 | +0.18 [-0.01, +0.41] p=0.06 | +0.15 [-0.07, +0.39] p=0.20 | +0.12 [-0.11, +0.35] p=0.33 | +0.39 [+0.14, +0.63] p=0.00 | -0.04 [-0.23, +0.17] p=0.76 | +0.10 [-0.13, +0.32] p=0.39 | +0.07 [-0.18, +0.32] p=0.57 | +0.35 [+0.12, +0.56] p=0.00 | +0.37 [+0.11, +0.62] p=0.00 |
| d2g:R | +0.00 [+0.00, +0.00] p=1.00 | +0.00 [+0.00, +0.00] p=1.00 | +0.00 [+0.00, +0.00] p=1.00 | +0.45 [+0.25, +0.68] p=0.00 | +0.45 [+0.25, +0.65] p=0.00 | +0.38 [+0.12, +0.60] p=0.00 | +0.28 [+0.03, +0.50] p=0.04 | +0.23 [-0.03, +0.45] p=0.09 | +0.07 [-0.10, +0.25] p=0.53 | +0.15 [-0.07, +0.38] p=0.25 | +0.25 [+0.03, +0.47] p=0.04 | +0.07 [-0.12, +0.30] p=0.58 | +0.15 [+0.00, +0.33] p=0.07 | +0.05 [-0.10, +0.20] p=0.64 | +0.15 [+0.03, +0.30] p=0.02 | +0.35 [+0.12, +0.55] p=0.01 |
| g2d:F1 | +0.04 [-0.05, +0.13] p=0.36 | -0.02 [-0.13, +0.09] p=0.76 | -0.02 [-0.13, +0.09] p=0.80 | +0.47 [+0.30, +0.64] p=0.00 | +0.42 [+0.23, +0.61] p=0.00 | +0.51 [+0.34, +0.67] p=0.00 | +0.25 [+0.06, +0.46] p=0.01 | +0.35 [+0.19, +0.51] p=0.00 | +0.04 [-0.14, +0.22] p=0.69 | +0.32 [+0.11, +0.53] p=0.00 | +0.24 [+0.05, +0.43] p=0.01 | +0.00 [-0.19, +0.20] p=0.97 | +0.13 [-0.03, +0.29] p=0.12 | +0.04 [-0.17, +0.23] p=0.69 | +0.39 [+0.21, +0.56] p=0.00 | +0.50 [+0.33, +0.68] p=0.00 |
| g2d:P | +0.05 [-0.00, +0.13] p=0.08 | -0.07 [-0.21, +0.03] p=0.21 | -0.07 [-0.23, +0.07] p=0.36 | +0.56 [+0.37, +0.74] p=0.00 | +0.46 [+0.21, +0.69] p=0.00 | +0.61 [+0.37, +0.81] p=0.00 | +0.29 [+0.07, +0.53] p=0.01 | +0.39 [+0.15, +0.61] p=0.00 | +0.04 [-0.11, +0.22] p=0.63 | +0.33 [+0.11, +0.52] p=0.01 | +0.34 [+0.17, +0.52] p=0.00 | +0.11 [-0.12, +0.36] p=0.42 | +0.26 [+0.06, +0.46] p=0.01 | +0.15 [-0.12, +0.39] p=0.25 | +0.54 [+0.34, +0.71] p=0.00 | +0.63 [+0.45, +0.81] p=0.00 |
| g2d:R | -0.00 [-0.10, +0.10] p=0.95 | -0.01 [-0.11, +0.10] p=0.98 | +0.02 [-0.07, +0.10] p=0.68 | +0.50 [+0.29, +0.68] p=0.00 | +0.46 [+0.26, +0.65] p=0.00 | +0.54 [+0.37, +0.71] p=0.00 | +0.28 [+0.07, +0.49] p=0.01 | +0.39 [+0.21, +0.58] p=0.00 | +0.08 [-0.10, +0.27] p=0.40 | +0.39 [+0.19, +0.60] p=0.00 | +0.25 [+0.02, +0.49] p=0.03 | -0.01 [-0.20, +0.18] p=0.90 | +0.04 [-0.14, +0.23] p=0.69 | -0.02 [-0.20, +0.17] p=0.88 | +0.34 [+0.13, +0.56] p=0.00 | +0.52 [+0.29, +0.72] p=0.00 |
| refusal(misspecified):extended | +0.14 [-0.29, +0.57] p=0.73 | +0.43 [+0.14, +0.71] p=0.04 | +0.14 [+0.00, +0.43] p=0.69 | -0.14 [-0.57, +0.29] p=0.77 | -0.14 [-0.43, +0.00] p=0.69 | -0.43 [-0.71, -0.14] p=0.04 | -0.29 [-0.71, +0.00] p=0.18 | -0.43 [-0.86, -0.14] p=0.04 | -0.29 [-0.86, +0.29] p=0.43 | -0.29 [-0.71, +0.29] p=0.40 | -0.43 [-0.86, -0.14] p=0.03 | -0.57 [-0.86, -0.14] p=0.00 | -0.57 [-0.86, -0.14] p=0.00 | +0.00 [-0.43, +0.43] p=1.00 | -0.43 [-0.86, -0.14] p=0.03 | +0.14 [-0.43, +0.71] p=0.85 |
| refusal(misspecified):pgxqa | +0.00 [-0.43, +0.43] p=1.00 | +0.14 [+0.00, +0.43] p=0.71 | +0.00 [-0.43, +0.43] p=1.00 | -0.14 [-0.57, +0.29] p=0.73 | -0.14 [-0.57, +0.29] p=0.73 | -0.71 [-1.00, -0.43] p=0.00 | -0.57 [-0.86, -0.29] p=0.01 | -0.14 [-0.57, +0.29] p=0.79 | -0.14 [-0.57, +0.29] p=0.77 | -0.57 [-1.00, -0.14] p=0.01 | -0.71 [-1.00, -0.43] p=0.00 | -0.86 [-1.00, -0.57] p=0.00 | -0.86 [-1.00, -0.57] p=0.00 | -0.29 [-0.57, +0.00] p=0.17 | -0.71 [-1.00, -0.43] p=0.00 | -0.14 [-0.57, +0.29] p=0.75 |
| refusal(well-specified):extended | +0.00 [-0.10, +0.10] p=1.00 | +0.03 [-0.05, +0.10] p=0.79 | +0.03 [-0.07, +0.12] p=0.78 | -0.20 [-0.35, -0.05] p=0.02 | -0.35 [-0.53, -0.17] p=0.00 | -0.72 [-0.85, -0.57] p=0.00 | -0.38 [-0.53, -0.22] p=0.00 | -0.42 [-0.60, -0.23] p=0.00 | -0.12 [-0.30, +0.05] p=0.20 | -0.25 [-0.42, -0.07] p=0.01 | -0.45 [-0.62, -0.28] p=0.00 | -0.07 [-0.20, +0.03] p=0.24 | -0.20 [-0.35, -0.07] p=0.01 | +0.07 [-0.05, +0.23] p=0.33 | -0.45 [-0.60, -0.28] p=0.00 | -0.03 [-0.15, +0.10] p=0.83 |
| refusal(well-specified):pgxqa | +0.03 [+0.00, +0.07] p=0.69 | +0.03 [+0.00, +0.07] p=0.78 | -0.03 [-0.10, +0.05] p=0.80 | -0.23 [-0.35, -0.10] p=0.00 | -0.33 [-0.50, -0.15] p=0.00 | -0.80 [-0.93, -0.68] p=0.00 | -0.45 [-0.60, -0.30] p=0.00 | -0.25 [-0.40, -0.07] p=0.01 | -0.17 [-0.33, -0.03] p=0.03 | -0.30 [-0.45, -0.15] p=0.00 | -0.53 [-0.68, -0.38] p=0.00 | -0.15 [-0.28, -0.05] p=0.00 | -0.28 [-0.42, -0.15] p=0.00 | +0.00 [-0.10, +0.10] p=1.00 | -0.53 [-0.68, -0.35] p=0.00 | -0.10 [-0.20, -0.03] p=0.03 |
| refusal_d2g:F1 | -0.05 [-0.13, +0.01] p=0.09 | -0.08 [-0.18, +0.02] p=0.12 | -0.07 [-0.20, +0.04] p=0.22 | +0.12 [-0.09, +0.31] p=0.26 | +0.26 [+0.08, +0.44] p=0.00 | +0.40 [+0.19, +0.59] p=0.00 | +0.10 [-0.15, +0.33] p=0.44 | +0.10 [-0.07, +0.30] p=0.29 | -0.09 [-0.26, +0.07] p=0.28 | +0.03 [-0.19, +0.26] p=0.81 | +0.14 [-0.01, +0.30] p=0.08 | -0.17 [-0.34, +0.03] p=0.08 | +0.13 [-0.06, +0.32] p=0.19 | -0.05 [-0.26, +0.16] p=0.60 | +0.24 [+0.06, +0.43] p=0.01 | +0.34 [+0.16, +0.52] p=0.00 |
| refusal_d2g:P | -0.05 [-0.14, +0.01] p=0.14 | -0.08 [-0.22, +0.05] p=0.21 | -0.13 [-0.26, -0.01] p=0.04 | +0.11 [-0.10, +0.33] p=0.30 | +0.26 [+0.07, +0.47] p=0.00 | +0.36 [+0.14, +0.57] p=0.00 | +0.06 [-0.17, +0.29] p=0.54 | +0.11 [-0.09, +0.33] p=0.35 | -0.08 [-0.28, +0.11] p=0.46 | +0.04 [-0.19, +0.26] p=0.75 | +0.18 [-0.00, +0.36] p=0.05 | -0.18 [-0.38, +0.02] p=0.08 | +0.10 [-0.10, +0.31] p=0.35 | -0.06 [-0.26, +0.16] p=0.58 | +0.27 [+0.04, +0.48] p=0.02 | +0.28 [+0.06, +0.49] p=0.01 |
| refusal_d2g:R | -0.02 [-0.06, +0.00] p=0.75 | +0.01 [-0.06, +0.08] p=0.94 | +0.04 [-0.04, +0.12] p=0.42 | +0.22 [-0.03, +0.44] p=0.09 | +0.31 [+0.11, +0.50] p=0.00 | +0.56 [+0.33, +0.75] p=0.00 | +0.25 [-0.03, +0.50] p=0.08 | +0.18 [+0.01, +0.37] p=0.05 | -0.11 [-0.28, +0.03] p=0.24 | +0.08 [-0.17, +0.36] p=0.63 | +0.09 [-0.06, +0.28] p=0.32 | -0.05 [-0.21, +0.12] p=0.65 | +0.22 [+0.06, +0.39] p=0.00 | +0.00 [-0.22, +0.19] p=1.00 | +0.12 [-0.02, +0.29] p=0.11 | +0.48 [+0.28, +0.69] p=0.00 |

## Masked-association recovery (E1)

| system | gene | drug | proposed | via | queried_round | in_digest | in_ledger | candidate | confidence | in_answer | in_risk_genes | in_candidate_genes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| phase15 | ACYP2 | cisplatin | True | A | 1 | True | True | True | 0.54 | True | True | False |
| phase15 | TPMT | cisplatin | False |  |  | True | True | True | 0.28 | True | True | False |
| phase15 | COMT | cisplatin | False |  |  | True | True | True | 0.28 | False | False | False |
| phase15 | GSTP1 | cisplatin | False |  |  | True | True | True | 0.28 | False | False | False |
| phase15 | ABCC3 | cisplatin | False |  |  | True | True | True | 0.28 | False | False | False |
| phase15 | SLC16A5 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| phase15 | SLC28A3 | doxorubicin | False |  |  | True | True | True | 0.38 | False | False | True |
| phase15 | RARG | doxorubicin | False |  |  | True | True | True | 0.54 | True | False | True |
| phase15 | UGT1A6 | doxorubicin | False |  |  | True | True | True | 0.28 | True | False | True |
| phase15 | CBR3 | doxorubicin | False |  |  | True | True | True | 0.09 | False | False | False |
| phase13 | ACYP2 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| phase13 | TPMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| phase13 | COMT | cisplatin | False |  |  | True | True | True | 0.28 | False | False | False |
| phase13 | GSTP1 | cisplatin | False |  |  | True | True | True | 0.28 | False | False | False |
| phase13 | ABCC3 | cisplatin | False |  |  | True | True | True | 0.28 | False | False | False |
| phase13 | SLC16A5 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| phase13 | SLC28A3 | doxorubicin | False |  |  | True | True | False | 0.07 | False | False | False |
| phase13 | RARG | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| phase13 | UGT1A6 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| phase13 | CBR3 | doxorubicin | False |  |  | True | True | False | 0.07 | False | False | False |
| llm_only | ACYP2 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| llm_only | TPMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| llm_only | COMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| llm_only | GSTP1 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| llm_only | ABCC3 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| llm_only | SLC16A5 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| llm_only | SLC28A3 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| llm_only | RARG | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| llm_only | UGT1A6 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| llm_only | CBR3 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| medrag | ACYP2 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| medrag | TPMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| medrag | COMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| medrag | GSTP1 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| medrag | ABCC3 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| medrag | SLC16A5 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| medrag | SLC28A3 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| medrag | RARG | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| medrag | UGT1A6 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| medrag | CBR3 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| imedrag | ACYP2 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| imedrag | TPMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| imedrag | COMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| imedrag | GSTP1 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| imedrag | ABCC3 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| imedrag | SLC16A5 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| imedrag | SLC28A3 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| imedrag | RARG | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| imedrag | UGT1A6 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| imedrag | CBR3 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| paperqa2 | ACYP2 | cisplatin | False |  |  | False | False | False |  | True | False | False |
| paperqa2 | TPMT | cisplatin | False |  |  | False | False | False |  | True | False | False |
| paperqa2 | COMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| paperqa2 | GSTP1 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| paperqa2 | ABCC3 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| paperqa2 | SLC16A5 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| paperqa2 | SLC28A3 | doxorubicin | False |  |  | False | False | False |  | True | False | False |
| paperqa2 | RARG | doxorubicin | False |  |  | False | False | False |  | True | False | False |
| paperqa2 | UGT1A6 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| paperqa2 | CBR3 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| paperqa2_fixed | ACYP2 | cisplatin | False |  |  | False | False | False |  | True | False | False |
| paperqa2_fixed | TPMT | cisplatin | False |  |  | False | False | False |  | True | False | False |
| paperqa2_fixed | COMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| paperqa2_fixed | GSTP1 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| paperqa2_fixed | ABCC3 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| paperqa2_fixed | SLC16A5 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| paperqa2_fixed | SLC28A3 | doxorubicin | False |  |  | False | False | False |  | True | False | False |
| paperqa2_fixed | RARG | doxorubicin | False |  |  | False | False | False |  | True | False | False |
| paperqa2_fixed | UGT1A6 | doxorubicin | False |  |  | False | False | False |  | True | False | False |
| paperqa2_fixed | CBR3 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| paperqa2_fixed_clinpgx | ACYP2 | cisplatin | False |  |  | False | False | False |  | True | False | False |
| paperqa2_fixed_clinpgx | TPMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| paperqa2_fixed_clinpgx | COMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| paperqa2_fixed_clinpgx | GSTP1 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| paperqa2_fixed_clinpgx | ABCC3 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| paperqa2_fixed_clinpgx | SLC16A5 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| paperqa2_fixed_clinpgx | SLC28A3 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| paperqa2_fixed_clinpgx | RARG | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| paperqa2_fixed_clinpgx | UGT1A6 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| paperqa2_fixed_clinpgx | CBR3 | doxorubicin | False |  |  | False | False | False |  | False | False | False |
| lightrag | ACYP2 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| lightrag | TPMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| lightrag | COMT | cisplatin | False |  |  | False | False | False |  | False | False | False |
| lightrag | GSTP1 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| lightrag | ABCC3 | cisplatin | False |  |  | False | False | False |  | True | False | False |
| lightrag | SLC16A5 | cisplatin | False |  |  | False | False | False |  | False | False | False |
| lightrag | SLC28A3 | doxorubicin | False |  |  | False | False | False |  | True | False | False |
| lightrag | RARG | doxorubicin | False |  |  | False | False | False |  | True | False | False |
| lightrag | UGT1A6 | doxorubicin | False |  |  | False | False | False |  | True | False | False |
| lightrag | CBR3 | doxorubicin | False |  |  | False | False | False |  | False | False | False |

## Recovery rates
| system | n | proposed | in digest | in ledger | candidate | in answer | in risk/candidate genes |
|---|---|---|---|---|---|---|---|
| phase15 | 10 | 10% | 90% | 90% | 90% | 40% | 50% |
| phase13 | 10 | 0% | 50% | 50% | 30% | 0% | 0% |
| llm_only | 10 | 0% | 0% | 0% | 0% | 0% | 0% |
| medrag | 10 | 0% | 0% | 0% | 0% | 0% | 0% |
| imedrag | 10 | 0% | 0% | 0% | 0% | 0% | 0% |
| paperqa2 | 10 | 0% | 0% | 0% | 0% | 40% | 0% |
| paperqa2_fixed | 10 | 0% | 0% | 0% | 0% | 50% | 0% |
| paperqa2_fixed_clinpgx | 10 | 0% | 0% | 0% | 0% | 10% | 0% |
| lightrag | 10 | 0% | 0% | 0% | 0% | 40% | 0% |

## PGxCorpus extraction

| metric | pgxcorpus_llm.jsonl | pgxcorpus_dict.jsonl |
|---|---|---|
| drug:F1 | 0.818 | 0.492 |
| drug:P | 0.914 | 0.546 |
| drug:R | 0.776 | 0.468 |
| drug:microF1 | 0.807 | 0.609 |
| gene[all]:F1 | 0.599 | 0.426 |
| gene[all]:P | 0.657 | 0.486 |
| gene[all]:R | 0.573 | 0.400 |
| gene[all]:microF1 | 0.645 | 0.532 |
| gene[symbols]:F1 | 0.692 | 0.510 |
| gene[symbols]:P | 0.714 | 0.542 |
| gene[symbols]:R | 0.684 | 0.495 |
| gene[symbols]:microF1 | 0.769 | 0.649 |
| n | 874 | 874 |
