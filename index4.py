import asyncio
import aiohttp
import os
import re
import ssl
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

output_folder="data"
api_key="app-KBux9ydPPVouHGLssndoinqg" # dify api key

async def request_image(session, api_key, frame_number):
    url = 'https://dify.lab.io/v1/chat-messages'
    headers = {
        'Authorization': f"Bearer {api_key}",
        'Content-Type': 'application/json',
    }

    image_url = f"http://minio.lab.io/wukong/extracted_frame_{frame_number}.jpg"
    
    payload = {
        "inputs": {},
        "query": "你是资深新闻记者，擅长分析视频画面信息，给出客观的评价信息。\n\n这个视频画面的背景是“新华社采访国产游戏《黑神话：悟空》制作人”的采访内容。忽略画面中的“新华社 Bilibili” 水印信息。",
        "response_mode": "blocking",
        "user": "qwen2-vl",
        "files": [
            {
                "type": "image",
                "transfer_method": "remote_url",
                "url": image_url
            }
        ]
    }
    
    async with session.post(url, headers=headers, json=payload, ssl=ssl_context) as response:
        if response.status == 200:
            response_data = await response.json()
            content = response_data.get('answer', '')
            
            with open(f"{output_folder}/{frame_number}.txt", "w") as f:
                f.write(content)
            
            print(f"Content saved to {frame_number}.txt")
        else:
            print(f"Error for frame {frame_number}: {response.status}, {response.reason}")
            print(await response.text())

def extract_numbers(folder_path):
    # 获取文件夹中所有 jpg 文件
    files = os.listdir(folder_path)
    jpg_files = [f for f in files if f.endswith('.jpg')]
    numbers = []
    for file in jpg_files:
        match = re.search(r'(\d+)\.jpg$', file)
        if match:
            number = int(match.group(1))
            numbers.append(number)
    return sorted(numbers)


async def main():
    frame_numbers = extract_numbers('extracted_frames')
    print(frame_numbers)


    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(2)  # 设置为合适的并发
        tasks = []

        async def bounded_request(frame_number):
            async with semaphore:
                await request_image(session, api_key, frame_number)

        for frame_number in frame_numbers:
            task = asyncio.create_task(bounded_request(frame_number))
            tasks.append(task)

        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
