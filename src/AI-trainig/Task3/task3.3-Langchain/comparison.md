# TASK 3.3: Raw HTTP vs LangChain LCEL

## Overview

This task compares two ways of calling an LLM:

1. **Raw HTTP using `httpx`**
2. **LangChain LCEL**

Both implementations use OpenRouter and PostgreSQL conversation history.

---

## 1. Raw HTTP Implementation

The raw implementation uses `httpx` directly.

Main responsibilities handled manually:

* Create HTTP requests
* Add API headers
* Build the request payload
* Send the request to OpenRouter
* Check the response status
* Parse the JSON response
* Extract the assistant's content
* Handle conversation history

Example flow:

```text
User Request
    ↓
Build JSON payload
    ↓
httpx POST request
    ↓
OpenRouter
    ↓
JSON response
    ↓
Extract choices[0].message.content
```

---

## 2. LangChain LCEL Implementation

The LangChain implementation uses:

* `ChatOpenAI`
* `ChatPromptTemplate`
* `MessagesPlaceholder`
* `StrOutputParser`
* LCEL pipe syntax

The main flow is:

```text
Prompt
   ↓
LLM
   ↓
Output Parser
```

Example:

```python
prompt | llm | parser
```

LangChain handles many of the low-level details automatically.

---

## 3. What LangChain Replaced

| Raw HTTP                 | LangChain                    |
| ------------------------ | ---------------------------- |
| `httpx.AsyncClient()`    | `ChatOpenAI`                 |
| Manual request payload   | `ChatPromptTemplate`         |
| Raw dictionaries         | `HumanMessage` / `AIMessage` |
| Manual JSON parsing      | `StrOutputParser`            |
| Procedural execution     | LCEL pipe                    |
| Manual callbacks/logging | LangChain callbacks          |

---

## 4. Execution Comparison

### Raw HTTP

The raw endpoint:

```text
POST /llm/raw/chat
```

uses `httpx` to call OpenRouter directly.

It manually handles the request and response.

### LangChain

The LangChain endpoint:

```text
POST /llm/langchain/chat
```

uses an LCEL chain:

```python
prompt | llm | StrOutputParser()
```

It also uses callbacks for logging and metrics.

---

## 5. Database and Conversation History

Both implementations:

1. Retrieve previous conversation history from PostgreSQL.
2. Add the new user question.
3. Send the conversation to OpenRouter.
4. Receive the LLM response.
5. Store the response in PostgreSQL.

So both implementations provide conversation memory.

---

## 6. Three Abstractions Provided by LangChain

### 1. Network Transport

LangChain hides:

* HTTP request creation
* Headers
* API endpoint handling
* Request serialization
* Status-code handling

**Judgment:** Worth handing over because it reduces repeated low-level HTTP code.

### 2. Response Parsing

LangChain hides manual JSON navigation such as:

```python
response.json()["choices"][0]["message"]["content"]
```

`StrOutputParser()` converts the model output into a string.

**Judgment:** Worth handing over because it makes response handling simpler.

### 3. Callbacks and Metrics

LangChain callbacks can handle:

* Token usage
* Latency
* Cost information
* Logging
* Observability

Example:

```text
LLM call started
       ↓
LLM execution
       ↓
Callback receives result
       ↓
Token and metric logging
```

**Judgment:** Worth handing over because it keeps monitoring logic separate from the main service code.

---

## 7. Callback Example

The callback produced output like:

```text
[CALLBACK] LLM call initiated via OpenRouter...

[CALLBACK] LLM execution finished.
Input Tokens: 142
Output Tokens: 285
Total Tokens: 427
```

This can later be used for the Week 6 instrumentation and observability work.

---

## Conclusion

### Raw HTTP

```text
More control
More manual code
More responsibility
```

### LangChain LCEL

```text
More abstraction
Less boilerplate
Composable chains
Built-in callback support
```

Both approaches successfully call the LLM and maintain conversation history. The main difference is that **raw HTTP gives more low-level control, while LangChain provides abstractions that reduce the amount of code we need to write manually.**
