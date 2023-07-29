#!/usr/bin/python3

import argparse
import os
from datetime import datetime, timedelta
from pymediainfo import MediaInfo
from typing import Tuple
from queue import PriorityQueue

class MetadataException(Exception):
  def __init__(self, message):
    super().__init__(message)

MEDIA_INFO_DATETIME_FORMAT = "%Z %Y-%m-%d %H:%M:%S"
LOWER_THRESHOLD_MS = 500
UPPER_THRESHOLD_MS = 30000

def get_full_file_list(directory: str) -> PriorityQueue:
  pq = PriorityQueue()
  for root, _, files in os.walk(directory):
    for file in files:
      pq.put(root + os.sep + file)
  return pq

def get_video_duration_time(path: str) -> Tuple[datetime, int]:
  try:
    info = MediaInfo.parse(path)
    data = info.general_tracks[0].to_data()
    if 'duration' not in data or 'encoded_date' not in data:
      raise MetadataException(f'File {path} does not contain required metadata.')
    timestamp = None
    try:
      timestamp = datetime.strptime(data['encoded_date'], MEDIA_INFO_DATETIME_FORMAT)
    except ValueError as e:
      d = data['encoded_date']
      raise MetadataException(f'File {path} contains date {d}, which is not a supported format.')
    duration = data['duration']
    if type(duration) is not int:
      raise MetadataException(f'File {path} has a duration {duration} that is not an integer.')
    return (timestamp, duration)
  except Exception as e:
    raise MetadataException(f'Unable to parse {path} for video metadata.')

def get_gapped_files(directory: str, threshold_lower: int, threshold_upper: int):
  flagged_pairs = []
  pq = get_full_file_list(directory)
  if not pq or pq.empty():
    return []

  prev = None
  prev_dt = None
  prev_dur_ms = None

  # Find the first video file in the queue
  while not pq.empty():
    prev = pq.get()
    try:
      prev_dt, prev_dur_ms = get_video_duration_time(prev)
      break
    except MetadataException:
      # Might not be a video file, which is fine. Skip it.
      pass

  if prev_dt is None:
    print(f'There were no valid video files in {directory}!')
    return []

  max_length = 0
  # Iterate through every file
  while not pq.empty():
    cur = pq.get()
    max_length = max(len(cur), max_length)
    print(f'Processing {cur}...'.ljust(max_length + 14), end='\r')

    try:
      cur_dt, cur_dur_ms = get_video_duration_time(cur)
      expected_cur_time = prev_dt + timedelta(milliseconds=prev_dur_ms)
      diff = cur_dt - expected_cur_time
      diff = diff / timedelta(milliseconds=1)
      if diff > threshold_lower and diff < threshold_upper:
        flagged_pairs.append((prev, cur, int(diff)))
      prev = cur
      prev_dt = cur_dt
      prev_dur_ms = cur_dur_ms
    except MetadataException:
      # Might not be a video file, which is fine. Skip it.
      pass
  return flagged_pairs

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Flag files that appear to have a gap in footage from the previous file.')
  parser.add_argument('--dir', '-d', required=True, type=str, help='Path to the directory containing the video recording files.')
  parser.add_argument('--threshold_lower', '-l', default=LOWER_THRESHOLD_MS, type=int, help='Specify the minimum gap size to flag as bad in milliseconds. Defaults to 500ms.')
  parser.add_argument('--threshold_upper', '-u', default=UPPER_THRESHOLD_MS, type=int, help='Specify the maximum gap size to flag as bad in milliseconds. Defaults to 30s.')
  args = parser.parse_args()

  flagged_files = get_gapped_files(args.dir, args.threshold_lower, args.threshold_upper)
  for prev, next, diff in flagged_files:
    prev = prev.replace(args.dir, '...')
    next = next.replace(args.dir, '...')
    print(f'Detected {diff}ms gap between "{prev}" and "{next}"')
  if not flagged_files:
    print('No footage gaps detected!')