from fastapi import HTTPException
import os
import openai


class ChatGPT:
    def __init__(self):
        pass

    async def generate_response(self, message: str) -> str:
        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo",  
                messages=[
                    {"role": "system", "content": "You are a helpful assistant to give solutions for web accessibility problems. give guidelines for code modification to make it more accessible. Answer in short ans specific sentences."},
                    {"role": "user", "content": message}
                ]
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
