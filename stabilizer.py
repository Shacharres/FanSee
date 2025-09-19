"""
This module is intended to ensure that the controller is not jumpy. 
We don't want the fan to change directions and speeds too often, or to be affected by people that walk by it without lingering around.
A simple stabilizer would break the image into a grid and maintain a cyclic buffer that counts when there was an object inside each cell
within the last N frames. The controller would then only react to cells that have had an object in them for at least M out of the last N frames.
"""

import numpy as np

import config
from utils import get_center_pixels


grid_size = config.OPTICAL_H // 10, config.OPTICAL_W // 10


def init_stabilizer(n_frames: int):
    history = np.zeros((n_frames, *grid_size), dtype=np.uint8)
    return history


def update_buffer(history: np.ndarray, current_boxes: list[list[int]]) -> np.ndarray:
    """Updates the history buffer with this frame's detections."""
    history[1:] = history[:-1]  # shift history buffer
    history[0, :] = 0  # clear the first frame, to be filled with new data
    
    for box in current_boxes:
        x1, y1, x2, y2 = box
        relevant_bounds = np.round(np.array([x1, x2, y1, y2]) / 10).astype(int)
        history[0, np.clip(relevant_bounds[2], 0, grid_size[0]-1):np.clip(relevant_bounds[3]+1, 0, grid_size[0]),
                   np.clip(relevant_bounds[0], 0, grid_size[1]-1):np.clip(relevant_bounds[1]+1, 0, grid_size[1])] += 1
        # for y in range(relevant_bounds[2], np.min([relevant_bounds[3] + 1, grid_size[0]])):
        #     for x in range(relevant_bounds[0], np.min([relevant_bounds[1] + 1, grid_size[1]])):
        #         # if 0 <= y < grid_size[0] and 0 <= x < grid_size[1]:
        #             history[0, y, x] += 1
    return history


def get_stable_cells(history: np.ndarray, threshold: int) -> np.ndarray:
    """Returns the cells that have been stable for at least `threshold` frames."""
    return np.where(history.sum(axis=0) >= threshold, 1, 0)



def get_stable_islands(history: np.ndarray, threshold: int) -> list[list[int]]:  # todo test
    """Returns the bounding boxes of the stable cells."""
    # do island detection to group adjacent cells and return a single box for each group
    stable_cells = get_stable_cells(history, threshold)
    
    boxes = []
    visited = np.zeros_like(stable_cells)

    def dfs(y, x):
        stack = [(y, x)]
        min_x, max_x, min_y, max_y = x, x, y, y
        while stack:
            cy, cx = stack.pop()
            if visited[cy, cx]:
                continue
            visited[cy, cx] = 1
            min_x = min(min_x, cx)
            max_x = max(max_x, cx)
            min_y = min(min_y, cy)
            max_y = max(max_y, cy)
            for ny, nx in [(cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)]:
                if 0 <= ny < stable_cells.shape[0] and 0 <= nx < stable_cells.shape[1]:
                    if stable_cells[ny, nx] == 1 and not visited[ny, nx]:
                        stack.append((ny, nx))
        boxes.append([min_x * 10, min_y * 10, (max_x + 1) * 10, (max_y + 1) * 10])

    return boxes


def is_box_within_stable_cell(box: list[int], stable_cells: np.ndarray) -> bool:
    """ Returns True if the box is within any of the stable cells. """
    x1, y1, x2, y2 = box
    relevant_grid_bounds = np.round(np.array([x1, x2, y1, y2]) / 10).astype(int)
    if np.any(stable_cells[relevant_grid_bounds[2]:relevant_grid_bounds[3]+1, relevant_grid_bounds[0]:relevant_grid_bounds[1]+1]):  
        return True
    return False


def get_stable_boxes(history: np.ndarray, current_frame_boxes: list[list[int]], threshold: int) -> list[list[int]]:
    """ Returns the boxes from the current frame that should be considered as fan candidates since they are in stable areas. """
    to_consider = get_stable_cells(history, threshold)
    if not np.any(to_consider): return [], []
    stable_boxes = []
    for box in current_frame_boxes:
        if is_box_within_stable_cell(box, to_consider):
            stable_boxes.append(box)
    stable_centers = get_center_pixels(stable_boxes)
    return stable_boxes, stable_centers


if __name__ == "__main__":
    history = init_stabilizer(config.STABILIZER_N_FRAMES)
    # simulate some boxes
    for _ in range(300):
        x1 = np.random.randint(0, config.OPTICAL_W)
        y1 = np.random.randint(0, config.OPTICAL_H)
        x2 = np.random.randint(0, config.OPTICAL_W)
        y2 = np.random.randint(0, config.OPTICAL_H)
        boxes = [[x1, y1, min(x1 + 100, config.OPTICAL_W), min(y1 + 100, config.OPTICAL_H)], [x2, y2, min(x2 + 100, config.OPTICAL_W), min(y2 + 100, config.OPTICAL_H)]]
        history = update_buffer(history, boxes)
    stable = get_stable_boxes(history, boxes, config.STABILIZER_M_FRAMES)
    print(stable)