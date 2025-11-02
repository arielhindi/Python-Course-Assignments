
def circle_area(radius):
    """
    Calculate the area of a circle using the radius.

    Formula: Area = (radius**2 * pi)

    Args:
        radius (float): The radius of the circle

    Returns:
        float: The area of the circle
    """
    area = (radius**2 * 3.14159)
    return area


# Example usage
if __name__ == "__main__":
    #pass
    #...
    # Get radius from user input
    try:
        radius = float(input("Enter the radius of the circle: "))

        # Calculate and display the area
        area = circle_area(radius)
        print(f"Circle with radius {radius} has area: {area}")

    except ValueError:
        print("Please enter valid numbers for radius.")
