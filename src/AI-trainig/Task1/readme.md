# Task 1.1 – Public API

I used Python with the `httpx` library to send a request to the API and received the response in JSON format. I also checked the status code and printed the response.

Through this task, I understood how to make an API request, handle the JSON response, and check whether the request was successful or not.

# Task 1.2 – First Gemini Model Call

 First API call to the Gemini model.

I stored my API key in a `.env` file instead of directly writing it in the Python code. I used `python-dotenv` to load the API key and `httpx` to send the request to the Gemini API.

I created a request body containing my question and sent it to the Gemini model. After receiving the response, I extracted the generated answer from the JSON response.

# Task 1.3 – Token and Cost Reporting

token counting, cost calculation, and latency measurement.

I counted the input and output tokens and calculated the cost based on the token usage and the model's pricing. I also used `perf_counter()` to measure how long the API request took and converted the time into milliseconds.

I calculated both the input cost and output cost and then calculated the total cost of the request. I also converted the total cost from USD to INR.

I checked the Gemini usage information to understand how the actual API usage and token consumption are reported by the provider.

Through this task, I understood that API calls are not only about getting the answer. We also need to consider token usage, latency, and cost.

# Task 1.4 – Temperature and Context Window

In this task, I learned how temperature affects the output of a Gemini model.

First, I ran the same prompt multiple times with temperature set to `0`. For simple questions, I noticed that the answers were often identical. I then changed the temperature to `1.0` and ran the same prompt multiple times. The answers started to vary even though the question was the same.

I understood that temperature controls the randomness of the model's response. A lower temperature generally produces more consistent responses, while a higher temperature allows more variation.

I also tested `maxOutputTokens` by deliberately keeping it low. I observed that the response could get cut off when the model reached the output token limit.

Finally, I tested a very large prompt to understand what happens when the context becomes too large. The API returned an error instead of providing the normal `candidates` response. This helped me understand that the model has a context window limit.

# Task 1.5 – Batch Mode

In this task, I worked with multiple prompts instead of sending only one prompt at a time.

I created a `prompt.txt` file containing multiple questions and read the prompts from the file using Python.

First, I implemented sequential execution, where each prompt is sent one after another. I measured the total time taken for all the requests.

Then I used `asyncio` and `httpx.AsyncClient` to send the requests concurrently using `asyncio.gather()`. This allowed multiple API requests to run at the same time instead of waiting for each request to finish before starting the next one.

I compared the sequential execution time with the concurrent execution time. In my test with 10 prompts, the sequential execution took around 9.42 seconds, while the concurrent execution took around 1.42 seconds. This showed that concurrent execution can be much faster for API requests because the program does not have to wait for every network request one by one.

I also collected the input tokens, output tokens, and cost for each prompt and calculated the total batch cost and average cost per prompt.

While testing the batch mode, I also encountered a `429 RESOURCE_EXHAUSTED` error. The Gemini API showed that my free-tier limit was 15 requests per minute for the model I was using. Since I was running the prompts sequentially and then running them concurrently in the same program, the total number of requests exceeded the available limit.

Because of this, some concurrent requests failed and my program returned `None` for those prompts. `None` did not mean that Gemini generated an empty answer; it meant that the API request failed because of the quota limit.

This task helped me understand the difference between sequential and concurrent execution, and also showed me that API rate limits need to be considered when working with batch requests.
