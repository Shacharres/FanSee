"""
Utility functions for various tasks.
"""

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))



# =========== Basic Detection helpers ============
def get_center_pixels(ppl_boxes):
    """
    Compute center (x,y) pixel for each detected person box.
    
    Args:
        ppl_boxes (list of tuple): list of (x1, y1, x2, y2)
    
    Returns:
        centers (list of tuple): list of (x_center, y_center)
    """
    centers = []
    for (x1, y1, x2, y2) in ppl_boxes:
        xc = int((x1 + x2) / 2)
        yc = int((y1 + y2) / 2)
        centers.append((xc, yc))
    return centers