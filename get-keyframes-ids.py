import cv2
import os
import re

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

def extract_frames(video_path, frame_numbers, output_folder):
    # 创建输出文件夹（如果不存在）
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 打开视频文件
    video = cv2.VideoCapture(video_path)
    
    # 获取视频的总帧数和帧率
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    
    print(f"视频总帧数: {total_frames}")
    print(f"视频帧率: {fps}")
    
    for frame_number in frame_numbers:
        # 设置视频读取位置
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        # 读取帧
        ret, frame = video.read()
        
        if ret:
            # 保存帧为图像文件
            output_path = os.path.join(output_folder, f"extracted_frame_{frame_number}.jpg")
            cv2.imwrite(output_path, frame)
            print(f"已提取并保存帧 {frame_number}")
        else:
            print(f"无法读取帧 {frame_number}")
    
    # 释放视频对象
    video.release()

# 使用示例
video_path = 'video.mp4'  # 替换为实际的视频文件路径
keyframes_folder = 'keyframes_output'  # 替换为之前保存关键帧的文件夹路径
output_folder = 'extracted_frames'  # 指定输出文件夹

# 获取需要提取的帧号
frame_numbers = extract_numbers(keyframes_folder)

# 提取指定帧
extract_frames(video_path, frame_numbers, output_folder)

print("帧提取完成！")
