# Business Glossary Web Application - Technical Specification

## Overview
A web application for managing and displaying business glossary terms for an insurance company, bridging the gap between business and technical stakeholders while being AI-agent friendly.

## Data Model

### Term Entity
```typescript
interface GlossaryTerm {
  id: string;                          // Unique identifier
  term: string;                        // Primary term name
  synonyms: string[];                  // Alternative names
  category: TermCategory;              // Classification
  status: TermStatus;                  // Lifecycle status
  
  // Three-layer definition structure
  businessDefinition: string;          // 1-2 sentences, plain language
  businessContext: string;             // 2-3 sentences, usage and importance
  technicalBridge?: string;            // Optional technical mapping
  
  // Metadata for data elements
  dataType?: DataType;                 // For fields: string, number, date, etc.
  allowedValues?: string[];            // For constrained/coded fields
  cardinality?: string;                // Relationship constraints
  isCalculated?: boolean;              // Derived vs. stored
  relatedTerms: string[];              // IDs of related terms
  
  // Governance
  owner: string;                       // Business owner
  steward: string;                     // Data steward
  lastReviewed: Date;
  version: number;
  
  // Metadata
  createdAt: Date;
  createdBy: string;
  updatedAt: Date;
  updatedBy: string;
  tags: string[];
}

enum TermCategory {
  PERSON_ENTITY = "Person/Entity",
  PRODUCT = "Product",
  POLICY = "Policy",
  CLAIM = "Claim",
  PAYMENT = "Payment",
  COVERAGE = "Coverage",
  RISK = "Risk",
  FINANCIAL = "Financial",
  DATE_TIME = "Date/Time",
  STATUS_CODE = "Status/Code",
  METRIC = "Metric",
  PROCESS = "Process",
  OTHER = "Other"
}

enum TermStatus {
  DRAFT = "Draft",
  REVIEW = "Under Review",
  APPROVED = "Approved",
  DEPRECATED = "Deprecated"
}

enum DataType {
  STRING = "String",
  NUMBER = "Number",
  DATE = "Date",
  DATETIME = "DateTime",
  BOOLEAN = "Boolean",
  CURRENCY = "Currency",
  PERCENTAGE = "Percentage"
}
```

## Core Features

### 1. Term Creation & Editing
**Form Structure:**
- Guided wizard with three steps matching the three-layer approach
- Step 1: Basic Info (term, synonyms, category)
- Step 2: Business Definition (with character guidance: 100-200 chars)
- Step 3: Business Context (with character guidance: 200-400 chars)
- Step 4: Technical Bridge (optional, 100-200 chars)
- Step 5: Metadata & Relationships

**Validation Rules:**
- Business definition required, must not contain the term itself (circular definition check)
- No undefined acronyms in business definition (acronym detector)
- Synonym uniqueness check across glossary
- Related terms must exist in glossary
- If allowedValues provided, require at least 2 values

**AI Writing Assistant Integration:**
- "Check Definition Quality" button that evaluates against checklist:
  - First sentence understandable to non-insurance person?
  - Avoids circular definitions?
  - Defines boundaries clearly?
  - Uses consistent pattern for category?
- "Suggest Improvements" feature using Claude API
- "Generate Technical Bridge" for auto-mapping from business definition

### 2. Term Display & Browse

**List View:**
- Filterable by category, status, owner
- Searchable across term, synonyms, all definition fields
- Sortable by term name, last updated, category
- Visual indicators for status (icons/colors)
- Bulk actions: export, change status, tag

**Detail View:**
- Three-layer structure clearly separated with visual hierarchy
- Collapsible technical bridge section
- Related terms as clickable links
- Relationship diagram for connected terms
- Synonym badges
- Version history timeline
- Comments/discussion thread per term

**AI-Friendly Export:**
- JSON export with structured format for LLM consumption
- Markdown export optimized for RAG systems
- CSV export for spreadsheet analysis
- API endpoint returning structured JSON

### 3. Quality Assurance Dashboard

**Quality Metrics Display:**
- Definition completeness score per term
- Terms missing business context
- Terms with circular definitions
- Terms not reviewed in 6+ months
- Orphaned terms (no relationships)
- Inconsistent patterns within categories

**Automated Checks:**
- Circular definition detector
- Acronym without expansion detector
- Sentence length analyzer (too short/too long)
- Pattern consistency checker within categories
- Synonym conflict detector

### 4. Relationship Visualizer

**Interactive Graph:**
- Node = term
- Edge = relationship
- Color-coded by category
- Hoverable for quick definition preview
- Click to navigate to term detail
- Filter by relationship type
- Zoom and pan functionality

### 5. Search & Discovery

**Smart Search Features:**
- Full-text search across all fields
- Synonym-aware search
- Category faceted search
- "Find similar terms" using semantic similarity
- "Terms used with..." showing co-occurring terms
- Recent searches saved per user

**AI-Powered Features:**
- "Explain this term in context of..." (uses Claude to provide custom explanations)
- "Compare terms" side-by-side view with AI highlighting differences
- "Find gaps" - suggest missing terms based on existing glossary

### 6. Collaboration Features

**Review Workflow:**
- Submit for review → Notify reviewers
- Comment and suggest changes
- Approve/Request changes/Reject
- Version control with diff view

**Discussion:**
- Comment threads per term
- @mentions for notifications
- Resolution status tracking

### 7. Import/Export

**Import Sources:**
- CSV with template mapping
- Excel with multi-sheet support
- JSON bulk import
- Copy from another glossary (merge strategy)

**Export Formats:**
- JSON (full structure, API-ready)
- Markdown (one file per term or combined)
- CSV (flattened for analysis)
- PDF report (formatted, printable)
- HTML static site

## User Interface Requirements

### Design Principles
- Clean, professional insurance industry aesthetic
- High readability: minimum 16px body text
- Clear visual hierarchy for three-layer structure
- Accessible (WCAG 2.1 AA compliant)
- Responsive: desktop-first, mobile-friendly

### Key Screens

**1. Home/Dashboard**
- Recent terms updated
- Terms needing review
- Quality metrics summary
- Quick search bar
- Category browse tiles

**2. Term List**
- Table view with columns: Term, Category, Status, Last Updated, Owner
- Filters sidebar: Category, Status, Owner, Tags
- Search bar with autocomplete
- Bulk action toolbar
- Create new term button (prominent)

**3. Term Detail**
- Header: Term name, synonyms, category badge, status badge
- Business Definition section (prominent, large text)
- Business Context section
- Technical Bridge section (collapsible)
- Metadata sidebar: owner, steward, dates, version
- Related terms section with visual links
- Actions: Edit, Delete, Export, Share, Comment
- Version history accordion

**4. Term Editor**
- Step-by-step wizard OR single-page form (user preference)
- Real-time character count and guidance
- AI assistant panel (collapsible)
- Save draft / Submit for review buttons
- Preview mode toggle

**5. Quality Dashboard**
- Metrics cards (terms needing review, quality score, completeness)
- Issue list table with filters
- Export quality report button
- Auto-check scheduler settings

**6. Relationship Graph**
- Full-screen graph visualization
- Control panel: filters, layout options, legend
- Search/highlight specific terms
- Export as image

## Technical Architecture

### Frontend Stack
- **Framework**: React 18+ with TypeScript
- **UI Components**: Tailwind CSS + shadcn/ui
- **State Management**: React Context + React Query for server state
- **Routing**: React Router v6
- **Forms**: React Hook Form + Zod validation
- **Rich Text**: TipTap or Lexical editor
- **Graph Viz**: D3.js or React Flow
- **Search**: Client-side Fuse.js or server-side full-text search

### Backend Stack (Recommendations)
- **API**: REST or GraphQL
- **Database**: PostgreSQL (full-text search, JSONB for metadata)
- **Storage**: Terms table, versions table, comments table, relationships table
- **Search Index**: PostgreSQL tsvector or Elasticsearch for large glossaries
- **Auth**: JWT-based authentication

### AI Integration Points
- **Quality Checker**: POST /api/terms/{id}/check-quality
- **Suggestion Engine**: POST /api/terms/{id}/suggest-improvements
- **Semantic Search**: POST /api/search/semantic with query
- **Gap Analysis**: POST /api/glossary/analyze-gaps
- **Generate Technical Bridge**: POST /api/terms/{id}/generate-technical

All AI endpoints should:
- Accept term data and return structured suggestions
- Use Claude API with specific prompts for each function
- Cache results for performance
- Include confidence scores

### Database Schema

```sql
-- Terms table
CREATE TABLE terms (
    id UUID PRIMARY KEY,
    term VARCHAR(255) NOT NULL UNIQUE,
    synonyms TEXT[],
    category VARCHAR(50),
    status VARCHAR(50),
    business_definition TEXT NOT NULL,
    business_context TEXT NOT NULL,
    technical_bridge TEXT,
    data_type VARCHAR(50),
    allowed_values TEXT[],
    cardinality VARCHAR(255),
    is_calculated BOOLEAN,
    owner VARCHAR(255),
    steward VARCHAR(255),
    last_reviewed DATE,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255),
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by VARCHAR(255),
    tags TEXT[],
    metadata JSONB
);

-- Full-text search index
CREATE INDEX terms_search_idx ON terms 
USING GIN(to_tsvector('english', 
    term || ' ' || 
    COALESCE(business_definition, '') || ' ' || 
    COALESCE(business_context, '')
));

-- Relationships table
CREATE TABLE term_relationships (
    id UUID PRIMARY KEY,
    from_term_id UUID REFERENCES terms(id),
    to_term_id UUID REFERENCES terms(id),
    relationship_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Versions table (for history)
CREATE TABLE term_versions (
    id UUID PRIMARY KEY,
    term_id UUID REFERENCES terms(id),
    version INTEGER,
    term_data JSONB,
    changed_by VARCHAR(255),
    changed_at TIMESTAMP DEFAULT NOW(),
    change_notes TEXT
);

-- Comments table
CREATE TABLE term_comments (
    id UUID PRIMARY KEY,
    term_id UUID REFERENCES terms(id),
    user_id VARCHAR(255),
    comment TEXT,
    parent_comment_id UUID REFERENCES term_comments(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## API Endpoints

### Terms
- `GET /api/terms` - List terms (with filters, pagination)
- `GET /api/terms/{id}` - Get term details
- `POST /api/terms` - Create term
- `PUT /api/terms/{id}` - Update term
- `DELETE /api/terms/{id}` - Delete term
- `GET /api/terms/{id}/versions` - Get version history
- `GET /api/terms/{id}/relationships` - Get related terms

### Search
- `GET /api/search?q={query}` - Full-text search
- `POST /api/search/semantic` - Semantic similarity search
- `GET /api/search/suggestions?q={query}` - Autocomplete

### Quality
- `GET /api/quality/dashboard` - Quality metrics
- `POST /api/terms/{id}/check-quality` - Run quality checks
- `GET /api/quality/issues` - List quality issues

### AI Features
- `POST /api/ai/check-definition` - Check definition quality
- `POST /api/ai/suggest-improvements` - Get improvement suggestions
- `POST /api/ai/generate-technical-bridge` - Auto-generate technical mapping
- `POST /api/ai/explain-context` - Contextual explanation

### Export/Import
- `POST /api/export` - Export glossary (format in body)
- `POST /api/import` - Import terms (with file upload)
- `GET /api/export/{exportId}` - Download export file

## Implementation Phases

### Phase 1: Core CRUD (Week 1-2)
- Term creation, editing, deletion
- List and detail views
- Basic search and filtering
- Categories and statuses

### Phase 2: Quality Features (Week 3)
- Validation rules implementation
- Quality checker integration
- Quality dashboard
- Automated checks

### Phase 3: Collaboration (Week 4)
- Comments and discussions
- Review workflow
- Version history
- User notifications

### Phase 4: Advanced Features (Week 5-6)
- Relationship visualizer
- AI-powered suggestions
- Semantic search
- Import/export functionality

### Phase 5: Polish & Deploy (Week 7)
- UI/UX refinement
- Performance optimization
- Documentation
- Deployment setup

## Configuration Files

### Environment Variables
```bash
# Frontend
REACT_APP_API_URL=http://localhost:3000/api
REACT_APP_CLAUDE_API_KEY=your-claude-api-key

# Backend
DATABASE_URL=postgresql://user:pass@localhost:5432/glossary
CLAUDE_API_KEY=your-claude-api-key
JWT_SECRET=your-jwt-secret
PORT=3000
```

### Quality Check Rules Configuration
```json
{
  "rules": {
    "circularDefinition": {
      "enabled": true,
      "severity": "error"
    },
    "minBusinessDefinitionLength": {
      "enabled": true,
      "threshold": 50,
      "severity": "warning"
    },
    "maxBusinessDefinitionLength": {
      "enabled": true,
      "threshold": 300,
      "severity": "warning"
    },
    "undefinedAcronyms": {
      "enabled": true,
      "severity": "warning",
      "allowList": ["ID", "URL", "API"]
    },
    "patternConsistency": {
      "enabled": true,
      "severity": "info"
    }
  }
}
```

## Deployment Considerations

### Frontend Deployment
- Build optimized production bundle
- Deploy to Vercel, Netlify, or AWS S3 + CloudFront
- Configure environment variables
- Enable HTTPS

### Backend Deployment
- Containerize with Docker
- Deploy to AWS ECS, Google Cloud Run, or Heroku
- Configure database connection pooling
- Set up monitoring and logging
- Enable CORS for frontend domain

### Database
- Use managed PostgreSQL (AWS RDS, Google Cloud SQL)
- Configure automated backups
- Set up read replicas for scale
- Enable connection pooling

## Testing Requirements

### Unit Tests
- Component tests for React components
- Service tests for business logic
- Validation rule tests

### Integration Tests
- API endpoint tests
- Database integration tests
- AI feature integration tests

### E2E Tests
- Critical user flows: create term, search, edit
- Review workflow
- Export/import

## Documentation Deliverables

1. **User Guide**: How to use the glossary application
2. **Admin Guide**: Configuration and management
3. **API Documentation**: OpenAPI/Swagger spec
4. **Development Setup**: How to run locally
5. **Deployment Guide**: Production deployment steps
6. **Quality Guidelines**: How to write good definitions (this document)

## Success Metrics

- **Adoption**: % of data elements documented
- **Quality**: Average quality score across terms
- **Usage**: Search queries per day, page views
- **Timeliness**: Average review cycle time
- **Completeness**: % terms with all three layers defined
- **Relationships**: Average connections per term

---

## Notes for Claude Code

When implementing this specification:

1. **Start with the data model** - Create TypeScript interfaces first
2. **Build the form first** - The term creation/edit form is the heart of the app
3. **Implement validation incrementally** - Start with required fields, add sophisticated checks later
4. **Mock the AI features initially** - Use placeholder responses until Claude API integration
5. **Prioritize the three-layer display** - This is the core value proposition
6. **Use component libraries** - shadcn/ui provides excellent insurance-appropriate components
7. **Consider SQLite for development** - Easier local setup, PostgreSQL for production
8. **Test the quality checker thoroughly** - This is a key differentiator

The goal is a professional, usable tool that insurance business analysts and data engineers both love using.