#Goal: Get real time bus times for a stop and route

#Version: 0.2
# Updated version to change route finding logic
# Currenly not using real time data

# GFTS Stop by Code = Stop ID
# GTFS Routes by Stop = Route ID
# GTFS Trips by Route = trip ids
# GTFS Stop Times by Id = Stop time

import http.client, urllib.request, urllib.parse, urllib.error, base64
import json
import datetime
from datetime import timedelta
import time
from multiprocessing import Pool
import config #Contains API Key

#API Key - Create file named config.py that contains your key in named var
subscription_key = config.subscription_key

#Query Paramaters
#stop_name = "3907" #Source from https://at.govt.nz/bus-train-ferry/timetables/find-my-stop-or-station-on-a-map/
#stop_name = "7001"
#route_name = "923" 



#Request Headers
headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
}

# Request parameters
params = urllib.parse.urlencode({
    'callback': '',
})

def parse_json(data):
    data = json.loads(data)
    return(data)

def get_stop_word_name(stop_name):
    try:
        conn = http.client.HTTPSConnection('api.at.govt.nz')
        conn.request("GET", "/v2/gtfs/stops/stopCode/"+ stop_name +"?%s" % params, "", headers)
        response = conn.getresponse()
        data = response.read()
        data_dict = parse_json(data)
        stop_word_name = data_dict["response"][0]["stop_name"]
        conn.close()
        return stop_word_name

    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

def get_stop_word_name_long(stop_name):
    try:
        conn = http.client.HTTPSConnection('api.at.govt.nz')
        conn.request("GET", "/v2/gtfs/stops/stopId/"+ stop_name +"?%s" % params, "", headers)
        response = conn.getresponse()
        data = response.read()
        data_dict = parse_json(data)
        stop_word_name = data_dict["response"][0]["stop_name"]
        conn.close()
        return stop_word_name

    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

def get_stop_id(stop_name):
    try:
        conn = http.client.HTTPSConnection('api.at.govt.nz')
        conn.request("GET", "/v2/gtfs/stops/stopCode/"+ stop_name +"?%s" % params, "", headers)
        response = conn.getresponse()
        data = response.read()
        data_dict = parse_json(data)
        stop_id = data_dict["response"][0]["stop_id"]
        conn.close()
        return stop_id

    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

def get_route_id(stop_id, route_name):
    try:
        conn = http.client.HTTPSConnection('api.at.govt.nz')
        conn.request("GET", "/v2/gtfs/routes/stopid/"+ stop_id +"?%s" % params, "", headers)
        response = conn.getresponse()
        data = response.read()
        data_dict = parse_json(data)
        conn.close()
        for item in data_dict["response"]:
            if item["route_short_name"] == route_name:
                route_id = item["route_id"]
                conn.close()
                print("Route ID: " + route_id)
                return route_id
            else:
                pass  
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

def get_trip_ids(route_id):
    try:
        trips = []
        conn = http.client.HTTPSConnection('api.at.govt.nz')
        conn.request("GET", "/v2/gtfs/trips/routeId/"+ route_id +"?%s" % params, "", headers)
        response = conn.getresponse()
        data = response.read()
        data_dict = parse_json(data)
        for trip in data_dict["response"]:
            trips.append(trip["trip_id"])
        conn.close()
        return trips

    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

def get_stop_times(stop_id):
    try:
        conn = http.client.HTTPSConnection('api.at.govt.nz')
        conn.request("GET", "/v2/gtfs/stopTimes/stopId/"+ stop_id +"?%s" % params, "", headers)
        response = conn.getresponse()
        data = response.read()
        data_dict = parse_json(data)
        stop_times = []
        for item in data_dict["response"]:
            stop_times.append(item)
        conn.close()
        return stop_times

    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

def get_live_updates(trip_id):
    params = urllib.parse.urlencode({
    'callback': '',
    'tripid': trip_id,
    })
    try:
        conn = http.client.HTTPSConnection('api.at.govt.nz')
        conn.request("GET", "/v2/public/realtime/tripUpdates/"+"?%s" % params, "", headers)
        response = conn.getresponse()
        data = response.read()
        data_dict = parse_json(data)
        conn.close()
        if data_dict["response"]["entity"] == []:
            return "no data"
        return data_dict

    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))


def get_next_bus(route_name, stop_name, minutes_to_stop):
    #print("Getting Stop ID")
    stop_id = get_stop_id(stop_name)
    print("Stop ID: " + stop_id)
    #print("Getting Route ID")
    route_id = get_route_id(stop_id, route_name)

    #print("Getting Trip IDs")
    trip_ids = get_trip_ids(route_id)

    #print("Getting Stop Times")
    all_stop_times = []
    stop_times = []
    all_stop_times = get_stop_times(stop_id)
    for stop_time in all_stop_times:
        if stop_time["trip_id"] in trip_ids:
            stop_times.append(stop_time["arrival_time"])
    data = dict(zip(trip_ids, stop_times))

    #print("Getting Next Bus Time")
    now = datetime.datetime.now()
    now = now.strftime("%H:%M:%S")
    now = datetime.datetime.strptime(now, "%H:%M:%S")
    next_bus = []
    actual_bus_time = ""
    max_time = datetime.datetime.strptime("23:59:59", "%H:%M:%S")
    for key, value in data.items():
        value = datetime.datetime.strptime(value, "%H:%M:%S")
        if value > now and value < max_time:
            value = value.strftime("%H:%M:%S")
            next_bus.append(value)
            if value == min(next_bus):
                current_trip = key
                max_time = datetime.datetime.strptime(value, "%H:%M:%S")
    if next_bus == []:
        return "no more buses today", "no more buses today"
    next_bus = min(next_bus)
    next_bus = datetime.datetime.strptime(next_bus, "%H:%M:%S")
    next_bus = next_bus.strftime("%I:%M %p")
 

#    print("Getting Live Updates")
    live_data = get_live_updates(current_trip)
    if live_data == "no data":
        print("No data/Bus not on route")
    else:
        for item in live_data["response"]["entity"]:
            if item["trip_update"]["trip"]["trip_id"] == current_trip:
                bus_stop_id = item["trip_update"]["stop_time_update"]["stop_id"]
                bus_stop_name = get_stop_word_name_long(stop_name)
                print("Bus is at", bus_stop_name)
                while True:
                    try:
                        bus_delay = item["trip_update"]["stop_time_update"]["departure"]["delay"]
                        break
                    except:
                        pass
                    try:
                        bus_delay = item["trip_update"]["stop_time_update"]["arrival"]["delay"]
                        break
                    except:
                        print("An error occured when getting bus delay")
                bus_delay = bus_delay/60
                print("Bus is", round(bus_delay,2), "minutes late")
                #Calculate bus time with delay
                actual_bus_time = datetime.datetime.strptime(next_bus, "%I:%M %p")
                actual_bus_time = actual_bus_time + datetime.timedelta(minutes=bus_delay)
                actual_bus_time = actual_bus_time.strftime("%I:%M %p")
                print("Bus is due at", actual_bus_time)
        if actual_bus_time == "":
            actual_bus_time = next_bus
    if next_bus == [] or actual_bus_time == "":
        return "", "", ""
    else:
        given_time = datetime.datetime.strptime(actual_bus_time, "%I:%M %p")
        final_time = given_time - timedelta(minutes=minutes_to_stop)
        final_time = final_time.strftime("%I:%M %p")
        
        return next_bus, actual_bus_time, final_time

if __name__ == "__main__":
    start_time = time.time()
    next_bus, actual_bus_time, final_time = get_next_bus("923", "7001", 5)
    if next_bus != "" and actual_bus_time != "":
        print("Scheduled arrival time: ", next_bus)
        print("Leave at: ", final_time)
    print("--- %s seconds ---" % (time.time() - start_time))