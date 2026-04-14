# Claude Code Context - HIPAA Compliance Bot Refactoring

## Project Intent
Refactor existing HIPAA compliance Slack bot to support:
1. **Swappable LLM providers** (currently Gemini, future Claude)
2. **Adaptive confidence thresholds** based on question complexity
3. **Hybrid knowledge base** (local vector DB + live integration search)
4. **Multi-bot architecture** (HIPAA bot now, architecture/onboarding bots later)
5. **Clean separation of concerns** with ports & adapters pattern

## Current State
Working bot with basic RAG functionality. Needs architectural improvements for:
- Provider swappability (locked to Gemini)
- Better confidence scoring (static threshold)
- Prompt management (hardcoded)
- Knowledge base routing (no hybrid strategy)

## Target Architecture

### Layer Structure (Bottom → Top)

**Clients** (External API wrappers):
- `SlackClient` - Parse events, send messages
- `VectorDBClient` - Pinecone/Weaviate wrapper
- `LLMClient` - Gemini/Claude API wrapper

**Services** (Business logic):
- `Augmenter` - Personality injection, prompt building, output formatting
- `ConfidenceEvaluator` - Adaptive threshold based on question complexity + chunk quality
- `KnowledgeBaseRouter` - Select primary KB, fallback to integrations
- `PromptManager` - Load prompts from files

**Providers** (Swappable backends):
- `RAGProvider` (interface) - embed(), retrieve(), generate()
  - `GeminiRAGProvider` (current)
  - `ClaudeRAGProvider` (future)

**Core**:
- `MessageValidator` - Pre-filter confidence scoring
- `BotEngine` - Orchestrates flow

**Bots** (Domain-specific):
- `HipaaBot` - Uses RAGProvider + Augmenter + config

**App**:
- `app.py` - Flask, webhooks, DI setup

## Key Design Decisions

### 1. Adaptive Confidence Threshold
**Current:** Static threshold (e.g., 0.75)
**Target:** Adjust based on question complexity
```python
class ConfidenceEvaluator:
    BASE_THRESHOLD = 0.75
    MAX_ADJUSTMENT = 0.20
    
    def should_answer(self, question: str, chunks: List[Chunk]) -> tuple[bool, dict]:
        complexity = self._calculate_complexity(question)  # 0.0-1.0
        chunk_quality = self._calculate_chunk_quality(chunks)
        
        adjusted_threshold = self.BASE_THRESHOLD - (complexity * self.MAX_ADJUSTMENT)
        should_answer = chunk_quality['avg_score'] >= adjusted_threshold
        
        return should_answer, metadata
    
    def _calculate_complexity(self, question: str) -> float:
        score = 0.0
        q_lower = question.lower()
        
        # Length factor
        if len(question.split()) > 25: score += 0.3
        elif len(question.split()) > 15: score += 0.15
        
        # Specificity indicators
        if any(w in q_lower for w in ['specific', 'edge case', 'exception']): 
            score += 0.25
        
        # Comparative/multi-part
        if any(w in q_lower for w in ['vs', 'versus', 'compared']): 
            score += 0.2
        
        return min(score, 1.0)
```

### 2. RAGProvider Interface (Swappable)
**Current:** Direct Gemini calls
**Target:** Abstract interface
```python
class RAGProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        pass
    
    @abstractmethod
    def retrieve(self, query_vector: List[float], collection: str, top_k: int) -> List[Chunk]:
        pass
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

class GeminiRAGProvider(RAGProvider):
    def __init__(self, api_key, vector_db_client):
        self.embedder = GeminiEmbedder(api_key)
        self.retriever = VectorDBRetriever(vector_db_client)
        self.generator = GeminiGenerator(api_key)
```

### 3. Prompt Management
**Current:** Hardcoded prompts
**Target:** File-based with runtime reload
```
prompts/
├── hipaa_bot/
│   ├── system.txt
│   ├── user_template.txt
│   └── fallback.txt
└── architecture_bot/
    ├── system.txt
    └── user_template.txt
```
```python
class PromptManager:
    def load(self, bot_name: str, template_name: str) -> str:
        path = f"{self.prompts_dir}/{bot_name}/{template_name}.txt"
        # Load and cache
    
    def reload(self):
        # Clear cache for runtime editing
```

### 4. Hybrid Knowledge Base (Future)
**Current:** Local vector DB only
**Target:** Local KB + live integration fallback
```python
def retrieve(self, question: str, config: dict) -> List[Chunk]:
    # Step 1: Search local KB
    local_chunks = self.vector_db.search(question, collection)
    
    # Step 2: Assess if we need live data
    needs_live = self._assess_recency_need(question)  # "who's working on X now?"
    local_quality = self._assess_quality(local_chunks)
    
    # Step 3: Decide strategy
    if needs_live['required']:
        live_chunks = self._search_integrations(question)
        return self._merge_chunks(local_chunks, live_chunks)
    
    if local_quality['sufficient']:
        return local_chunks
    
    # Fallback to live if local is weak
    return local_chunks  # or search live
```

## Data Flow
```
Slack message
  ↓
SlackClient.parse() → Message object
  ↓
MessageValidator.validate() → Pass/Fail (pre-filter)
  ↓
BotEngine.route() → HipaaBot
  ↓
HipaaBot.process():
  1. query_vector = RAGProvider.embed(question)
  2. chunks = RAGProvider.retrieve(query_vector, collection)
  3. should_answer, metadata = ConfidenceEvaluator.should_answer(question, chunks)
  4. if not should_answer → return fallback
  5. prompt = Augmenter.build_prompt(question, chunks, personality, rules)
  6. answer = RAGProvider.generate(prompt)
  7. formatted = Augmenter.format_output(answer, config)
  ↓
SlackClient.send(formatted) → Thread reply
```

## Refactoring Strategy

**Preserve existing functionality, enhance architecture incrementally:**

### Phase 1: Extract RAGProvider Interface
- Create `RAGProvider` abstract class
- Wrap current Gemini code in `GeminiRAGProvider`
- Update bot to use provider interface
- **No behavior change, just abstraction**

### Phase 2: Add ConfidenceEvaluator
- Extract current threshold logic
- Add complexity scoring
- Keep existing threshold as fallback
- **Enhancement: smarter answering**

### Phase 3: Add PromptManager
- Move prompts to files
- Add reload capability
- Keep existing prompts as default
- **Enhancement: editable prompts**

### Phase 4: Add Augmenter Service
- Extract personality/formatting logic
- Centralize prompt building
- **Enhancement: reusable across bots**

### Phase 5: Prepare for Multi-Bot
- Make config per-bot
- Add BotEngine router
- **Future: architecture_bot, onboarding_bot**

## Migration Principles

1. **max(new_structure, current_code)** - Keep what works, enhance what doesn't
2. **No big-bang rewrites** - Incremental refactoring
3. **Preserve existing behavior** - Tests should still pass
4. **Add abstraction where needed** - Don't over-engineer
5. **File-based config** - Simple, version-controlled

## What NOT to Change

- Slack integration (if working)
- Vector DB setup (if working)
- Gemini API calls (wrap, don't replace)
- Basic message flow (preserve)

## What MUST Change

- Hardcoded thresholds → Adaptive
- Coupled LLM provider → Swappable interface
- Hardcoded prompts → File-based
- Monolithic bot → Layered architecture

## Code Organization Target
```
hipaa-bot/
├── app.py                      # Flask + DI
├── config/
│   ├── providers.yaml          # LLM provider configs
│   └── bots/
│       └── hipaa_bot.yaml      # Bot-specific config
├── prompts/
│   └── hipaa_bot/
│       ├── system.txt
│       ├── user_template.txt
│       └── fallback.txt
├── bots/
│   └── hipaa_bot.py
├── core/
│   ├── bot_engine.py
│   └── message_validator.py
├── services/
│   ├── augmenter.py
│   ├── confidence_evaluator.py
│   ├── knowledge_base_router.py  # Future
│   └── prompt_manager.py
├── providers/
│   ├── rag_provider.py         # Interface
│   ├── gemini_provider.py
│   └── claude_provider.py      # Future
├── clients/
│   ├── slack_client.py
│   ├── vector_db_client.py
│   └── llm_client.py
└── data/
    └── hipaa_docs/
```

## Success Criteria

After refactoring:
1. ✅ Can swap Gemini → Claude with config change only
2. ✅ Adaptive threshold lowers false negatives on complex questions
3. ✅ Prompts editable without code changes
4. ✅ Clean separation: clients → services → providers → bots
5. ✅ Easy to add new bots (architecture_bot, etc.)
6. ✅ All existing tests pass
7. ✅ No regression in answer quality

## Notes for Claude Code

- **Start with Phase 1** (RAGProvider interface)
- **Preserve working code** - wrap, don't rewrite
- **Add tests for new components** before refactoring
- **Keep git history clean** - one phase per commit
- **Ask before big changes** - discuss tradeoffs

---

**Current priority:** Phase 1 - Extract RAGProvider interface while preserving all existing Gemini functionality.