```bash
#!/bin/bash

echo "🔧 Setting up EE Research Scout (ROMA Extension)"

# Check if ROMA submodule exists
if [ ! -d "roma" ]; then
    echo "📥 Cloning ROMA framework..."
    git submodule add https://github.com/sentient-agi/ROMA.git roma
    git submodule update --init --recursive
fi

# Setup ROMA
echo "🚀 Setting up ROMA framework..."
cd roma
./setup.sh --docker
cd ..

# Install additional dependencies
echo "📦 Installing EE-specific dependencies..."
pip install -r requirements.txt

# Setup databases
echo "🗄️  Setting up databases..."
docker-compose up -d postgres neo4j

# Wait for databases
echo "⏳ Waiting for databases to be ready..."
sleep 10

# Initialize database schemas
echo "🔨 Initializing database schemas..."
psql -h localhost -U postgres -d ee_scout -f database/init_postgres.sql
docker exec neo4j cypher-shell -u neo4j -p changeme -f /var/lib/neo4j/import/schema.cypher

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "  Backend: cd roma && docker-compose up"
echo "  Frontend: cd frontend && npm install && npm run dev"
echo ""
echo "Access the chat interface at http://localhost:3000"