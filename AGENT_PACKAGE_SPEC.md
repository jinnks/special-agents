# Special Agents Package Specification (.sagent)

## Overview

A `.sagent` package is a standardized format for distributing AI agents on the Special Agents marketplace. It uses YAML for human readability and includes all necessary components to deploy a specialized AI agent.

## Package Format

A `.sagent` package is a **ZIP archive** containing:

```
my-agent.sagent (ZIP file)
├── agent.yaml           # Main configuration (REQUIRED)
├── system_prompt.txt    # System prompt (REQUIRED)
├── examples/            # Example conversations (OPTIONAL)
│   ├── example1.yaml
│   └── example2.yaml
├── knowledge/           # Knowledge base files (OPTIONAL)
│   ├── data.txt
│   └── context.md
├── tools/               # Tool definitions (OPTIONAL - future)
│   └── tools.yaml
└── README.md            # Agent documentation (OPTIONAL)
```

## File Specifications

### 1. agent.yaml (REQUIRED)

Main configuration file defining the agent's metadata and behavior.

```yaml
# Agent Package Format Version
version: "1.0"

# Agent Metadata
metadata:
  name: "Holiday Planning Expert"
  version: "1.0.0"
  author: "username"
  description: "AI agent specialized in planning holidays, suggesting destinations, and creating itineraries"
  category: "travel"  # productivity, education, travel, health, finance, creative
  tags:
    - travel
    - holidays
    - planning
    - itinerary

  # Pricing
  price: 9.99
  currency: "USD"

  # License
  license: "MIT"  # or proprietary, CC-BY, etc.

# Agent Configuration
agent:
  # Model preferences (optional - defaults to Claude Sonnet)
  model: "claude-3-5-sonnet-20241022"

  # Temperature (0.0 - 1.0)
  temperature: 0.7

  # Max tokens for responses
  max_tokens: 4096

  # Response style
  tone: "friendly"  # professional, casual, friendly, formal

  # Language support
  languages:
    - en
    - es
    - fr

# Capabilities and Limitations
capabilities:
  strengths:
    - "Expert knowledge of global destinations"
    - "Creates detailed day-by-day itineraries"
    - "Budget-conscious recommendations"
    - "Cultural insights and local tips"

  limitations:
    - "Cannot make actual bookings"
    - "Prices may not be real-time"
    - "Requires user to specify budget and preferences"

# Ethical Guidelines
ethics:
  safe_for_children: true
  data_collection: false
  privacy_preserving: true
  harmful_use_prevention: true

# Example Use Cases
use_cases:
  - "Plan a 2-week European vacation"
  - "Suggest weekend getaways within budget"
  - "Create family-friendly itineraries"
  - "Find off-the-beaten-path destinations"
```

### 2. system_prompt.txt (REQUIRED)

The core system prompt that defines the agent's behavior, expertise, and personality.

```
You are a Holiday Planning Expert AI agent. Your role is to help users plan amazing vacations and trips.

EXPERTISE:
- Global destination knowledge
- Budget planning
- Itinerary creation
- Cultural insights
- Travel logistics

PERSONALITY:
- Enthusiastic about travel
- Patient and detail-oriented
- Budget-conscious
- Culturally sensitive

WORKFLOW:
1. Understand user's preferences (budget, dates, interests, group size)
2. Suggest 2-3 destination options with rationale
3. Once destination chosen, create detailed day-by-day itinerary
4. Include activities, restaurants, accommodations, transportation tips
5. Provide budget breakdown

CONSTRAINTS:
- Always ask about budget first
- Consider travel restrictions and seasons
- Mention visa requirements when relevant
- Prioritize safety and practicality
- Cannot make actual bookings - provide recommendations only

RESPONSE FORMAT:
- Use clear sections (Overview, Itinerary, Budget, Tips)
- Include specific recommendations (not just generic advice)
- Provide alternatives when possible
```

### 3. examples/ (OPTIONAL)

Example conversations demonstrating the agent's capabilities.

**examples/example1.yaml:**
```yaml
conversation:
  - role: user
    content: "I want to plan a 1-week trip to Japan for 2 people, budget around $3000"

  - role: assistant
    content: |
      Great choice! Japan is amazing. Let me help you plan this trip.

      First, a few questions to personalize your itinerary:
      1. What time of year are you planning to visit?
      2. Are you interested in: cultural sites, modern cities, nature, food, or a mix?
      3. Does your $3000 budget include flights or just in-country expenses?

      Based on your budget, I'd suggest focusing on 2-3 cities to maximize your experience...
```

### 4. knowledge/ (OPTIONAL)

Additional context, data, or reference materials the agent might need. These files are appended to the system prompt or used as retrieval context.

**knowledge/destinations.txt:**
```
JAPAN - TOKYO
- Best seasons: March-May (cherry blossoms), Sept-Nov (fall colors)
- Budget daily cost: $100-150 per person
- Must-see: Senso-ji Temple, Shibuya Crossing, Meiji Shrine
- Food: Try ramen ($8-15), conveyor belt sushi ($20-30)
...
```

### 5. tools/ (OPTIONAL - Future Feature)

For agents that need external tools (APIs, calculators, etc.). Uses MCP (Model Context Protocol) standard.

**tools/tools.yaml:**
```yaml
tools:
  - name: currency_converter
    type: mcp
    description: Convert between currencies
    endpoint: "https://api.exchangerate.com/v1/convert"

  - name: flight_search
    type: api
    description: Search for flight prices
    requires_api_key: true
```

### 6. README.md (OPTIONAL)

Human-readable documentation for buyers.

```markdown
# Holiday Planning Expert

Your personal AI travel planner! Get customized itineraries, budget breakdowns, and insider tips.

## What I Can Do
- Create detailed day-by-day itineraries
- Suggest destinations based on your budget
- Provide cultural insights and local tips
- Help with budget planning

## Best For
- First-time travelers to new countries
- Budget-conscious travelers
- Family vacation planning
- Solo adventure seekers

## How to Use
1. Tell me your budget and dates
2. Share your interests (culture, food, nature, etc.)
3. I'll suggest destinations and create a full itinerary

## Example Questions
- "Plan a 10-day trip to Southeast Asia for $2000"
- "Best weekend getaways from London under £500"
- "Family-friendly 2-week USA road trip"
```

## Validation Rules

When a `.sagent` package is uploaded, the platform validates:

### Required Files
- ✅ `agent.yaml` exists and is valid YAML
- ✅ `system_prompt.txt` exists and is non-empty
- ✅ Package size < 50MB
- ✅ All referenced files exist

### Metadata Validation
- ✅ `name` is 3-100 characters
- ✅ `category` is valid (productivity/education/travel/health/finance/creative)
- ✅ `price` is >= 0
- ✅ `version` follows semver (e.g., 1.0.0)

### System Prompt Validation
- ✅ Length: 100-10000 characters
- ✅ No malicious content (checked via Claude API)
- ✅ Passes ethical review

### Optional Validations
- ⚠️ Warning if no examples provided
- ⚠️ Warning if no README provided
- ⚠️ Suggestion to add knowledge base for complex domains

## Ethical Review Process

After upload, each agent undergoes:

1. **Automated Checks**
   - Scans for harmful keywords
   - Checks against prohibited use cases
   - Validates safe_for_children claim

2. **AI Review** (using Claude)
   - Analyzes system prompt for harmful intent
   - Checks for privacy violations
   - Evaluates alignment with ethical guidelines

3. **Human Review** (for flagged agents)
   - Manual inspection by moderators
   - Approval or rejection with feedback

## Version Management

Sellers can update their agents:
- **Patch updates** (1.0.1): Bug fixes, prompt improvements
- **Minor updates** (1.1.0): New features, expanded knowledge
- **Major updates** (2.0.0): Significant changes to behavior

Buyers automatically get updates unless they opt-out.

## Distribution

Once approved:
1. Package is stored in secure cloud storage
2. Metadata indexed in database
3. Agent listed in marketplace
4. On purchase, agent is "activated" for buyer
5. Chat interface loads agent configuration

## Example Package Creation

```bash
# Directory structure
mkdir my-holiday-agent
cd my-holiday-agent

# Create required files
cat > agent.yaml << EOF
version: "1.0"
metadata:
  name: "Holiday Planning Expert"
  version: "1.0.0"
  author: "traveler123"
  description: "AI travel planner"
  category: "travel"
  price: 9.99
  currency: "USD"
EOF

cat > system_prompt.txt << EOF
You are a Holiday Planning Expert...
EOF

# Create optional directories
mkdir examples knowledge

# Package it
zip -r holiday-planner.sagent *

# Upload to Special Agents marketplace
```

## Benefits of This Format

1. **Human-readable**: YAML is easy to read and edit
2. **Extensible**: Can add new fields without breaking compatibility
3. **Portable**: ZIP archive works everywhere
4. **Versionable**: Git-friendly for tracking changes
5. **Standardized**: Clear structure for all agents
6. **Ethical**: Built-in ethical guidelines and review
7. **Future-proof**: Supports tools, knowledge bases, examples

## Future Enhancements

- **Agent SDK**: Python library to create/test packages locally
- **CLI tool**: `sagent create`, `sagent validate`, `sagent publish`
- **Marketplace API**: Programmatic package upload
- **Analytics**: Track agent usage and performance
- **A/B testing**: Test prompt variations
- **Fine-tuning**: Allow custom model fine-tuning (advanced tier)

## Comparison to Other Formats

| Feature | Special Agents (.sagent) | OpenAI GPTs | LangChain | HuggingFace |
|---------|-------------------------|-------------|-----------|-------------|
| Format | ZIP + YAML | JSON | Python | Model Card |
| Portability | ✅ High | ❌ Platform-locked | ⚠️ Code-based | ✅ High |
| Ethical Review | ✅ Built-in | ⚠️ Basic | ❌ None | ⚠️ Optional |
| Versioning | ✅ Semantic | ❌ No | ⚠️ Git-based | ✅ Git-based |
| Knowledge Base | ✅ Included | ⚠️ External | ✅ Integrated | ✅ Datasets |
| Tools Support | ✅ MCP | ✅ Actions | ✅ Full | ❌ Limited |
| Human-readable | ✅ YAML | ⚠️ JSON | ❌ Code | ✅ Markdown |

## License

This specification is open-source under MIT license. Anyone can implement `.sagent` package support in their platform.

---

**Special Agents Package Format v1.0**
Created: 2025-11-25
Status: Draft Specification
