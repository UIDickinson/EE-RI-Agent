// EE Research Scout Neo4j Knowledge Graph Schema
// Define constraints and indexes for optimal performance

// ============================================================================
// CONSTRAINTS (Unique identifiers)
// ============================================================================

// Query nodes
CREATE CONSTRAINT query_id IF NOT EXISTS
FOR (q:Query) REQUIRE q.id IS UNIQUE;

// Paper nodes
CREATE CONSTRAINT paper_id IF NOT EXISTS
FOR (p:Paper) REQUIRE p.id IS UNIQUE;

// Patent nodes
CREATE CONSTRAINT patent_id IF NOT EXISTS
FOR (p:Patent) REQUIRE p.id IS UNIQUE;

// Component nodes
CREATE CONSTRAINT component_id IF NOT EXISTS
FOR (c:Component) REQUIRE c.id IS UNIQUE;

// Technology nodes
CREATE CONSTRAINT tech_id IF NOT EXISTS
FOR (t:Technology) REQUIRE t.id IS UNIQUE;

// Manufacturer nodes
CREATE CONSTRAINT mfr_id IF NOT EXISTS
FOR (m:Manufacturer) REQUIRE m.name IS UNIQUE;

// Application nodes
CREATE CONSTRAINT app_id IF NOT EXISTS
FOR (a:Application) REQUIRE a.name IS UNIQUE;

// ============================================================================
// INDEXES (For faster lookups)
// ============================================================================

// Query indexes
CREATE INDEX query_timestamp IF NOT EXISTS
FOR (q:Query) ON (q.timestamp);

CREATE INDEX query_text IF NOT EXISTS
FOR (q:Query) ON (q.text);

// Paper indexes
CREATE INDEX paper_year IF NOT EXISTS
FOR (p:Paper) ON (p.year);

CREATE INDEX paper_title IF NOT EXISTS
FOR (p:Paper) ON (p.title);

// Patent indexes
CREATE INDEX patent_filing_date IF NOT EXISTS
FOR (p:Patent) ON (p.filing_date);

CREATE INDEX patent_office IF NOT EXISTS
FOR (p:Patent) ON (p.office);

CREATE INDEX patent_status IF NOT EXISTS
FOR (p:Patent) ON (p.status);

// Component indexes
CREATE INDEX component_part_number IF NOT EXISTS
FOR (c:Component) ON (c.part_number);

CREATE INDEX component_category IF NOT EXISTS
FOR (c:Component) ON (c.category);

CREATE INDEX component_lifecycle IF NOT EXISTS
FOR (c:Component) ON (c.lifecycle);

CREATE INDEX component_trl IF NOT EXISTS
FOR (c:Component) ON (c.trl);

// Technology indexes
CREATE INDEX tech_trl IF NOT EXISTS
FOR (t:Technology) ON (t.trl);

CREATE INDEX tech_maturity IF NOT EXISTS
FOR (t:Technology) ON (t.maturity);

// ============================================================================
// SAMPLE DATA STRUCTURE (for reference)
// ============================================================================

// Example Query node
// CREATE (q:Query {
//   id: 'query_12345',
//   text: 'Find GaN power ICs for automotive',
//   timestamp: datetime(),
//   focus_areas: ['power_management', 'automotive'],
//   depth: 'deep'
// })

// Example Paper node
// CREATE (p:Paper {
//   id: 'paper_doi_123',
//   doi: '10.1109/example.2024',
//   title: 'Advanced GaN Power Conversion',
//   authors: ['Smith, J.', 'Doe, A.'],
//   year: 2024,
//   abstract: '...',
//   url: 'https://...'
// })

// Example Patent node
// CREATE (pt:Patent {
//   id: 'EP1234567B1',
//   patent_number: 'EP1234567B1',
//   title: 'GaN Power IC Design',
//   applicant: 'Infineon Technologies',
//   filing_date: date('2022-01-15'),
//   status: 'Granted',
//   office: 'EPO',
//   region: 'EU'
// })

// Example Component node
// CREATE (c:Component {
//   id: 'TPS54620',
//   part_number: 'TPS54620',
//   manufacturer: 'Texas Instruments',
//   category: 'Buck Converter',
//   trl: 9,
//   lifecycle: 'Active',
//   specifications: '{...}'
// })

// Example Technology node
// CREATE (t:Technology {
//   id: 'gan_power',
//   name: 'Gallium Nitride Power Conversion',
//   trl: 8,
//   maturity: 'Production',
//   description: '...'
// })

// Example Manufacturer node
// CREATE (m:Manufacturer {
//   name: 'Infineon Technologies',
//   region: 'EU',
//   headquarters: 'Germany'
// })

// Example Application node
// CREATE (a:Application {
//   name: 'Automotive Power Systems',
//   domain: 'Automotive',
//   description: '...'
// })

// ============================================================================
// RELATIONSHIP DEFINITIONS
// ============================================================================

// Research relationships
// (Query)-[:FOUND_PAPER]->(Paper)
// (Query)-[:FOUND_PATENT]->(Patent)
// (Query)-[:FOUND_COMPONENT]->(Component)

// Citation relationships
// (Paper)-[:CITES]->(Patent)
// (Paper)-[:CITES]->(Paper)
// (Patent)-[:CITES_PRIOR_ART]->(Patent)

// Implementation relationships
// (Patent)-[:IMPLEMENTS]->(Technology)
// (Component)-[:IMPLEMENTS]->(Technology)
// (Patent)-[:DESCRIBES_COMPONENT]->(Component)

// Analysis relationships
// (Paper)-[:DISCUSSES]->(Technology)
// (Paper)-[:ANALYZES]->(Component)
// (Paper)-[:COMPARES]->(Component)

// Manufacturing relationships
// (Component)-[:MANUFACTURED_BY]->(Manufacturer)
// (Manufacturer)-[:LOCATED_IN]->(Region)

// Application relationships
// (Component)-[:SUITABLE_FOR]->(Application)
// (Technology)-[:ENABLES]->(Application)

// Alternative relationships
// (Component)-[:ALTERNATIVE_TO]->(Component)
// (Technology)-[:ALTERNATIVE_TO]->(Technology)

// Evolution relationships
// (Technology)-[:EVOLVED_FROM]->(Technology)
// (Component)-[:SUCCESSOR_OF]->(Component)

// ============================================================================
// USEFUL QUERIES (Examples)
// ============================================================================

// Find all components for a specific application
// MATCH (c:Component)-[:SUITABLE_FOR]->(a:Application {name: 'Automotive Power Systems'})
// WHERE c.lifecycle = 'Active' AND c.trl >= 8
// RETURN c.part_number, c.manufacturer, c.trl
// ORDER BY c.trl DESC

// Trace innovation path: Paper → Patent → Component
// MATCH path = (paper:Paper)-[:CITES]->(patent:Patent)-[:IMPLEMENTS]->(tech:Technology)<-[:IMPLEMENTS]-(comp:Component)
// WHERE paper.year >= 2020
// RETURN path
// LIMIT 10

// Find alternative components
// MATCH (c1:Component {part_number: 'TPS54620'})-[:ALTERNATIVE_TO]-(c2:Component)
// WHERE c2.lifecycle = 'Active'
// RETURN c2.part_number, c2.manufacturer, c2.trl

// Get component with full context
// MATCH (c:Component {part_number: 'TPS54620'})
// OPTIONAL MATCH (c)-[:MANUFACTURED_BY]->(m:Manufacturer)
// OPTIONAL MATCH (c)-[:SUITABLE_FOR]->(a:Application)
// OPTIONAL MATCH (c)<-[:DISCUSSES]-(paper:Paper)
// OPTIONAL MATCH (c)<-[:DESCRIBES_COMPONENT]-(patent:Patent)
// RETURN c, m, collect(DISTINCT a) as applications,
//        collect(DISTINCT paper) as papers,
//        collect(DISTINCT patent) as patents

// Find trending technologies by paper count
// MATCH (tech:Technology)<-[:DISCUSSES]-(paper:Paper)
// WHERE paper.year >= 2022
// WITH tech, count(paper) as paper_count
// RETURN tech.name, paper_count, tech.trl
// ORDER BY paper_count DESC
// LIMIT 10