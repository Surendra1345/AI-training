Concepts Applied:
2.12 Multi-turn conversation
2.13 Streaming
2.14 Model fallback
2.15 Conversation cost
2.16 Provider failure handling
Features

1. Multi-turn conversation

The application maintains the complete conversation history throughout the session.
Each user question and assistant response is stored in the conversation history and sent again with the next request.
This allows follow-up questions to use previous context.

Example:

User: What is Python?
Assistant: Python is a programming language.
User: Why is it popular?
Assistant: Python is popular because...

2. Streaming

Responses are streamed from the model so that generated text appears in the terminal as it arrives instead of waiting for the complete response.
The streamed response is also collected so the complete assistant answer can be added to the conversation history.

3. Model fallback

The application uses a primary model and a fallback model.
Primary model:
Qwen3.6-35B-A3B

Fallback model:

GPT-4o-mini
If the primary model fails, the application automatically tries the fallback model using the same conversation history.
The user does not need to manually select the second model.

4. Deliberate fallback testing

The primary model is deliberately given an invalid model name to force a provider failure.
The expected behavior is:

Primary model
    ↓
Failure
    ↓
Fallback model
    ↓
Successful response
After confirming the fallback works, the valid primary model can be restored.

5. Per-turn cost

For every successful request, the application records the input and output token counts.
The input cost and output cost are calculated using the pricing of the model that handled the request.
The total cost for that turn is:
Input cost + Output cost = Turn cost
The application prints the token counts and the cost after every turn.

6. Running conversation cost
The application maintains a cumulative conversation cost.
After every successful turn, the current turn cost is added to the previous total.

Example:

Turn 1
Turn Cost: $0.000100
Conversation Total Cost: $0.000100

Turn 2
Turn Cost: $0.000180
Conversation Total Cost: $0.000280

Turn 3
Turn Cost: $0.000250
Conversation Total Cost: $0.000530

Because the conversation history is resent on every turn, later requests can contain more input tokens, which can increase the cost per turn.


The CLI supports multiple conversation turns.
Conversation history is maintained and resent with every request.
Responses stream to the terminal as they arrive.
A fallback model is automatically used when the primary model fails.
The primary model failure is deliberately tested.
The user receives a response without manually switching models.
Input and output tokens are captured for each turn.
Input cost, output cost, and total turn cost are calculated.
The running conversation total cost is printed after every successful turn.
The cost per turn can increase as the conversation history grows.