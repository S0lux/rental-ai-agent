import os;
import lib.postgresql_connector as pg_connector;

from dotenv import load_dotenv;
from typing import Annotated;

env_path = os.path.join(os.path.dirname(__file__), '..', '.env');
load_dotenv(dotenv_path=env_path);

_connector = pg_connector.PostgresqlConnector();
_connector.connect();

def find_customer_by_email(
    email: Annotated[str, "The email address of the customer"]
):
    """
    Finds a customer by their email address.
    :param email: The email address of the customer.
    :return: Customer data if found, otherwise None.
    """
    query = "SELECT * FROM customer WHERE email = %s"
    try:
        cursor = _connector.execute_query(query, (email,))
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(f"Error finding customer by email: {e}")
        return None

def find_film_by_title(
    title: Annotated[str, "The title of the film"]
):
    """
    Finds a film by its title.
    :param title: The title of the film.
    :return: Film data if found, otherwise None.
    """
    query = "SELECT * FROM film WHERE title = %s"
    try:
        cursor = _connector.execute_query(query, (title,))
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(f"Error finding film by title: {e}")
        return None

def find_films_with_similar_title(
    title: Annotated[str, "The title of the film to search for"]
):
    """
    Finds films with similar titles.
    :param title: The title of the film to search for.
    :return: List of films with similar titles.
    """
    query = "SELECT * FROM film WHERE title ILIKE %s"
    try:
        cursor = _connector.execute_query(query, (f"%{title}%",))
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"Error finding films with similar title: {e}")
        return []

def check_film_availability(
    film_id: Annotated[int, "The ID of the film to check"]
):
    """
    Determines if at least one copy of the specified film is currently available for rental (i.e., not checked out).
    :param film_id: The unique identifier of the film to check.
    :return: True if at least one copy is available to rent, False if all are currently rented out or on error.
    """
    query = """
            SELECT i.inventory_id
            FROM inventory i
            LEFT JOIN rental r ON i.inventory_id = r.inventory_id AND r.return_date IS NULL
            WHERE i.film_id = %s
            AND r.rental_id IS NULL;
            """
    try:
        cursor = _connector.execute_query(query, (film_id,))
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        print(f"Error checking film availability: {e}")
        return False

def rent_film(
    customer_id: Annotated[int, "The ID of the customer"], 
    film_id: Annotated[int, "The ID of the film to rent"], 
    staff_id: Annotated[int, "The ID of the staff processing the rental"]
):
  """
  Rents a film to a customer.
  :param customer_id: The ID of the customer.
  :param film_id: The ID of the film to rent.
  :param staff_id: The ID of the staff processing the rental.
  :return: Rental ID if successful, None otherwise.
  """
  # Check if the customer has rented any film in the last 24 hours
  check_rental_query = """
          SELECT COUNT(*)
          FROM rental
          WHERE customer_id = %s
            AND rental_date >= (NOW() - INTERVAL '24 HOURS');
          """
  try:
      last_24_hours_rental_count = _connector.execute_query(check_rental_query, (customer_id,)).fetchone()[0]
      if last_24_hours_rental_count > 0:
          print("Error: Customer has already rented a film in the last 24 hours.")
          return None

      query = """
              INSERT INTO rental (rental_date, inventory_id, customer_id, staff_id)
              SELECT NOW(), i.inventory_id, %s, %s
              FROM inventory i
              LEFT JOIN rental r ON i.inventory_id = r.inventory_id AND r.return_date IS NULL
              WHERE i.film_id = %s
                AND r.rental_id IS NULL
              LIMIT 1
              RETURNING rental_id;
              """
      
      cursor = _connector.execute_query(query, (customer_id, staff_id, film_id))
      rental_id = cursor.fetchone()
      return rental_id[0] if rental_id else None
  except Exception as e:
      print(f"Error renting film: {e}")
      return None
    
def get_customer_rental_history(
    customer_id: Annotated[int, "The ID of the customer"]
):
    """
    Retrieves the rental history of a customer.
    :param customer_id: The ID of the customer.
    :return: List of rentals for the customer.
    """
    query = """
            SELECT
              c.customer_id,
              c.first_name,
              c.last_name,
              r.rental_id,
              r.rental_date,
              f.title AS film_title,
              r.return_date
            FROM
              customer c
            JOIN
              rental r ON c.customer_id = r.customer_id
            JOIN
              inventory i ON r.inventory_id = i.inventory_id
            JOIN
              film f ON i.film_id = f.film_id
            WHERE
              c.customer_id = %s
            ORDER BY
              r.rental_date DESC;
            """
    try:
        cursor = _connector.execute_query(query, (customer_id,))
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"Error retrieving customer rental history: {e}")
        return []

def close_connection():
    """Closes the database connection."""
    if _connector:
        _connector.disconnect()
        print("Database connection closed.");
