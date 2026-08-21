# Task 2.4 – Structured Extraction That Does Not Break

## Overview

This task extracts structured information from unstructured text using an open-weight language model. The model response is cleaned, converted into JSON, and validated using a Pydantic model.

The program is designed to handle malformed responses without crashing.

## Input

The program uses the following unstructured text:

> My name is Surendra and I am 22 years old. I am working at Genworx.ai as a Fullstack Trainee.

The program extracts:

- Name
- Age
- Company
- Role

## Expected Output

{
  "name": "Surendra",
  "age": 22,
  "company": "Genworx.ai",
  "role": "Fullstack Trainee"
}