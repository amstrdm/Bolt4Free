from time import sleep
import config
import json
import logging
import requests
import threading

logging.basicConfig(level=logging.INFO)

class HTTPClient:
    def __init__(self, base_url, cookie, authorization, user_agent):
        self.base_url = base_url
        self.cookie = cookie
        self.authorization = authorization
        self.user_agent = user_agent

    def send_request(self, endpoint, body):
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
        self.http_client = http_client
        self.payment_instrument_id = payment_instrument_id

    def start_ride(self, vehicle_handle):
        create_and_start_body = {
            "vehicle_handle": {
                "value": vehicle_handle,
                "type": "uuid",
            },
            "source": "single_order",
            "payment_instrument_id": self.payment_instrument_id
        }

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

            getactive_response = self.http_client.send_request("getActive", getactive_body)
            if getactive_response:
                getactive_id_value = getactive_response.json().get('data', {}).get('order', {}).get('id')

                termination_thread = threading.Thread(
                    target=self.terminate_ride_after_delay, 
                    args=(getactive_id_value,)
                )
                termination_thread.start()

    def terminate_ride_after_delay(self, getactive_id_value):
        sleep(50)  # Wait for 50 seconds before terminating the ride

        finish1_body = {
            "gps_lat": "50.092434640968932",
            "order_id": getactive_id_value,
            "gps_lng": "8.2257654130646571"
        }

        finish1_response = self.http_client.send_request("finish", finish1_body)
        if finish1_response:
            logging.info("Finish1 request sent: Waiting for confirmation...")

        finish2_body = {
            "order_id": getactive_id_value,
            "gps_lng": 8.2257654130646571,
            "gps_lat": 50.092434640968932,
            "confirmed_view_keys": ["photo_capture_key"]
        }

        finish2_response = self.http_client.send_request("finish", finish2_body)
        if finish2_response:
            logging.info("Finish2 request sent: Ride termination request completed successfully")

def main():
    base_url = config.BASE_URL
    cookie = config.COOKIE
    authorization = config.AUTHORIZATION
    payment_instrument_id = config.PAYMENT_INSTRUMENT_ID
    user_agent = config.USER_AGENT

    http_client = HTTPClient(base_url, cookie, authorization, user_agent)
    scooter = BoltScooter(http_client, payment_instrument_id)

    vehicle_handle = input("Please enter the id of your Bolt scooter (Placed under the scannable QR code): ")
    scooter.start_ride(vehicle_handle)

if __name__ == "__main__":
    main()