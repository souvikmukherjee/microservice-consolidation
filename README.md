# Microservice Consolidation Platform 🚀

An AI-powered platform that automates the analysis, planning, and execution of microservice consolidation. Transform multiple microservices into unified Spring Boot applications using intelligent conflict detection and automated merge strategies.

## 📖 Documentation

- **📋 [Detailed Design & Architecture](./DESIGN.md)** - Complete system design with Mermaid diagrams
- **🎯 [Project Planning & Tasks](./microservices-consolidation/README.md)** - Taskmaster-AI setup and current project state

---

## 🚀 Quick Start for Mac Users

### Prerequisites Installation

#### 1. Install Homebrew (if not already installed)
```bash
# Install Homebrew - the package manager for macOS
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add Homebrew to your PATH (follow the instructions shown after installation)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc
```

#### 2. Install Java 21
```bash
# Install Java 21 using Homebrew
brew install openjdk@21

# Link Java 21 to be available system-wide
sudo ln -sfn /opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-21.jdk

# Add Java to your PATH
echo 'export JAVA_HOME=/opt/homebrew/opt/openjdk@21' >> ~/.zshrc
echo 'export PATH="$JAVA_HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Verify Java installation
java -version
# Should show: openjdk version "21.x.x"
```

#### 3. Install Python 3.10+
```bash
# Install Python using Homebrew
brew install python@3.11

# Verify Python installation
python3 --version
# Should show: Python 3.11.x

# Install pip if not available
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
rm get-pip.py
```

#### 4. Install Node.js and npm
```bash
# Install Node.js using Homebrew
brew install node

# Verify installation
node --version  # Should show v20.x.x or higher
npm --version   # Should show 9.x.x or higher
```

#### 5. Install Git (if not already installed)
```bash
# Install Git
brew install git

# Configure Git (replace with your information)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## 🛠️ Project Setup

### 1. Clone and Setup Repository
```bash
# Clone the repository
git clone https://github.com/souvikmukherjee/microservice-consolidation.git
cd microservice-consolidation

# Verify you're in the correct directory
pwd
# Should show: /path/to/microservice-consolidation
```

### 2. Setup API Keys
```bash
# Create environment file for API keys
cp .env.example .env

# Edit the .env file with your API keys
nano .env
```

Add your API keys to the `.env` file:
```bash
# Required for AI-powered analysis
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional - for research capabilities
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# GitHub integration (optional)
GITHUB_TOKEN=your_github_token_here
```

**💡 How to get API keys:**
- **OpenAI**: Visit [platform.openai.com](https://platform.openai.com/api-keys)
- **Anthropic**: Visit [console.anthropic.com](https://console.anthropic.com/)
- **Perplexity**: Visit [perplexity.ai](https://www.perplexity.ai/settings/api)
- **GitHub**: Visit [github.com/settings/tokens](https://github.com/settings/tokens)

### 3. Setup Java Backend
```bash
# Navigate to Spring Boot backend
cd springboot-backend

# Make gradlew executable
chmod +x gradlew

# Build the project
./gradlew build

# Verify build was successful
ls build/libs/
# Should show: springboot-backend-0.0.1-SNAPSHOT.jar

# Return to project root
cd ..
```

### 4. Setup Python Environment
```bash
# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install compatibility engine dependencies
cd compatibility-engine
pip install -r requirements.txt
cd ..

# Install GitHub integration dependencies  
cd github-integration
pip install -r requirements.txt
cd ..

# Verify installations
python -c "import langchain; print('LangChain installed successfully')"
python -c "import typer; print('Typer installed successfully')"
```

### 5. Setup Frontend (Optional)
```bash
# Navigate to frontend directory
cd microservices-consolidation

# Install Node.js dependencies
npm install

# Build the frontend
npm run build

# Return to project root
cd ..
```

---

## 🎯 Running the Platform

### Option 1: Quick Demo Run
```bash
# Ensure you're in the project root and virtual environment is active
source venv/bin/activate

# Run the complete consolidation pipeline
cd iMCE
python consolidation_orchestrator.py

# This will:
# 1. Discover microservices in repos/ directory
# 2. Analyze API and dependency conflicts
# 3. Generate merge strategy
# 4. Create consolidated Spring Boot application
```

### Option 2: Step-by-Step Analysis

#### Step 1: Analyze API Conflicts
```bash
# Activate virtual environment
source venv/bin/activate

# Run API conflict analysis
cd compatibility-engine
python -m typer api_conflict.py run --repo1=../repos/spring-boot-microservices --repo2=../repos/dubbo

# View results
cat api_conflict_results.json
```

#### Step 2: Analyze Dependencies
```bash
# Run dependency analysis
python -m typer dependency_conflict.py run --repo1=../repos/spring-boot-microservices --repo2=../repos/dubbo

# View results  
cat dependency_conflict_results.json
```

#### Step 3: Full Consolidation
```bash
# Run complete consolidation
cd ../iMCE
python consolidation_orchestrator.py

# Check generated application
ls -la consolidated-service/ms-imce/
```

### Option 3: Frontend Development Server
```bash
# Start the Next.js development server
cd microservices-consolidation
npm run dev

# Visit http://localhost:3000 in your browser
```

---

## 📁 Understanding the Output

After running the consolidation, you'll find:

### Generated Files
```
consolidated-service/ms-imce/               # ← Main consolidated Spring Boot app
├── src/main/java/com/imce/app/
│   ├── MsImceApplication.java             # ← Spring Boot main class
│   ├── controller/                        # ← REST controllers (6 files)
│   ├── service/                          # ← Business logic (429 files)
│   ├── repository/                       # ← Data access (19 files)
│   ├── model/                           # ← Domain models (96 files)
│   ├── config/                          # ← Configuration (316 files)
│   └── ...
├── src/main/resources/
│   ├── application.properties           # ← Merged configuration
│   └── ...
├── build.gradle                        # ← Gradle build file
└── gradlew                             # ← Gradle wrapper

api_conflict_results.json               # ← API conflict analysis
dependency_conflict_results.json        # ← Dependency analysis  
consolidation_merge_plan.json          # ← AI-generated merge strategy
consolidation_progress.md              # ← Mermaid visualization
```

### Running the Consolidated Application
```bash
# Navigate to the generated application
cd consolidated-service/ms-imce

# Run the consolidated Spring Boot application
./gradlew bootRun

# The application will start on http://localhost:8080
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Java Issues
```bash
# If Java is not found
echo $JAVA_HOME
# Should show: /opt/homebrew/opt/openjdk@21

# If gradlew permission denied
chmod +x gradlew

# If build fails
./gradlew clean build --stacktrace
```

#### Python Issues
```bash
# If virtual environment issues
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# If package installation fails
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# If import errors
python -c "import sys; print(sys.path)"
```

#### API Key Issues
```bash
# Verify environment variables are loaded
source .env
echo $OPENAI_API_KEY  # Should not be empty

# Test API connectivity
python -c "
import openai
import os
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
print('OpenAI API key is valid')
"
```

#### Memory/Performance Issues
```bash
# If running out of memory during analysis
export JAVA_OPTS="-Xmx4g -Xms2g"

# If Python process is slow
export PYTHONUNBUFFERED=1
```

---

## 📊 Example Usage Scenarios

### Scenario 1: Analyze Existing Microservices
```bash
# Place your microservice repositories in repos/ directory
mkdir -p repos
cp -r /path/to/your/microservices/* repos/

# Run analysis
source venv/bin/activate
cd iMCE
python consolidation_orchestrator.py
```

### Scenario 2: Test with Sample Data
```bash
# The project includes sample microservices for testing
ls repos/
# Should show: dubbo/ spring-boot-microservices/

# Run with sample data
cd iMCE
python consolidation_orchestrator.py
```

### Scenario 3: Custom Analysis
```bash
# Run only conflict analysis
cd compatibility-engine
python -m typer api_conflict.py run --repo1=../repos/service1 --repo2=../repos/service2 --output=custom_results.json
```

---

## 🎓 Learning the System

### Understanding the Architecture
1. **Read the Design Document**: [DESIGN.md](./DESIGN.md) contains detailed architecture diagrams
2. **Explore the Code**: Start with `iMCE/consolidation_orchestrator.py`
3. **Check the Results**: Examine generated JSON files and consolidated application

### Key Components to Understand
- **iMCE Orchestrator**: Main coordination engine
- **Compatibility Engine**: AI-powered conflict analysis  
- **Spring Boot Backend**: Static code analysis
- **File Classification**: How Java files are organized

### Customization Points
- **AI Models**: Modify in compatibility engine configuration
- **File Classification**: Update `classify_java_file()` function
- **Merge Strategies**: Customize in `generate_merge_plan()`

---

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Code formatting
black .
isort .
```

### Submitting Changes
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "Add your feature"`
4. Push to branch: `git push origin feature/your-feature`
5. Submit a Pull Request

---

## 📚 Additional Resources

- **[Detailed Architecture](./DESIGN.md)** - System design and component interactions
- **[Project Planning](./microservices-consolidation/README.md)** - Task management with Taskmaster-AI
- **[API Documentation](./api-docs/)** - Detailed API reference (if available)
- **[Contributing Guide](./CONTRIBUTING.md)** - Development guidelines
- **[Changelog](./CHANGELOG.md)** - Version history and updates

---

## ❓ Support

If you encounter issues:

1. **Check the logs**: Look for error messages in console output
2. **Verify setup**: Ensure all prerequisites are correctly installed
3. **Check API keys**: Confirm your API keys are valid and properly configured
4. **Review documentation**: Check [DESIGN.md](./DESIGN.md) for technical details
5. **Open an issue**: Create a GitHub issue with detailed error information

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

## 🌟 Acknowledgments

- **LangChain** for AI orchestration framework
- **Spring Boot** for Java microservice foundation  
- **OpenAI & Anthropic** for LLM capabilities
- **Taskmaster-AI** for project management
- **Mermaid.js** for architecture visualization

---

**Happy Consolidating! 🚀**

Transform your microservice complexity into unified, maintainable applications with the power of AI.