---
name: sage-mcp-builder
description: Build or repair an MCP server, its tool contracts, or a client integration.
---

Inspect the client's supported protocol and the installed SDK version. Retrieve
the relevant [official protocol](https://modelcontextprotocol.io/docs/develop/build-server)
and SDK documentation before using version-sensitive APIs.
Choose stdio for a local process or the supported HTTP transport for a remote
service. Keep logs off stdio protocol output. Define narrow input/output schemas,
bounded pagination and payloads, actionable errors, timeouts, and cancellation.
Separate read operations from mutations. Keep credentials out of schemas, logs,
and committed configuration; preserve the service's authorization boundaries.

Implement tools around real user workflows and existing API contracts. Return
compact structured results without duplicating large data in text. Use deferred
tool discovery where the client supports it. Test actual initialization, tool
listing/calls, invalid inputs, external failure, and cleanup through the intended
transport. Report protocol checks separately from tests that exercise service
credentials or live data. Tool annotations describe behavior; they do not enforce
permissions.
