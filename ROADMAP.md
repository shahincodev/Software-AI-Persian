# Software-AI Development Roadmap

## Free Models & Smart API System - Development Plan

---

## Current Issues Identified

### 1. Security Issue (FIXED)
- `.env` file contained a **real API key** that was exposed
- **Status**: FIXED - Key removed, `.env` cleaned up

### 2. Duplicate Variables
- `GROQ_API_KEY` appears twice (lines 31 and 80)
- `OPENAI_API_KEY` appears twice (lines 64 and 83)
- `GOOGLE_API_KEY` appears twice (lines 23 and 86)
- `MODEL_TEMPERATURE` appears twice (lines 49 and 101)

### 3. Outdated/Non-free Models
- OpenRouter models listed are paid (gpt-5.2, claude-sonnet-4.5, etc.)
- Should use free `:free` variants available on OpenRouter

---

## Phase 1: Clean `.env.example` & `.env`

**Goal:** Fix security issues, remove duplicates, update placeholders

### Tasks
- [ ] Remove duplicate variables from `.env.example`
- [ ] Replace all placeholder keys with consistent format: `your-{provider}-key-here`
- [ ] Remove the exposed real API key from `.env`
- [ ] Add comments explaining which models are free
- [ ] Organize sections cleanly with clear headers
- [ ] Add new section for smart API checker settings

### Files to Modify
| File | Action |
|------|--------|
| `.env.example` | Edit - Clean up duplicates, update placeholders |
| `.env` | Edit - Remove exposed key, fix duplicates |

---

## Phase 2: Update `model_config.py` with Free Models

**Goal:** Replace paid models with current free alternatives (2026 verified)

### Model Mapping

| Provider | Old (Paid) | New (Free) |
|----------|-----------|------------|
| OpenRouter | `openai/gpt-oss-120b` | `openai/gpt-oss-120b:free` |
| OpenRouter | `openai/gpt-5.2` | `meta-llama/llama-3.3-70b-instruct:free` |
| OpenRouter | `openai/gpt-5-mini` | `qwen/qwen3-coder:free` |
| OpenRouter | `anthropic/claude-sonnet-4.5` | `qwen/qwen3-235b-a22b:free` |
| OpenRouter | `mistralai/ministral-14b-2512` | `nvidia/nemotron-3-ultra-550b-a55b:free` |
| Google | Keep existing | Gemini 2.5 Flash (free) |
| Groq | Keep existing | Llama 3.3 70B (free) |
| HuggingFace | Keep existing | DeepSeek (free tier) |

### New Free Models to Add

#### OpenRouter (Free Tier)
- `openai/gpt-oss-120b:free` - Priority 100
- `meta-llama/llama-3.3-70b-instruct:free` - Priority 95
- `qwen/qwen3-235b-a22b:free` - Priority 90
- `nvidia/nemotron-3-ultra-550b-a55b:free` - Priority 85
- `qwen/qwen3-coder:free` - Priority 80
- `openrouter/free` - Priority 70 (auto-router fallback)

#### Google AI Studio (Free Tier)
- `gemini-2.5-flash` - Priority 88 (10 RPM, 250 RPD)

#### Groq (Free Tier)
- `llama-3.3-70b-versatile` - Priority 78
- `qwen-qwq-32b` - Priority 75

#### HuggingFace (Free Tier)
- `deepseek-ai/DeepSeek-V3.2` - Priority 60

### Tasks
- [ ] Update OpenRouter models to free variants
- [ ] Add new free models from OpenRouter
- [ ] Verify Google/Groq/HuggingFace models are current
- [ ] Update priority rankings
- [ ] Update model descriptions

### Files to Modify
| File | Action |
|------|--------|
| `core/model_config.py` | Edit - Update model registry |

---

## Phase 3: Create Smart API Checker Program

**Goal:** Build `tools/api_checker.py` - Smart program to check API status and auto-select models

### Features

#### 1. API Key Validation
- Test each provider's API key validity
- Show response times and availability
- Detect rate limits and quotas

#### 2. Auto Model Selection (OpenCode-style)
- User enters API key → system selects best free model
- Like OpenCode: you provide the key, we pick the model
- Automatic priority optimization

#### 3. Health Monitoring
- Track which providers are responding
- Log response times
- Detect outages

#### 4. Fallback Configuration
- Auto-configure optimal fallback chain
- Generate recommended `model_config.py` settings

### Program Flow
```
User runs: python tools/api_checker.py

1. Reads .env file
2. Tests each API key:
   - Google: Quick Gemini flash request
   - Groq: Quick Llama request
   - OpenRouter: Check free models available
   - HuggingFace: Check inference endpoint
3. Shows status table:
   ✅ Google   - 3 free models available
   ✅ Groq     - 2 free models available
   ❌ OpenRouter - No valid key
4. Auto-updates .env with optimal model selections
5. Generates config recommendations
```

### CLI Options
```bash
# Full check
python tools/api_checker.py

# Check specific provider
python tools/api_checker.py --provider google

# Auto-configure .env
python tools/api_checker.py --auto-configure

# Show only available models
python tools/api_checker.py --available-only

# Test specific model
python tools/api_checker.py --test-model gemini-2.5-flash
```

### Tasks
- [ ] Create `tools/api_checker.py` base structure
- [ ] Implement API key validation for each provider
- [ ] Implement auto model selection logic
- [ ] Add health monitoring
- [ ] Add CLI interface with argparse
- [ ] Add auto-configure feature
- [ ] Add status table display

### Files to Create
| File | Action |
|------|--------|
| `tools/api_checker.py` | Create - Smart API checker program |

---

## Phase 4: Update `.env` (Runtime)

**Goal:** Clean up runtime .env file

### Tasks
- [ ] Remove the exposed real API key
- [ ] Add placeholder format consistent with .env.example
- [ ] Add new variables for smart API checker

### Files to Modify
| File | Action |
|------|--------|
| `.env` | Edit - Remove exposed key, fix duplicates |

---

## Phase 5: Testing & Validation

**Goal:** Verify everything works correctly

### Tasks
- [ ] Test API checker with valid keys
- [ ] Test API checker with invalid keys
- [ ] Verify model fallback chain works
- [ ] Run existing test suite
- [ ] Update test files if needed

### Files to Check
| File | Action |
|------|--------|
| `tests/test_ai_brain_provider_detection.py` | Verify tests pass |
| `tests/test_api_connection.py` | Verify API tests pass |
| `tests/test_comprehensive.py` | Verify comprehensive tests pass |

---

## Free Models Reference (2026)

### Google AI Studio (Free)
- **Gemini 2.5 Flash** - 10 RPM, 250K TPM, 250 RPD
- **Gemini Flash-Lite** - 30 RPM, 1000 RPD

### Groq (Free)
- **Llama 3.3 70B** - Very fast inference
- **Llama 3.1 8B** - Ultra fast
- **Qwen3 32B** - Reasoning capable

### OpenRouter (Free)
- `openai/gpt-oss-120b:free`
- `meta-llama/llama-3.3-70b-instruct:free`
- `qwen/qwen3-235b-a22b:free`
- `nvidia/nemotron-3-ultra-550b-a55b:free`
- `qwen/qwen3-coder:free`
- `openrouter/free` (auto-router)

### HuggingFace (Free)
- **DeepSeek-V3.2** - Free serverless inference

### Ollama (Local - Unlimited)
- Any model pulled locally via `ollama pull`

---

## Success Criteria

- [ ] No real API keys in `.env.example`
- [ ] No duplicate variables in `.env` or `.env.example`
- [ ] All models in `model_config.py` are free
- [ ] Smart API checker program works
- [ ] All existing tests pass
- [ ] Documentation updated

---

## Timeline

| Phase | Estimated Time | Status |
|-------|---------------|--------|
| Phase 1: Clean .env files | 10 min | Pending |
| Phase 2: Update models | 15 min | Pending |
| Phase 3: Create API checker | 30 min | Pending |
| Phase 4: Update runtime .env | 5 min | Pending |
| Phase 5: Testing | 15 min | Pending |
| **Total** | **~75 min** | |

---

*Last updated: 2026-07-08*
