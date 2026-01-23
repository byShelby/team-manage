# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## ⚠️ CRITICAL RULES - READ FIRST

### 🔴 MANDATORY: Always Use Auggie-MCP for Context Retrieval

**AT ANY TIME when you need project context, you MUST use `mcp__auggie__codebase-retrieval` tool.**

- **DO NOT** use Grep, Glob, or Read tools for initial code exploration
- **DO NOT** make assumptions about code structure without querying auggie-mcp first
- **DO** use auggie-mcp with natural language queries (e.g., "Where is user authentication handled?", "How is the database connected?")
- **DO** use auggie-mcp before making any code changes to understand existing patterns

**Example queries:**
- "Where are the ChatGPT API calls implemented?"
- "How is JWT token validation handled?"
- "What is the database schema for teams?"
- "How does the redemption flow work?"

### 🔴 MANDATORY: One Task at a Time, Always Get User Approval

**Complete ONLY ONE task at a time. For EVERY subtask, you MUST get user approval before proceeding.**

- **DO NOT** complete multiple tasks in a single session without user confirmation
- **DO NOT** assume the user wants you to continue to the next task
- **DO** stop after completing each subtask and ask user for approval to continue
- **DO** present your plan for the next subtask and wait for user confirmation
- **DO** ask user for specific implementation choices before coding

**Workflow for each task:**
1. Understand the task requirements (use auggie-mcp for context)
2. Present your implementation plan to the user
3. Wait for user approval
4. Implement the task
5. Report completion and ask if user wants to proceed to next task
6. **STOP and WAIT** for user response

**Example:**
- ✅ "I've completed Task 1: Configuration management. Would you like me to proceed with Task 2: Team account import?"
- ❌ "I've completed Task 1. Now I'll start Task 2..." (DO NOT do this)

### 🔴 MANDATORY: Task Completion Requires User Confirmation

**NEVER mark a task as completed without explicit user confirmation.**

- **DO NOT** automatically mark tasks as "已完成" in 任务.md
- **DO NOT** update task status to "completed" without user approval
- **DO** present your work and ask user to confirm if the task is complete
- **DO** wait for user to explicitly say the task is done before updating status

**Workflow:**
1. Complete the implementation
2. Present the results to the user
3. Ask: "Please confirm if this task is complete and ready to be marked as 已完成"
4. Wait for user confirmation
5. Only after user confirms, update 任务.md with "已完成" status

### 🔴 MANDATORY: Clean Up Test Files After Task Completion

**Test files created during development MUST be deleted after task completion.**

- **DO** create test files during development for verification
- **DO NOT** leave test files in the project after task is confirmed complete
- **DO** delete all temporary test files (test_*.py, verify_*.py, etc.) after user confirms task completion
- **DO** keep only production code and essential scripts (like init_db.py)

**Example test files to delete:**
- test_settings.py
- verify_db.py
- test_*.py
- Any other temporary testing scripts

---

## Project Overview

**GPT Team 管理和兑换码自动邀请系统** - A ChatGPT Team account management system that enables administrators to manage multiple Team accounts and allows users to join Teams through redemption codes.

**Technology Stack**: Python + FastAPI + SQLite + curl_cffi + Jinja2

---

## Key Documents - Where to Find Information

### 📄 需求.md (Requirements)
- **Complete project requirements and specifications**
- Database schema definitions
- Business logic and workflows
- API integration details
- **IMPORTANT**: Always consult user before implementing specific details from this document

### 📄 任务.md (Tasks)
- **Records in-progress and completed tasks**
- Task status tracking (待开始/进行中/已完成)
- Task dependencies and priorities
- Subtask breakdowns
- **IMPORTANT**: Always check here before starting work to understand current task status
- **IMPORTANT**: Plan tasks and write them to this document before implementation
- Follow priority order: P0 (Core) → P1 (Important) → P2 (Enhancement)

### 📄 openai-api.md (API Documentation)
- ChatGPT API endpoints and authentication
- JWT token parsing and validation
- Error handling strategies
- Retry logic and proxy configuration

### 📄 接口.md (API Interface Documentation)
- **Complete API interface definitions for the system**
- All implemented and planned endpoints
- Request/response formats and examples
- Authentication requirements (🔒 markers)
- Implementation status (✅ implemented / ⏳ pending)
- HTTP status codes and error handling
- Data models and business logic
- **IMPORTANT**: Reference this document when implementing or testing API endpoints

---

## Important Rules

1. **🔴 MANDATORY - Always use auggie-mcp**: At ANY time when you need project context, you MUST use `mcp__auggie__codebase-retrieval` tool. This is the PRIMARY and PREFERRED method for understanding the codebase. Do NOT use Grep/Glob/Read for initial exploration.

2. **🔴 MANDATORY - One task at a time**: Complete ONLY ONE task at a time. For EVERY subtask, get user approval before proceeding. Never assume the user wants you to continue automatically.

3. **🔴 MANDATORY - Use multiple-choice questions**: When asking user for confirmation or decisions, ALWAYS use the AskUserQuestion tool with multiple-choice options. NEVER ask open-ended questions that require the user to type answers. Provide clear options for the user to select from.

4. **Consult user before implementation**: When implementing features from 需求.md, ask user for specific implementation choices.

5. **Plan tasks and update 任务.md**: Before starting work, read 需求.md, plan tasks, and write them to 任务.md. Update task status during implementation (待开始 → 进行中 → 已完成).

6. **Follow task priorities**: Check 任务.md for current task status. Follow P0 → P1 → P2 order.

7. **Respect task dependencies**: Some tasks depend on others (e.g., Task 1 must complete before Task 2).

---

## Development Workflow

### Before Starting Any Task

1. **Read 需求.md** to understand detailed requirements
2. **Check 任务.md** to understand current task status (in-progress and completed tasks)
3. **Plan the task**: Break down into subtasks and identify dependencies
4. **Write the plan to 任务.md**: Document planned tasks with status "待开始"
5. **Use auggie-mcp** to understand relevant codebase context
6. **Present your plan** to the user and wait for approval

### During Implementation

1. **Update task status in 任务.md**: Mark task as "进行中" before starting
2. **Use auggie-mcp** before reading or modifying any files
3. **Ask user** for implementation choices when multiple approaches are possible (use AskUserQuestion tool with multiple-choice options)
4. **Stop after each subtask** and ask user if you should continue
5. **Update task status in 任务.md**: Mark subtask as "已完成" immediately after completion

### After Completing a Task

1. **Report completion** to the user
2. **Ask if user wants to proceed** to the next task
3. **STOP and WAIT** for user response
4. **DO NOT** automatically continue to the next task


---

## Notes

- This is a **greenfield project** - no existing code yet
- All implementation details must be confirmed with user before coding
- **🔴 REMINDER**: At ANY time when you need project context, ALWAYS use `mcp__auggie__codebase-retrieval` first
- **🔴 REMINDER**: Complete ONE task at a time, get user approval before continuing
