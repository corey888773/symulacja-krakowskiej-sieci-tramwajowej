import math

def calculate_distance_based_on_t(t, t_max, v_max, a):
    t_full_speed = v_max / a

    if t < t_full_speed:
        return 0.5 * a * t * t
    
    if t < t_max - t_full_speed:
        return v_max * (t - 0.5 * t_full_speed)
    
    if t < t_max:
        return v_max * (t_max - 0.5 * t_full_speed) - 0.5 * a * (t_max - t) ** 2
    
def calculate_x_and_y_based_on_t(t, t_max, v_max, a, x0, y0, theta, distance_between_nodes):
    distance = calculate_distance_based_on_t(t, t_max, v_max, a)
    x = x0 + distance * math.cos(theta)
    y = y0 + distance * math.sin(theta)
    return x, y