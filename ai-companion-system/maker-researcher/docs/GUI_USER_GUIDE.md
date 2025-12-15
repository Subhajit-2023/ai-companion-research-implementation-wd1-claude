# AI Maker-Researcher GUI - Complete User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Dashboard](#dashboard)
4. [Research Interface](#research-interface)
5. [Code Tools](#code-tools)
6. [Task Management](#task-management)
7. [Approvals](#approvals)
8. [Knowledge Base](#knowledge-base)
9. [Optimization](#optimization)
10. [Reports & Analytics](#reports--analytics)
11. [Keyboard Shortcuts](#keyboard-shortcuts)
12. [Troubleshooting](#troubleshooting)

---

## Introduction

The AI Maker-Researcher GUI is a modern, intuitive web interface for interacting with the autonomous AI research and development system. It provides visual representations of system status, research results, and task progress, making it easier to understand and control the AI assistant.

### Key Features

- **Real-time Dashboard**: Monitor system health, metrics, and activity at a glance
- **Visual Research**: See research results with categorized cards and charts
- **Code Generation**: Generate and analyze code with syntax highlighting
- **Task Tracking**: Visual task boards with status indicators
- **Approval Workflow**: Review proposed changes with diff visualization
- **Knowledge Management**: Browse and search your document library
- **Performance Analytics**: Charts and graphs showing system performance

---

## Getting Started

### Prerequisites

1. The Maker-Researcher API server must be running:
   ```bash
   cd ai-companion-system/maker-researcher
   python run.py --api
   ```

2. Ollama must be running with required models installed

### Starting the GUI

```bash
cd ai-companion-system/maker-researcher/gui
npm install
npm run dev
```

The GUI will be available at `http://localhost:3001`

### First Launch

When you first open the GUI, you'll see:

1. **Sidebar Navigation** (left): Access all sections of the application
2. **Status Indicator** (bottom-left): Shows system health
3. **Main Content Area** (center): Displays the current page
4. **Pending Approvals Badge**: Shows number of items awaiting your review

---

## Dashboard

The Dashboard is your command center, providing an overview of the entire system.

### System Metrics Cards

At the top, you'll see four metric cards:

| Card | Description | Warning Level |
|------|-------------|---------------|
| **CPU Usage** | Current processor utilization | Red when >80% |
| **Memory** | RAM usage with GB used | Amber when >80% |
| **GPU** | Graphics processor usage | Amber when >90% |
| **Disk** | Storage utilization | Red when >90% |

### Quick Stats

Below the metrics, three stat cards show:
- **Total Tasks**: Number of tasks in the system
- **Pending Approvals**: Changes waiting for your review (click to jump to Approvals)
- **Documents**: Files in your knowledge base

### Resource Usage Chart

An interactive area chart shows resource usage over time:
- **Blue line**: CPU usage
- **Green line**: Memory usage
- **Orange line**: GPU usage

Hover over any point to see exact values.

### Task Distribution

A donut chart shows your tasks by status:
- **Green**: Completed
- **Amber**: In Progress
- **Blue**: Pending
- **Red**: Failed

### System Alerts

If issues are detected, they appear in a highlighted alert box:
- High CPU/Memory usage warnings
- GPU memory pressure
- Service errors

### Recent Activity

A timeline of your most recent tasks with:
- Status indicator (colored dot)
- Task title and category
- Creation time

---

## Research Interface

The Research page lets you search the web, academic papers, and code repositories.

### Performing a Search

1. Enter your query in the search box
2. Check/uncheck options:
   - **Academic Papers**: Include ArXiv and Semantic Scholar
   - **Code Examples**: Include GitHub repositories
   - **News**: Include recent news articles
3. Click **Search** or press Enter

### Understanding Results

Results are displayed in three categories:

#### Web Results (Blue)
- Title and URL
- Snippet from the page
- Click "Open" to visit the source

#### Academic Papers (Green)
- Paper title
- Authors (first 3 shown)
- Year and citation count
- Link to PDF when available

#### Code Examples (Orange)
- Repository name
- Star count
- Primary language
- Description

### Research Summary

Below the results, an AI-generated summary synthesizes all findings into actionable insights.

### Research Assistant Chat

The sidebar contains a chat interface where you can:
- Ask follow-up questions about your research
- Get explanations of concepts
- Request deeper analysis

The assistant shows which agent (researcher, advisor, etc.) is responding.

### Recent Sessions

Previously searched queries are saved for quick access. Click any session to re-run that search.

---

## Code Tools

The Code Tools section provides three main functions.

### Generate Tab

Create new code from natural language descriptions:

1. **Description**: Explain what code you need
2. **Language**: Select the programming language
3. Click **Generate Code**

The generated code appears with:
- Syntax highlighting
- Copy button
- Confidence score indicator

### Analyze Tab

Analyze existing code files:

1. Enter the **File Path** (absolute or relative to project)
2. Click **Analyze**

Results show:
- **Lines of Code**: Total line count
- **Complexity Score**: 0-10 rating (lower is better)
- **Functions/Classes**: Count of definitions
- **Issues**: Detected problems with severity
- **Suggestions**: AI-recommended improvements

### Debug Tab

Get help fixing errors:

1. Paste your **Error Message** or stack trace
2. Select the **Language**
3. Click **Debug**

The analysis includes:
- Error type identification
- File and line number (if available)
- Root cause analysis
- Suggested fixes with code snippets
- Confidence level for each fix

---

## Task Management

The Tasks page provides a visual way to manage AI tasks.

### Task Overview

At the top, status cards show task counts:
- **All Tasks**: Total number
- **Pending**: Waiting to start
- **In Progress**: Currently running (animated)
- **Awaiting Approval**: Need your review
- **Completed**: Successfully finished
- **Failed**: Encountered errors

Click any card to filter the list.

### Task Cards

Each task displays:
- **Status Icon**: Visual indicator (spinning for in-progress)
- **Title**: Task name
- **Description**: What the task does
- **Category Badge**: Research, Code, Debug, etc.
- **Time**: When created (relative)
- **Approval Badge**: If approval is required

### Creating Tasks

Click **New Task** to open the creation dialog:

1. **Title**: Brief name for the task
2. **Description**: Detailed explanation
3. **Category**: Type of task
   - Research: Information gathering
   - Code: Generation or modification
   - Debug: Error investigation
   - Optimize: Performance improvements
   - Advise: General questions
4. **Priority**: Low, Normal, High, Urgent
5. **Require Approval**: Check if you want to review before execution

### Canceling Tasks

For pending or awaiting-approval tasks, click the trash icon to cancel.

---

## Approvals

The Approvals page is where you review proposed changes before they're applied.

### Approval Overview

Stats at the top show:
- **Pending**: Total awaiting review
- **Auto-Approve Eligible**: Safe changes that could be auto-approved
- **High Risk**: Changes requiring careful review

### Approval Cards

Each approval request shows:
- **Summary**: What the change does
- **Request ID**: Unique identifier
- **Change Count**: Number of modifications
- **Risk Level**: Safe, Low, Medium, High, Critical
- **Creation Time**: When requested

### Reviewing Changes

Click **View Changes** to expand:

Each change shows:
- **File Path**: What file is affected
- **Risk Badge**: Individual risk level
- **Description**: What will change
- **Diff View**: Color-coded before/after
  - Green lines: Additions
  - Red lines: Removals
  - Blue lines: Context

### Impact Analysis

Review the impact analysis to understand:
- What systems are affected
- Potential side effects
- Dependencies

### Rollback Plan

Every approval includes a rollback plan explaining how to undo the changes if needed.

### Taking Action

- **Approve**: Apply the changes
- **Reject**: Cancel with optional reason

---

## Knowledge Base

The Knowledge page manages your document library.

### Adding Documents

1. Enter the **File Path** to your document
2. Supported formats: PDF, EPUB, TXT, MD, Python, JavaScript
3. Click **Add to Knowledge Base**

Processing extracts text and creates searchable chunks.

### Searching Knowledge

1. Enter your query in the search box
2. Click **Search**

Results show:
- Source document
- Matching content snippet
- Relevance percentage

### Document Library

Your documents are displayed as cards showing:
- **Icon**: Based on file type (PDF, EPUB, etc.)
- **Title**: Document or file name
- **Author**: If available
- **Stats**: Page count and chunk count
- **Type Badge**: File format

### Deleting Documents

Click the trash icon on any document card to remove it from the knowledge base.

---

## Optimization

The Optimize page helps tune performance for your RTX 4060.

### Running Analysis

Click **Run Analysis** to:
1. Collect current system metrics
2. Identify bottlenecks
3. Generate recommendations

### Bottlenecks

Detected issues appear in an amber-highlighted box:
- GPU memory pressure
- High CPU usage
- Memory constraints

### Recommendations

AI-generated suggestions are listed with checkmarks:
- Specific actions to take
- Expected improvements
- Implementation difficulty

### Optimization Guide

Expandable cards cover key areas:
- **Model Selection**: Best models for RTX 4060
- **Inference Settings**: Optimal parameters
- **Memory Management**: VRAM optimization
- **Concurrent Operations**: Request handling
- **Stable Diffusion**: Image generation settings

### Improvement History

Track your optimization efforts:
- Total improvements attempted
- Success count
- Overall success rate

---

## Reports & Analytics

The Reports page provides detailed analytics and visualizations.

### Summary Stats

Four key metrics at the top:
- **Total Tasks**: All-time count
- **Completed**: Successful tasks
- **Failed**: Unsuccessful tasks
- **Success Rate**: Percentage

### Charts

#### Tasks by Category (Pie Chart)
Shows distribution across Research, Code, Debug, etc.

#### Tasks by Status (Bar Chart)
Horizontal bars for each status type.

#### Activity Timeline (Area Chart)
Tasks created vs completed over time.

#### Response Time (Line Chart)
System response times over 24 hours.

#### Request Volume (Bar Chart)
Number of requests per hour.

### System Health Summary

Progress bars for:
- CPU Usage
- Memory
- GPU
- Disk

Each shows current percentage with color-coded bars.

### Exporting Reports

Click **Export Report** to download a JSON file containing:
- Summary statistics
- Tasks by category/status
- Current system metrics
- Timestamp

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + /` | Focus search |
| `Ctrl + N` | New task |
| `Ctrl + R` | Refresh data |
| `Esc` | Close modal |

---

## Troubleshooting

### GUI Won't Load

1. Ensure the API server is running (`python run.py --api`)
2. Check the API is accessible at `http://localhost:8001`
3. Check browser console for errors

### No Data Showing

1. Click the refresh button on the relevant page
2. Check if Ollama is running
3. Verify the API server hasn't crashed

### Research Returns No Results

1. Check internet connectivity
2. Try a more specific query
3. Wait and retry (search engines may rate limit)

### Charts Not Rendering

1. Try refreshing the page
2. Check browser console for JavaScript errors
3. Ensure you have tasks/data to display

### Slow Performance

1. Close other browser tabs
2. Check system resources in Dashboard
3. Consider using smaller LLM models

---

## Tips for Best Experience

1. **Keep the Dashboard visible** in a separate tab to monitor system health
2. **Use specific queries** for better research results
3. **Review approvals promptly** to keep tasks flowing
4. **Add relevant documents** to improve AI knowledge
5. **Check optimizations** periodically for performance tips
6. **Export reports** regularly for record-keeping

---

## Version History

- **v1.0.0** (December 2024): Initial release
  - Dashboard with real-time metrics
  - Research interface with multi-source search
  - Code generation and analysis
  - Task management with visual progress
  - Approval workflow with diff viewer
  - Knowledge base management
  - Performance optimization guide
  - Reports and analytics

---

*For CLI/API documentation, see USER_GUIDE.md*
