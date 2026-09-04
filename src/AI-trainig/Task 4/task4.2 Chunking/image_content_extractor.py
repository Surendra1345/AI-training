import base64
import os

import pymupdf
import requests
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader


load_dotenv()

API_KEY = os.getenv("Api-Key")

pdf_path = r"C:\Users\User\Downloads\OCR.pdf"


# --------------------------------------------------
# 1. Extract normal text from PDF
# --------------------------------------------------

loader = PyPDFLoader(pdf_path)
documents = loader.load()

print("Normal PDF text:")
for document in documents:
    print(document.page_content)


# --------------------------------------------------
# 2. Open PDF and extract actual embedded images
# --------------------------------------------------

pdf = pymupdf.open(pdf_path)

all_image_descriptions = []


for page_number, page in enumerate(pdf, start=1):
    images = page.get_images(full=True)
    for image_number, image in enumerate(images, start=1):
        xref = image[0]
        image_data = pdf.extract_image(xref)
        image_bytes = image_data["image"]
        image_ext = image_data["ext"]
        image_path = (
            f"extracted_page_{page_number}_"
            f"image_{image_number}.{image_ext}"
        )

        # Save actual extracted image
        with open(image_path, "wb") as file:
            file.write(image_bytes)

        print(f"Extracted image: {image_path}")


        # --------------------------------------------------
        # 3. Convert image to Base64
        # --------------------------------------------------

        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        image_url = (
            f"data:image/{image_ext};base64,{base64_image}"
        )


        # --------------------------------------------------
        # 4. Send image to Gemini through OpenRouter
        # --------------------------------------------------

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",

            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },

            json={
                "model": "google/gemini-3.7-flash",

                "max_tokens": 800,

                "messages": [
                    {
                        "role": "user",

                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "What is shown in this image? "
                                    "Answer in 2 or 3 simple sentences. "
                                    "Only describe what is visibly present. "
                                    "Do not provide reasoning."
                                ),
                            },

                            {
                                "type": "image_url",

                                "image_url": {
                                    "url": image_url
                                },
                            },
                        ],
                    }
                ],
            },
        )

result = response.json()

description = result["choices"][0]["message"]["content"]

print("\nImage description:")
print(description)