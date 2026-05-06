"""
Ball rendering: main ball, highlight, and ghost copies.

Separated from the Ball entity so that rendering can vary by game type
(e.g., Infinite mode adds ghost copies) without modifying the entity.
All functions take a Ball and drawing parameters — no side effects.
"""

import pygame


def ball_to_pixel(ball, cell_size, ox, oy):
    """Convert a ball's grid position to pixel coordinates.

    Returns:
        (px, py, pr) — pixel center X, center Y, and pixel radius.
        pr is clamped to min 2 to stay visible on very small windows.
    """
    px = int(ox + ball.gx * cell_size)
    py = int(oy + ball.gy * cell_size)
    pr = max(int(ball.radius * cell_size), 2)
    return px, py, pr


def draw_ball(surface, ball, cell_size, ox, oy):
    """Draw a ball as a filled circle with a small highlight dot.

    The highlight is a lighter circle offset to the upper-left, giving
    a subtle 3D depth effect. The +90 brightness shift on the highlight
    is clamped to 255 to prevent overflow.

    Args:
        surface: Target pygame surface.
        ball: Ball entity with .color, .gx, .gy, .radius.
        cell_size, ox, oy: Scaling parameters from get_scaling().
    """
    px, py, pr = ball_to_pixel(ball, cell_size, ox, oy)
    # Main ball circle
    pygame.draw.circle(surface, ball.color, (px, py), pr)
    # Small highlight for depth — offset to upper-left
    highlight = tuple(min(255, c + 90) for c in ball.color)
    pygame.draw.circle(surface, highlight,
                       (px - pr // 4, py - pr // 4), max(pr // 3, 1))


def draw_ghost(surface, ball, cols, rows, cell_size, ox, oy):
    """Draw faded ghost copies of a ball near wrapping edges.

    In Infinite mode, when a ball is within 1.5 cells of a portal edge,
    a dimmed copy is drawn on the opposite side of the screen. This
    previews where the ball will appear after wrapping.

    Ghost color is the ball color at 50% brightness. Only draws ghosts
    for axes where the ball is near the edge.

    Args:
        surface: Target surface.
        ball: Ball entity near a wrapping edge.
        cols, rows: Grid dimensions for wrap offset calculation.
        cell_size, ox, oy: Scaling parameters.
    """
    margin = 1.5  # How close to the edge (in grid cells) to show a ghost
    offsets = []
    # Check horizontal proximity to edges
    if ball.gx < margin:
        offsets.append((cols, 0))   # Ghost appears on the right side
    elif ball.gx > cols - margin:
        offsets.append((-cols, 0))  # Ghost appears on the left side
    # Check vertical proximity
    if ball.gy < margin:
        offsets.append((0, rows))   # Ghost appears at the bottom
    elif ball.gy > rows - margin:
        offsets.append((0, -rows))  # Ghost appears at the top

    for gox, goy in offsets:
        px = int(ox + (ball.gx + gox) * cell_size)
        py = int(oy + (ball.gy + goy) * cell_size)
        pr = max(int(ball.radius * cell_size), 2)
        # 50% brightness for the ghost effect
        ghost_color = tuple(c // 2 for c in ball.color)
        pygame.draw.circle(surface, ghost_color, (px, py), pr)


def draw_ghost_portal(surface, ball, portal_map, cols, rows, cell_size, ox, oy):
    """Draw faded ghost copies at destination portals.

    When a ball is near a portal opening, a dimmed copy appears at the
    destination portal's position to preview where the ball will emerge.
    Works with randomly-paired portals — the ghost appears at the actual
    destination, not just the opposite side.

    Args:
        surface: Target surface.
        ball: Ball entity near a portal edge.
        portal_map: dict mapping (edge, pos) → (dest_edge, dest_pos).
        cols, rows: Grid dimensions.
        cell_size, ox, oy: Scaling parameters.
    """
    margin = 1.5
    ghosts = []

    # Check all four edges for nearby portals
    if ball.gx < margin:
        dest = portal_map.get(("left", int(ball.gy)))
        if dest:
            ghosts.append(dest)
    if ball.gx > cols - margin:
        dest = portal_map.get(("right", int(ball.gy)))
        if dest:
            ghosts.append(dest)
    if ball.gy < margin:
        dest = portal_map.get(("top", int(ball.gx)))
        if dest:
            ghosts.append(dest)
    if ball.gy > rows - margin:
        dest = portal_map.get(("bottom", int(ball.gx)))
        if dest:
            ghosts.append(dest)

    ghost_color = tuple(c // 2 for c in ball.color)
    pr = max(int(ball.radius * cell_size), 2)
    for edge, pos in ghosts:
        if edge == "left":
            gx, gy = 0.5, pos + 0.5
        elif edge == "right":
            gx, gy = cols - 0.5, pos + 0.5
        elif edge == "top":
            gx, gy = pos + 0.5, 0.5
        else:
            gx, gy = pos + 0.5, rows - 0.5
        px = int(ox + gx * cell_size)
        py = int(oy + gy * cell_size)
        pygame.draw.circle(surface, ghost_color, (px, py), pr)
