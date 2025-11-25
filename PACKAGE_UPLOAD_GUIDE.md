# Agent Package Upload Guide

## Overview

Special Agents supports two methods for creating AI agents:

1. **Simple Form** (Quick): For basic agents without advanced features
2. **.sagent Package** (Professional): Full-featured with examples, knowledge base, and documentation

This guide focuses on the `.sagent` package format.

## Why Use .sagent Packages?

### Benefits:
- ✅ Version control for your agents
- ✅ Include knowledge bases and reference materials
- ✅ Provide example conversations for buyers
- ✅ Professional documentation
- ✅ Portable across platforms
- ✅ Shows buyers you're serious about quality

### When to Use:
- Complex agents with specialized knowledge
- Agents that need reference data
- Professional marketplace listings
- Agents you plan to update/improve over time

## Creating a .sagent Package

### 1. Create Directory Structure

```bash
mkdir my-agent
cd my-agent

# Create required files
touch agent.yaml
touch system_prompt.txt

# Create optional directories
mkdir examples
mkdir knowledge
touch README.md
```

### 2. Write agent.yaml (REQUIRED)

This is your agent's metadata and configuration:

```yaml
version: "1.0"

metadata:
  name: "Your Agent Name"
  version: "1.0.0"
  author: "your_username"
  description: "What your agent does"
  category: "travel"  # or productivity, education, health, finance, creative
  tags:
    - tag1
    - tag2
  price: 9.99
  currency: "USD"
  license: "MIT"

agent:
  model: "claude-3-5-sonnet-20241022"
  temperature: 0.7
  max_tokens: 4096
  tone: "friendly"
  languages:
    - en

capabilities:
  strengths:
    - "What your agent is good at"
    - "Another strength"
  limitations:
    - "What it cannot do"

ethics:
  safe_for_children: true
  data_collection: false
  privacy_preserving: true
  harmful_use_prevention: true
```

### 3. Write system_prompt.txt (REQUIRED)

This defines your agent's behavior:

```
You are a [ROLE] AI agent. Your role is to help users [PURPOSE].

EXPERTISE:
- List your areas of expertise
- Be specific about what you know

PERSONALITY:
- How you interact with users
- Your communication style

WORKFLOW:
1. Step-by-step process you follow
2. Questions you ask
3. How you provide value

CONSTRAINTS:
- What you cannot do
- Important limitations
- Safety considerations

RESPONSE FORMAT:
- How you structure responses
- What sections you use
```

### 4. Add Examples (OPTIONAL)

Create `examples/example1.yaml`:

```yaml
conversation:
  - role: user
    content: "User's question"

  - role: assistant
    content: |
      Your agent's response
```

### 5. Add Knowledge Base (OPTIONAL)

Create files in `knowledge/`:
- `data.txt` - Reference data
- `context.md` - Background information
- Any text files your agent needs

### 6. Add README.md (OPTIONAL)

Write documentation for buyers:

```markdown
# Agent Name

Brief description

## What I Can Do
- Feature 1
- Feature 2

## Best For
- Use case 1
- Use case 2

## Example Questions
- "Example question 1"
- "Example question 2"
```

### 7. Package It

Using Python (works everywhere):

```bash
cd ..
python3 -m zipfile -c my-agent.sagent my-agent/
```

Or using zip command (if available):

```bash
zip -r my-agent.sagent my-agent/
```

## Uploading Your Package

1. **Login as a Seller**
   - Register with "I'm a seller" checked
   - Or existing account must be seller

2. **Navigate to Upload**
   - Click "Upload Package" in navigation
   - Or go to `/agents/upload-package`

3. **Select Your File**
   - Choose your `.sagent` or `.zip` file
   - Max size: 50MB

4. **Validation**
   - System automatically validates your package
   - Shows errors if validation fails
   - Shows warnings for optional improvements

5. **Ethical Review**
   - If valid, agent is submitted for review
   - Status: "Pending Review"
   - Typically reviewed within 24-48 hours

6. **Approval**
   - Once approved, agent appears in marketplace
   - You can track purchases and reviews

## Validation Rules

Your package must pass these checks:

### Required:
- ✅ `agent.yaml` exists and is valid YAML
- ✅ `system_prompt.txt` exists (100-50,000 characters)
- ✅ Package size < 50MB
- ✅ Agent name is 3-100 characters
- ✅ Valid category (productivity/education/travel/health/finance/creative)
- ✅ Price >= 0
- ✅ Version follows semver (e.g., 1.0.0)

### Warnings (not required but recommended):
- ⚠️ No examples/ directory
- ⚠️ No README.md
- ⚠️ No knowledge base
- ⚠️ No tags specified

## Example Package

See `/examples/sample-packages/holiday-planner.sagent` for a complete example.

To examine it:

```bash
cd /home/fsiddiqui/special-agents/examples/sample-packages
python3 -m zipfile -e holiday-planner.sagent extracted/
ls -R extracted/
```

## Testing Your Package

Before uploading, you can validate locally using Python:

```python
from backend.app.agent_package import AgentPackageValidator

validator = AgentPackageValidator()
result = validator.validate_package('my-agent.sagent')

if result['valid']:
    print("✅ Package is valid!")
    print("Metadata:", result['metadata'])
else:
    print("❌ Validation errors:")
    for error in result['errors']:
        print(f"  - {error}")

if result['warnings']:
    print("⚠️ Warnings:")
    for warning in result['warnings']:
        print(f"  - {warning}")
```

## Package Updates

To update an existing agent:

1. Modify files in your agent directory
2. Update version in `agent.yaml` (e.g., 1.0.0 → 1.1.0)
3. Re-package and upload
4. Buyers get updates automatically (or can opt-out)

Version numbering:
- **Patch** (1.0.1): Bug fixes, small prompt improvements
- **Minor** (1.1.0): New features, expanded knowledge
- **Major** (2.0.0): Significant behavior changes

## Ethical Guidelines

Your agent will be reviewed for:

1. **Safety**: Does it promote safe, responsible behavior?
2. **Privacy**: Does it respect user privacy?
3. **Fairness**: Is it inclusive and unbiased?
4. **Honesty**: Does it avoid deception?
5. **Positive Impact**: Does it benefit humanity?

### Prohibited:
- ❌ Agents that help with illegal activities
- ❌ Agents that generate harmful content
- ❌ Agents that violate privacy
- ❌ Agents that spread misinformation
- ❌ Agents designed to manipulate users

### Encouraged:
- ✅ Educational agents
- ✅ Productivity tools
- ✅ Creative assistants
- ✅ Health and wellness support
- ✅ Financial literacy
- ✅ Travel and planning

## Troubleshooting

### "Package is not a valid ZIP file"
- Make sure you're creating a ZIP archive
- Try using `python3 -m zipfile` instead of zip command

### "Missing required file: agent.yaml"
- Check file is named exactly `agent.yaml` (lowercase)
- Make sure it's in the root of the ZIP, not in a subdirectory

### "Invalid YAML in agent.yaml"
- Use a YAML validator online
- Check for proper indentation (spaces, not tabs)
- Ensure strings with special characters are quoted

### "System prompt too short"
- Minimum 100 characters required
- Provide detailed instructions for your agent

### "Package validation failed: harmful keywords"
- Review your system prompt
- Remove references to prohibited activities
- Focus on positive, helpful use cases

## Need Help?

- Check the full specification: `/AGENT_PACKAGE_SPEC.md`
- View example package: `/examples/sample-packages/`
- Ask in the community forum (coming soon!)
- Contact support: support@special-agents.ai (placeholder)

## Quick Reference

Minimum viable package:

```
my-agent.sagent
├── agent.yaml          # Metadata (required)
└── system_prompt.txt   # Instructions (required)
```

Recommended package:

```
my-agent.sagent
├── agent.yaml          # Metadata
├── system_prompt.txt   # Instructions
├── examples/           # Sample conversations
│   └── example1.yaml
├── knowledge/          # Reference data
│   └── data.txt
└── README.md          # Documentation
```

## Status Flow

1. **Created** - Package uploaded successfully
2. **Pending Review** - Awaiting ethical review
3. **Approved** - Listed in marketplace
4. **Rejected** - Failed review (feedback provided)
5. **Active** - Available for purchase
6. **Inactive** - Removed by creator

Happy agent building! 🤖
