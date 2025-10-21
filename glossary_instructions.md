# Business Glossary Development Instructions

## Project Overview
You are helping develop a business glossary for an insurance domain. This glossary serves as the bridge between business stakeholders and technical teams, and must be optimized for both human comprehension and AI agent processing.

## Your Core Responsibilities

1. **Write Clear Definitions**: Create business glossary entries that are immediately understandable to non-technical stakeholders while providing necessary technical context for developers and AI systems.

2. **Maintain Consistency**: Use consistent patterns and structures across all glossary entries to enable pattern recognition by AI agents and easy scanning by humans.

3. **Ensure Completeness**: Every definition should stand alone without requiring readers to look up other undefined terms first.

## Definition Structure

Use this three-layer approach for every glossary term:

### Layer 1: Business Definition (Required)
- **Length**: 1-2 sentences
- **Purpose**: What does this mean in plain language?
- **Audience**: Non-technical business users
- **Test**: Could a new hire understand this on day one?

**Pattern for common term types**:
- Person/Entity: "The [person/organization] who/that [role/function]..."
- Date: "The date when [specific event occurs]..."
- Amount: "The [monetary value/quantity] of [what it measures]..."
- Status: "The current state of [entity] indicating [meaning]..."

### Layer 2: Business Context (Required)
- **Length**: 2-3 sentences
- **Purpose**: Why does this matter? How is it used?
- **Include**: Business processes, decision impacts, relationships to other concepts
- **Include**: Cardinality when relevant (one-to-one, one-to-many, etc.)

### Layer 3: Technical Bridge (Optional)
- **Length**: 1-2 sentences
- **Purpose**: System mapping for technical teams
- **Include only if**: The term is frequently used in technical work
- **Format**: "Stored in [TABLE.COLUMN]. Related to [OTHER_TABLES]."

## Writing Rules

### Do:
- ✅ Start with what the term IS before explaining what it does
- ✅ Use "Explain to a New Hire" test - avoid undefined jargon
- ✅ Be specific about scope and boundaries
- ✅ List synonyms explicitly: "Term (also called Synonym1, Synonym2):"
- ✅ Specify allowed values for coded fields
- ✅ Distinguish between events (real-world) and records (system entries)
- ✅ Note whether values are stored directly or calculated
- ✅ Use consistent sentence patterns for similar term types

### Don't:
- ❌ Use circular definitions ("Premium Amount: The amount of the premium")
- ❌ Start with technical details before business meaning
- ❌ Use acronyms without explanation
- ❌ Define terms using other undefined terms
- ❌ Be vague about temporal concepts ("as of when?")
- ❌ Mix event descriptions with record descriptions

## Insurance-Specific Guidance

### Handle Temporal Data Carefully
Insurance data is often time-dependent. Be explicit:
- "Current Premium: The premium amount in effect as of today"
- "Original Premium: The premium amount when the policy was first issued"

### Distinguish Common Ambiguities
- Claim = request, payment, or entire lifecycle? Be specific.
- Insured vs Policyholder - choose one primary term, note synonyms
- Date of loss vs date of claim vs date of report - clarify exactly which event

### Specify Relationships
Help both humans and AI understand data connections:
- "Each policy must have exactly one policyholder, but a policyholder may have multiple policies."
- "A claim may have multiple payments over time."

## Quality Checklist

Before submitting any definition, verify:
- [ ] First sentence is understandable to non-insurance person
- [ ] Technical teams can find what they need
- [ ] No unexplained acronyms
- [ ] AI agent has enough context to join related data correctly
- [ ] Term defined without requiring other term lookups first
- [ ] Scope and boundaries are clear
- [ ] Synonyms are explicitly noted
- [ ] Dates specify exactly which event they represent
- [ ] Relationships and cardinality are mentioned when relevant

## Example Template

```
**[TERM NAME]**

*Business Definition*: [1-2 sentences in plain language describing what this is]

*Business Context*: [2-3 sentences explaining why it matters, how it's used in business processes, what decisions depend on it, and relationships to other concepts]

*Technical Details*: [Optional - 1-2 sentences about system storage and related tables]

*Synonyms*: [Alternative terms if applicable]

*Allowed Values*: [If applicable - list of valid values]
```

## Full Example Entry

**Deductible**

*Business Definition*: The amount a policyholder must pay out-of-pocket before insurance coverage begins paying for a covered loss.

*Business Context*: Deductibles help control insurance costs by having policyholders share in smaller losses. Higher deductibles typically result in lower premiums. The deductible is applied per claim or per policy period depending on policy terms. Once the deductible is met, the insurer pays covered expenses according to the policy limits and coinsurance provisions.

*Technical Details*: Stored in POLICY.DEDUCTIBLE_AMT. Related to CLAIM.DEDUCTIBLE_APPLIED which tracks the portion of the deductible used for each claim. Measured in the policy's currency denomination.

*Synonyms*: Out-of-pocket minimum (less common)

---

## When Working on Code

If you're writing code that processes business glossary data:
1. Ensure data models reflect the three-layer structure
2. Include validation for required vs optional fields
3. Implement synonym tracking and search
4. Support relationship mapping between terms
5. Enable temporal queries for time-dependent definitions
6. Provide clear error messages referencing business concepts, not just technical field names

## Questions to Ask

When clarifying requirements, prioritize:
- "What business problem does this term help solve?"
- "Who makes decisions based on this data?"
- "How does this relate to [similar term]?"
- "Is this value stored directly or calculated?"
- "What event does this date represent?"
- "Are there regional or product-line variations in meaning?"

---

**Remember**: You're building a universal translator. Every definition should work for the claims adjuster, the data engineer, and the AI agent processing insurance data.