import cv2
import numpy as np

def draw_rounded_rectangle(img, start, end, color, radius=15, thickness=-1):
    x1, y1 = start
    x2, y2 = end
    
    overlay = img.copy()
    if thickness < 0:  # Filled rectangle
        cv2.rectangle(overlay, (x1 + radius, y1), (x2 - radius, y2), color, -1)
        cv2.rectangle(overlay, (x1, y1 + radius), (x2, y2 - radius), color, -1)
        cv2.circle(overlay, (x1 + radius, y1 + radius), radius, color, -1)
        cv2.circle(overlay, (x2 - radius, y1 + radius), radius, color, -1)
        cv2.circle(overlay, (x1 + radius, y2 - radius), radius, color, -1)
        cv2.circle(overlay, (x2 - radius, y2 - radius), radius, color, -1)
    else:  # Border only
        cv2.rectangle(overlay, (x1 + radius, y1), (x2 - radius, y2), color, thickness)
        cv2.rectangle(overlay, (x1, y1 + radius), (x2, y2 - radius), color, thickness)
        cv2.circle(overlay, (x1 + radius, y1 + radius), radius, color, thickness)
        cv2.circle(overlay, (x2 - radius, y1 + radius), radius, color, thickness)
        cv2.circle(overlay, (x1 + radius, y2 - radius), radius, color, thickness)
        cv2.circle(overlay, (x2 - radius, y2 - radius), radius, color, thickness)
    
    cv2.addWeighted(overlay, 0.8, img, 0.2, 0, img)

def overlay_image(frame, overlay, x, y):
    h, w = overlay.shape[:2]
    alpha = overlay[:, :, 3] / 255.0
    for c in range(3):
        frame[y:y + h, x:x + w, c] = (
            alpha * overlay[:, :, c] + 
            (1 - alpha) * frame[y:y + h, x:x + w, c]
        )

def draw_button(frame, text, icon_path, position, size, selected, hover=False):
    x, y = position
    w, h = size

    # Gradient colors
    top_color = (180, 220, 255) if selected else (200, 200, 200)
    bottom_color = (120, 170, 255) if selected else (150, 150, 150)

    if hover:
        top_color = tuple(min(c + 20, 255) for c in top_color)
        bottom_color = tuple(min(c + 20, 255) for c in bottom_color)

    # Gradient effect
    for i in range(h):
        alpha = i / h
        color = tuple(int((1 - alpha) * tc + alpha * bc) 
                     for tc, bc in zip(top_color, bottom_color))
        cv2.line(frame, (x, y + i), (x + w, y + i), color, 1)

    # Draw border
    cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 50), 2)

    # Draw icon
    icon = cv2.imread(icon_path, cv2.IMREAD_UNCHANGED)
    icon_size = min(h - 40, w - 40)
    icon_resized = cv2.resize(icon, (icon_size, icon_size))
    overlay_image(frame, icon_resized, 
                 x + (w - icon_resized.shape[1]) // 2, y + 10)

    # Draw text
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
    text_x = x + (w - text_size[0]) // 2
    text_y = y + h - 10
    cv2.putText(frame, text, (text_x, text_y), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)