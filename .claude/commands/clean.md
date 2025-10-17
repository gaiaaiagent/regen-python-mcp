# Clean and Refactor

## RUN
`eza . --tree --git-ignore`

Check git working status and git history.

## READ
@docs/regen_mcp_thesis.md

First search through the repository and read various files to get a very strong sense of the current state of the project.

Seek to understand the intent of the project. Report your understanding of the intent back to the user.

Identify the best parts of the repository.

Identify the worst aspects of the repository.

Identify the structural patterns of the repository.

Construct a plan to clean the repository to increase long term functionality, reliability, and clarity. 

Requirements:
1. Ensure that .mcp.json contains correct configuration to have claude code connect the the regen python mcp server.
2. Ensure .claude/settings.json contains the following: 
```json
{
  "enableAllProjectMcpServers": true
}
```

Make sure that our tests actually rigorously examine the core and boundary
functionality of all of our intentions so that the point of the tests is to
verify that the mcp will fully support our users when they go to use it? Ensure
that tests drive the betterment of the repository and are not just tests for
tests sake.

