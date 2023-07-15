import logging
import json
import requests
import threading
from time import sleep
import config

class HTTPClient:
    def __init__(self, base_url, cookie, authorization, user_agent):
        """
        Initializes an HTTP client with the necessary credentials and headers.

        Args:
            base_url (str): The base URL of the API.
            cookie (str): The cookie value for authentication.
            authorization (str): The authorization value for authentication.
            user_agent (str): The user agent string for the request headers.
        """
        self.base_url = base_url
        self.cookie = cookie
        self.authorization = authorization
        self.user_agent = user_agent

    def send_request(self, endpoint, body):
        """
        Sends an HTTP POST request to the specified endpoint with the given request body.

        Args:
            endpoint (str): The endpoint to send the request to.
            body (dict): The request body in JSON format.

        Returns:
            requests.Response: The response object.

        Raises:
            requests.exceptions.RequestException: If an error occurs during the request.
        """
        url = self.base_url + endpoint
        headers = {
            "Host": "germany-rental.taxify.eu",
            "Cookie": self.cookie,
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Content-Length": str(len(json.dumps(body))),
            "Accept-Encoding": "gzip, deflate",
            "Authorization": self.authorization,
            "User-Agent": self.user_agent,
            "Accept-Language": "en-GB,en;q=0.9",
            "Cache-Control": "no-cache"
        }

        try:
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logging.error("Error sending request: %s", e)
            return None

class BoltScooter:
    def __init__(self, http_client, payment_instrument_id):
        """
        Initializes a BoltScooter instance with an HTTP client and payment instrument ID.

        Args:
            http_client (HTTPClient): The HTTP client to use for making requests.
            payment_instrument_id (str): The payment instrument ID.
        """
        self.http_client = http_client
        self.payment_instrument_id = payment_instrument_id

    def start_ride(self, vehicle_handle):
        """
        Starts a ride with the specified vehicle handle.

        Args:
            vehicle_handle (str): The ID of the Bolt scooter.

        """
        create_and_start_body = {
            "vehicle_handle": {
                "value": vehicle_handle,
                "type": "uuid",
            },
            "source": "single_order",
            "payment_instrument_id": self.payment_instrument_id
        }

        # Send createAndStart request
        response = self.http_client.send_request("createAndStart", create_and_start_body)
        if response:
            logging.info("Response from createAndStart: %s", response.text)
            id_value = response.json().get('data', {}).get('order', {}).get('id')

            getactive_body = {
                "source": "single_order",
                "order_id": id_value,
                "vehicle_handle": {
                    "value": vehicle_handle,
                    "type": "uuid"
                }
            }

            # Send getActive request
            getactive_response = self.http_client.send_request("getActive", getactive_body)
            if getactive_response:
                getactive_id_value = getactive_response.json().get('data', {}).get('order', {}).get('id')

                # Start termination thread
                termination_thread = threading.Thread(
                    target=self.terminate_ride_after_delay,
                    args=(getactive_id_value,)
                )
                termination_thread.start()

    def terminate_ride_after_delay(self, getactive_id_value):
        """
        Terminates the ride after a delay.

        Args:
            getactive_id_value (str): The ID of the active ride.
        """
        sleep(50)  # Wait for 50 seconds before terminating the ride

        finish1_body = {
            "gps_lat": "50.092434640968932",
            "order_id": getactive_id_value,
            "gps_lng": "8.2257654130646571"
        }

        # Send finish1 request
        finish1_response = self.http_client.send_request("finish", finish1_body)
        if finish1_response:
            logging.info("Finish1 request sent: Waiting for confirmation...")

        finish2_body = {
            "order_id": getactive_id_value,
            "gps_lng": 8.2257654130646571,
            "gps_lat": 50.092434640968932,
            "confirmed_view_keys": ["photo_capture_key"]
        }

        # Send finish2 request
        finish2_response = self.http_client.send_request("finish", finish2_body)
        if finish2_response:
            logging.info("Finish2 request sent: Ride termination request completed successfully")
    
def get_configuration():
    """
    Retrieves the configuration values for the HTTP client and BoltScooter.

    Returns:
        tuple: A tuple containing the configuration values (base_url, cookie, authorization,
            payment_instrument_id, user_agent).
    """
    # Get configuration values from config module or any other source
    base_url = config.BASE_URL
    cookie = config.COOKIE
    authorization = config.AUTHORIZATION
    payment_instrument_id = config.PAYMENT_INSTRUMENT_ID
    user_agent = config.USER_AGENT

    return base_url, cookie, authorization, payment_instrument_id, user_agent

def main():
    # Get the configuration values
    base_url, cookie, authorization, payment_instrument_id, user_agent = get_configuration()

    # Create an HTTP client and BoltScooter instance
    http_client = HTTPClient(base_url, cookie, authorization, user_agent)
    scooter = BoltScooter(http_client, payment_instrument_id)

    # Prompt user for vehicle handle
    vehicle_handle = input("Please enter the id of your Bolt scooter (Placed under the scannable QR code): ")

    # Start the ride
    scooter.start_ride(vehicle_handle)

if __name__ == "__main__":
    # Set up logging configuration
    logging.basicConfig(level=logging.INFO)

    # Run the main function
    main()