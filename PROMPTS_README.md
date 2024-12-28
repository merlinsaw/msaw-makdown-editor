# AI Prompts Submodule Guide

This guide explains how to add and manage the AI_Prompts repository as a submodule in your projects.

## Adding AI_Prompts as a Submodule

1. Navigate to your project directory in PowerShell:
```powershell
cd your-project-directory
```

2. Add the AI_Prompts repository as a submodule:
```powershell
git submodule add https://github.com/merlinsaw/AI_Prompts.git
```

3. Initialize and update the submodule:
```powershell
git submodule update --init --recursive
```

4. Commit the changes:
```powershell
git add .gitmodules AI_Prompts
git commit -m "Add AI_Prompts as submodule"
```

## Working with the Submodule

### When Cloning a Project with Submodules

You have two options:

#### Option 1: Clone with submodules directly
```powershell
git clone --recursive your-project-url
```

#### Option 2: If already cloned, initialize submodules after
```powershell
git submodule update --init --recursive
```

### Updating the Submodule

To update the submodule to the latest version:
```powershell
git submodule update --remote AI_Prompts
```
