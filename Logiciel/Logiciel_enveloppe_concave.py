import numpy as np
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt
from collections import defaultdict

def calculate_angles(p1, p2, p3):
    # Calcul des longueurs de chaque côté
    a = np.linalg.norm(p2 - p3)  # opposé à p1
    b = np.linalg.norm(p1 - p3)  # opposé à p2
    c = np.linalg.norm(p1 - p2)  # opposé à p3

    # Calcul de chaque angle (en radians)
    angle_p1 = np.arccos((b**2 + c**2 - a**2) / (2 * b * c))
    angle_p2 = np.arccos((a**2 + c**2 - b**2) / (2 * a * c))
    # angle_p3 = np.arccos((a**2 + b**2 - c**2) / (2 * a * b))

    # Conversion en degrés
    angle_p1_deg = np.degrees(angle_p1)
    angle_p2_deg = np.degrees(angle_p2)
    # angle_p3_deg = np.degrees(angle_p3)

    # L'angle opposé à p3 est angle_p3_deg
    return angle_p1_deg, angle_p2_deg

def find_boundary_edges(triangles):
    """
    Identify edges that belong to only one triangle (boundary edges).
    """
    edge_count = defaultdict(int)
    for tri in triangles:
        edges = [(tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])]
        for edge in edges:
            edge_count[tuple(sorted(edge))] += 1
    return {edge for edge, count in edge_count.items() if count == 1}

def filter_triangles_on_edge(points, triangles, min_angle=20, max_angle=60):
    """
    Remove triangles on the edge with boundary angles not in [min_angle, max_angle].
    """
    boundary_edges = find_boundary_edges(triangles)
    retained_triangles = []
    for tri_indices in triangles:
        edges = [(tri_indices[0], tri_indices[1]),
                 (tri_indices[1], tri_indices[2]),
                 (tri_indices[2], tri_indices[0])]

        is_removed = False
        for edge in edges:
            if tuple(sorted(edge)) in boundary_edges:
                # Calculate the angle opposite to the boundary edge
                opposite_point = list(set(tri_indices) - set(edge))[0]
                p1, p2, p3 = points[edge[0]], points[edge[1]], points[opposite_point]
                angle1, angle2 = calculate_angles(p1, p2, p3)
                # Si l'angle n'est pas dans l'intervalle [min_angle, max_angle], on retire le triangle
                if (angle1 < min_angle and angle2 < max_angle) or (angle2 < min_angle and angle1 < max_angle):
                    is_removed = True
                    break
        if not is_removed:
            retained_triangles.append(tri_indices)
    return np.array(retained_triangles)
def get_outer_shell(points, filtered_triangles):
    """
    Get the outer shell (boundary edges) of the remaining triangles.
    Returns the edges as a list of tuples: [((x1,y1),(x2,y2)), ...]
    """
    edge_count = defaultdict(int)
    for tri_indices in filtered_triangles:
        edges = [(tri_indices[0], tri_indices[1]),
                 (tri_indices[1], tri_indices[2]),
                 (tri_indices[2], tri_indices[0])]
        for edge in edges:
            edge_count[tuple(sorted(edge))] += 1

    boundary_edges = [edge for edge, count in edge_count.items() if count == 1]

    # Convertir chaque edge en ((x1, y1), (x2, y2)) plutôt que (array([...]), array([...]))
    boundary_coords = []
    for e in boundary_edges:
        p1 = points[e[0]]
        p2 = points[e[1]]
        # Convertir l'array NumPy en tuple
        p1_tuple = (float(p1[0]), float(p1[1]))
        p2_tuple = (float(p2[0]), float(p2[1]))
        boundary_coords.append(p1_tuple)
        boundary_coords.append(p2_tuple)

    return boundary_coords

def enveloppe_concave(points):
    # Delaunay triangulation
    tri = Delaunay(points)

    filtered_triangles = tri.simplices
    stable = False
    triangle = len(filtered_triangles)
    while not stable:
        filtered_triangles = filter_triangles_on_edge(points, filtered_triangles)
        # outer_shell contiendra maintenant une liste de paires de coordonnées
        triangle_new = len(filtered_triangles)
        if triangle_new == triangle:
            stable = True
        else:
            triangle = triangle_new
        # print(f"{len(filtered_triangles)} triangles conservés, {len(outer_shell)} arêtes en coquille extérieure.")
        outer_shell = get_outer_shell(points, filtered_triangles)

    return outer_shell
