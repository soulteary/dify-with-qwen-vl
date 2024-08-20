import cv2
import numpy as np
from sklearn.cluster import KMeans
import os

def preprocess_video(video_path):
    """
    预处理视频,提取所有帧
    """
    cap = cv2.VideoCapture(video_path)
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return frames

def detect_shot_boundaries(frames, threshold=30):
    """
    使用帧差法检测镜头边界
    """
    shot_boundaries = []
    for i in range(1, len(frames)):
        prev_frame = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
        curr_frame = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
        diff = np.mean(np.abs(curr_frame.astype(int) - prev_frame.astype(int)))
        if diff > threshold:
            shot_boundaries.append(i)
    return shot_boundaries

def extract_keyframes(frames, shot_boundaries):
    """
    从每个镜头中提取关键帧，返回关键帧及其对应的原始帧序号
    """
    keyframes = []
    keyframe_indices = []
    for i in range(len(shot_boundaries)):
        start = shot_boundaries[i-1] if i > 0 else 0
        end = shot_boundaries[i]
        shot_frames = frames[start:end]
        
        # 使用K-means聚类选择关键帧
        frame_features = np.array([cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).flatten() for frame in shot_frames])
        kmeans = KMeans(n_clusters=1, random_state=0).fit(frame_features)
        center_idx = np.argmin(np.sum((frame_features - kmeans.cluster_centers_[0])**2, axis=1))
        
        keyframes.append(shot_frames[center_idx])
        keyframe_indices.append(start + center_idx)  # 原始帧序号
    
    return keyframes, keyframe_indices

def save_keyframes(keyframes, keyframe_indices, output_dir):
    """
    保存关键帧到指定目录，使用原始帧序号命名
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for keyframe, index in zip(keyframes, keyframe_indices):
        output_path = os.path.join(output_dir, f'keyframe_{index:06d}.jpg')
        cv2.imwrite(output_path, keyframe)
    
    print(f"已保存 {len(keyframes)} 个关键帧到 {output_dir}")

def main(video_path, output_dir):
    frames = preprocess_video(video_path)
    shot_boundaries = detect_shot_boundaries(frames)
    keyframes, keyframe_indices = extract_keyframes(frames, shot_boundaries)
    save_keyframes(keyframes, keyframe_indices, output_dir)

if __name__ == "__main__":
    video_path = "mini.mp4"
    output_dir = "keyframes_output"
    main(video_path, output_dir)