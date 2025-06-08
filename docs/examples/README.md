# FlutterCraft Examples

This directory contains example projects and tutorials demonstrating FlutterCraft's capabilities.

---

## 📚 Available Examples

### 🚀 Basic Flutter App
**Directory**: `basic-flutter-app/`
**Description**: Simple Flutter app creation with minimal configuration
**Use Case**: First-time users, quick prototyping

```bash
# Create a basic Flutter app
fluttercraft create \
  --name my_basic_app \
  --org com.example \
  --platforms android,ios \
  --backend none \
  --no-github
```

### 🔥 Firebase Integration
**Directory**: `firebase-integration/`
**Description**: Flutter app with Firebase backend setup
**Use Case**: Apps requiring authentication, database, and cloud functions

```bash
# Create Firebase-integrated app
fluttercraft create \
  --name my_firebase_app \
  --org com.example \
  --platforms android,ios,web \
  --backend firebase \
  --github
```

### 🌐 Multi-Platform Setup
**Directory**: `multi-platform-setup/`
**Description**: Flutter app targeting all platforms
**Use Case**: Cross-platform applications, desktop apps

```bash
# Create multi-platform app
fluttercraft create \
  --name my_multiplatform_app \
  --org com.example \
  --platforms android,ios,web,windows,macos,linux \
  --backend supabase \
  --github
```

### 🏢 Enterprise Setup
**Directory**: `enterprise-setup/`
**Description**: Enterprise-ready Flutter app with full CI/CD
**Use Case**: Production applications, team development

```bash
# Create enterprise app
fluttercraft create \
  --name enterprise_app \
  --org com.company \
  --platforms android,ios,web \
  --backend firebase \
  --github \
  --fvm
```

---

## 🎯 Quick Start Examples

### Minimal Setup
```bash
# Simplest possible setup
fluttercraft create --name simple_app --no-interactive
```

### Development Setup
```bash
# Development-focused setup
fluttercraft create \
  --name dev_app \
  --platforms android,ios,web \
  --fvm \
  --no-github
```

### Production Setup
```bash
# Production-ready setup
fluttercraft create \
  --name prod_app \
  --org com.yourcompany \
  --platforms android,ios,web \
  --backend firebase \
  --github \
  --fvm
```

---

## 📋 Example Scenarios

### Scenario 1: Hackathon Project
**Goal**: Quick MVP for a hackathon
**Time**: 30 minutes setup
**Command**:
```bash
fluttercraft create \
  --name hackathon_mvp \
  --platforms android,web \
  --backend firebase \
  --github
```

### Scenario 2: Client Project
**Goal**: Professional app for a client
**Time**: 1 hour setup
**Command**:
```bash
fluttercraft create \
  --name client_project \
  --org com.client \
  --platforms android,ios \
  --backend supabase \
  --github \
  --fvm
```

### Scenario 3: Open Source Project
**Goal**: Community-driven Flutter package
**Time**: 45 minutes setup
**Command**:
```bash
fluttercraft create \
  --name oss_package \
  --org io.github.username \
  --platforms android,ios,web,windows,macos,linux \
  --backend none \
  --github
```

### Scenario 4: Learning Project
**Goal**: Educational Flutter app
**Time**: 15 minutes setup
**Command**:
```bash
fluttercraft create \
  --name learning_app \
  --platforms android \
  --backend none \
  --no-github \
  --no-fvm
```

---

## 🔧 Advanced Configuration Examples

### Custom Organization
```bash
fluttercraft create \
  --name corporate_app \
  --org com.corporation.mobile \
  --platforms android,ios \
  --backend firebase
```

### Specific Destination
```bash
fluttercraft create \
  --name project_app \
  --dest ~/Projects/Flutter \
  --platforms android,ios,web
```

### Non-Interactive Mode
```bash
fluttercraft create \
  --name automated_app \
  --org com.example \
  --platforms android,ios \
  --backend firebase \
  --github \
  --no-interactive
```

---

## 🧪 Testing Examples

### Unit Testing Setup
After creating a project, set up comprehensive testing:

```bash
# Navigate to project
cd my_app

# Run tests
flutter test

# Run tests with coverage
flutter test --coverage

# View coverage report
genhtml coverage/lcov.info -o coverage/html
open coverage/html/index.html
```

### Integration Testing
```bash
# Run integration tests
flutter test integration_test/

# Run on specific device
flutter test integration_test/ -d chrome
```

---

## 📱 Platform-Specific Examples

### Android-Only App
```bash
fluttercraft create \
  --name android_app \
  --platforms android \
  --backend firebase
```

### iOS-Only App
```bash
fluttercraft create \
  --name ios_app \
  --platforms ios \
  --backend firebase
```

### Web-Only App
```bash
fluttercraft create \
  --name web_app \
  --platforms web \
  --backend supabase
```

### Desktop App
```bash
fluttercraft create \
  --name desktop_app \
  --platforms windows,macos,linux \
  --backend none
```

---

## 🔄 Workflow Examples

### Development Workflow
1. **Create Project**:
   ```bash
   fluttercraft create --name dev_project --fvm
   ```

2. **Setup Development Environment**:
   ```bash
   cd dev_project
   fvm flutter pub get
   fvm flutter run
   ```

3. **Development Cycle**:
   ```bash
   # Make changes
   fvm flutter hot-reload
   
   # Run tests
   fvm flutter test
   
   # Build for testing
   fvm flutter build apk --debug
   ```

### Production Workflow
1. **Create Production Project**:
   ```bash
   fluttercraft create \
     --name prod_app \
     --org com.company \
     --platforms android,ios \
     --backend firebase \
     --github
   ```

2. **Setup CI/CD** (automatically configured)

3. **Release Process**:
   ```bash
   # Build release
   flutter build appbundle --release
   flutter build ios --release
   
   # Deploy
   # (CI/CD handles this automatically)
   ```

---

## 📚 Learning Path

### Beginner Path
1. Start with [basic-flutter-app](basic-flutter-app/)
2. Try [firebase-integration](firebase-integration/)
3. Explore [multi-platform-setup](multi-platform-setup/)

### Intermediate Path
1. Review [enterprise-setup](enterprise-setup/)
2. Customize templates and configurations
3. Implement advanced features

### Advanced Path
1. Contribute to FlutterCraft
2. Create custom templates
3. Extend CLI functionality

---

## 🤝 Contributing Examples

Have a great FlutterCraft example? We'd love to include it!

1. **Create your example project**
2. **Document the use case and commands**
3. **Submit a pull request**

### Example Contribution Template
```markdown
## Example Name
**Use Case**: Brief description
**Platforms**: List of platforms
**Backend**: Backend service used
**Special Features**: Any unique aspects

### Command
```bash
fluttercraft create [your-command-here]
```

### Description
Detailed explanation of what this example demonstrates...
```

---

**Happy building with FlutterCraft! 🚀**
