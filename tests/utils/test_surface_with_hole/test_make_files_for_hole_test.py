

def make_radiative_surface_with_hole():
    """
    Test the object_method_wrapper function.
    """
    # Example usage:
    surface = [(0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0)]
    hole = [(4, 4, 0), (6, 4, 0), (6, 6, 0), (4, 6, 0)]  # First hole

    # Get the contoured surface with multiple holes
    contoured_surface = contour_surface_with_hole(surface, hole)
    # Convert to a PyVista PolyData object for visualization
    face = np.array([[len(contoured_surface)] + list(range(len(contoured_surface)))])
    surface_polydata = pv.PolyData(contoured_surface, face)
    print (contoured_surface)

    # # Visualize the contoured surface with holes
    plotter = pv.Plotter()
    plotter.add_mesh(surface_polydata, color='cyan', line_width=2)

    plotter.show()
