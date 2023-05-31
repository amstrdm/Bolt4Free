# Bolt4Free
A Python Script exploiting a practical vulnerability in the Bolt E-Scooter app which makes it possible to use the E-Scooters without any charge

# Bolt Scooter Ride Automation

Bolt4Free is a Python script that exploits a practical vulnerability in the Bolt E-Scooter app, allowing you to use the E-Scooters without any charge. The script takes advantage of the facts that Bolt has no unlock fee, so a ride can be started and terminated as many times as desired and that if the duration of a ride is under a given timeframe there will be no charge.

## Prerequisites
- Bolt account with a confirmed Payment method set up
- Burpsuit to intercept `HTTP` requests and get the information below (more on how to get Burpsuit set up on mobile under [Intercepting Requests with Burp Suite](https://github.com/amstrdm/Bolt4Free/edit/main/README.md#intercepting-requests-with-burp-suite)

Before running this program, you need to have the following information:

- `cookie`: The cookie value required for authentication.
- `authorization`: The authorization value required for authentication (e.g., Basic KzQ5MTc2NzA4Njc1MDQ6MUZCRjAwMEYtQkQzRC00RjgwLUE5NUItRUZFODg4RjYzQzVB).
- `payment_instrument_id`: The ID of the payment instrument (e.g., adyen_paypal/6837466090316059).
- `user_agent` (optional): The user agent string to be used in the requests. The default value is "Bolt/109764413 CFNetwork/1390 Darwin/22.0.0".

- All of these values can be obtained from any `http` request outgoing from the Bolt mobile app

## Installation

To run the Bolt4Free script, you need to have the requests module installed. If you don't have it installed, you can install it using pip:
```
pip install requests
```
After the requirements are installed clone the repository:
```
git clone https://github.com/amstrdm/Bolt4Free.git
```

## Usage
Before running the script, make sure to modify the following variables in the code:

- `Cookie`: Replace with the value of the `Cookie` header from the requests intercepted by Burp Suite.
- `Authorization`: Replace with the value of the `Authorization` header from the requests intercepted by Burp Suite.
- `Payment_instrument_id`: Replace with the value of the `payment_instrument_id` parameter from the requests intercepted by Burp Suite.

Additionally, you can change the `user_agent` variable to match your desired user agent.

After that you can execute the script normally with Python:
```
cd Bolt4Free
python3 bolt4free.py
```


## Intercepting Requests with Burp Suite

To obtain the required variables (`Cookie`, `Authorization`, `Payment_instrument_id`), you can redirect the POST requests from your phone's Bolt app to a computer running Burp Suite. This allows you to capture the requests and extract the necessary values. You can find instructions on how to redirect requests from a phone to Burp Suite [here](https://portswigger.net/support/configuring-an-android-device-to-work-with-burp).

Please note that this process may require technical expertise and is intended for educational purposes only.

---

## Program Flow

The program follows the following steps:

1. `get_user_input()`: Prompts the user to enter the ID of their Bolt scooter.
2. `create_and_start_order`: Sends a POST request to the Bolt API to create and start the ride. Returns the response.
3. `extract_order_id`: Extracts the "order_id" from the response JSON.
4. `getactive1`: Sends a POST request to the Bolt API to get the active ride details. Returns the response.
5. `extract_getactive1_order_id`: Extracts the "getactive1_id_value" from the response JSON.
6. `getactive2`: Sends a second POST request to the Bolt API to get the active ride details (this request may be unnecessary and can potentially be removed).
7. `finish1`: Sends a POST request to the Bolt API to finish the ride (first step).
8. `finish2`: Sends a POST request to the Bolt API to finish the ride (second step, confirms termination).
9. Waits for the specified duration (50 seconds) to simulate the ride duration.
10. Sends requests to finish the ride and waits for the confirmation response.

## Error Handling

The program performs basic error handling. If any of the requests fail or return an unexpected response, an error message will be printed. The program will exit in case of an error.

### Disclaimer

- The Bolt4Free project is for educational purposes and is part of a Bug Bounty program. The creator of the project is not responsible for any explicit or illegal acts performed with the program. Use this script responsibly and at your own risk.

- Please Note that there is currently no "safe" way to exit the Program as that would require threading which will probably be added later on, therefore when terminating the program it is important to check on the official Bolt app if the Ride got terminated as chances are the program broke out of the loop early and therefore didn't send the necessary `POST` requests to terminate the ride.

- Note: This program is provided as-is and may require adjustments based on any changes to the Bolt API or the authentication process.
