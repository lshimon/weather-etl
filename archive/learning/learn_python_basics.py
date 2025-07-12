# LESSON 1: Variables and Basic Operations
print("=== PYTHON BASICS ===")

# Variables are like labeled boxes that store data
name = "Shimon"
age = 25
temperature = 27.5
is_sunny = True

print("My name is:", name)
print("I am", age, "years old")
print("Temperature:", temperature, "degrees")
print("Is it sunny?", is_sunny)

# Basic math operations
temp_in_fahrenheit = (temperature * 9/5) + 32
print("Temperature in Fahrenheit:", temp_in_fahrenheit)

print("\n" + "="*40)
print("LESSON 2: Working with different data types")

# Different types of data
city = "Tel Aviv"           # String (text)
current_temp = 27.5         # Float (decimal number) 
humidity = 60               # Integer (whole number)
has_rain = False           # Boolean (True/False)

print(f"City: {city} (type: {type(city)})")
print(f"Temperature: {current_temp} (type: {type(current_temp)})")
print(f"Humidity: {humidity} (type: {type(humidity)})")
print(f"Has rain: {has_rain} (type: {type(has_rain)})")

print("\n" + "="*40)
print("LESSON 3: Type Conversion (Fixing the mixing problem)")

# The problem you identified:
temp_as_string = "27.5"
number_to_add = 5

print("temp_as_string:", temp_as_string, "type:", type(temp_as_string))
print("number_to_add:", number_to_add, "type:", type(number_to_add))

# This would cause an error:
# result = temp_as_string + number_to_add  # ERROR!

# SOLUTIONS:
# Solution 1: Convert string to float
result1 = float(temp_as_string) + number_to_add
print("Solution 1 - Convert to float:", result1)

# Solution 2: Convert both to strings (joining text)
result2 = temp_as_string + str(number_to_add)
print("Solution 2 - Convert to strings:", result2)

print("\n" + "="*40)
print("LESSON 4: Understanding string operations")

# Breaking down the mystery line:
print("What does \\n + '='*40 do?")
print("\\n means: new line (like pressing Enter)")
print("'='*40 means: repeat = forty times")
print("Here it is:")
print("\n" + "="*40)
print("See? New line + 40 equal signs!")

# More string multiplication examples:
print("Python" * 3)  # Repeat "Python" 3 times
print("-" * 20)      # 20 dashes

print("\n" + "="*40)
print("LESSON 5: Type Conversion Functions in Detail")

# Examples of float() function
print("--- float() Examples ---")
print('float("27.5") =', float("27.5"), "type:", type(float("27.5")))
print('float("100") =', float("100"), "type:", type(float("100")))
print('float(25) =', float(25), "type:", type(float(25)))

# Examples of str() function  
print("\n--- str() Examples ---")
print('str(27.5) =', str(27.5), "type:", type(str(27.5)))
print('str(100) =', str(100), "type:", type(str(100)))
print('str(True) =', str(True), "type:", type(str(True)))

# Examples of int() function
print("\n--- int() Examples ---")
print('int("25") =', int("25"), "type:", type(int("25")))
print('int(27.9) =', int(27.9), "type:", type(int(27.9)), "← Notice: decimal cut off!")
print('int(27.1) =', int(27.1), "type:", type(int(27.1)), "← int() always cuts, never rounds")

print("\n--- Real ETL Example ---")
# This is what happens when you get data from APIs or CSV files
api_temperature = "28.3"  # Data from API comes as string
csv_humidity = "65"       # Data from CSV comes as string

print("Raw data from API:", api_temperature, "type:", type(api_temperature))
print("Raw data from CSV:", csv_humidity, "type:", type(csv_humidity))

# Convert for calculations
temp_for_calc = float(api_temperature)
humidity_for_calc = int(csv_humidity)

print("After conversion:", temp_for_calc, "type:", type(temp_for_calc))
print("After conversion:", humidity_for_calc, "type:", type(humidity_for_calc))

# Now we can do math:
average_temp = (temp_for_calc + 25.0) / 2
print("Average temperature:", average_temp)

print("\n" + "="*40)
print("LESSON 6: Decision Making with if/else")

# Basic if statement
temperature_now = 30.0
print(f"Current temperature: {temperature_now}°C")

if temperature_now > 25:
    print("It's hot! 🔥")
    print("Turn on the AC")

print("This line always runs (outside the if)")

print("\n--- if/else Example ---")
# if/else - choose between two options
humidity_now = 40

if humidity_now > 60:
    print("High humidity - feels sticky")
else:
    print("Normal humidity - feels comfortable")

print("\n--- if/elif/else Example ---")
# Multiple conditions with elif (else if)
weather_condition = "Rain"

if weather_condition == "Sunny":
    print("☀️ Great day for a walk!")
elif weather_condition == "Cloudy":
    print("☁️ Nice weather, might be cool")
elif weather_condition == "Rain":
    print("🌧️ Take an umbrella!")
else:
    print("🤷 Unknown weather condition")

print("\n--- Comparison Operators ---")
temp = 28
print(f"Temperature: {temp}")
print(f"temp > 25: {temp > 25}")    # Greater than
print(f"temp < 30: {temp < 30}")    # Less than  
print(f"temp == 28: {temp == 28}")  # Equal to (note: double ==)
print(f"temp != 25: {temp != 25}")  # Not equal to
print(f"temp >= 28: {temp >= 28}")  # Greater than or equal
print(f"temp <= 30: {temp <= 30}")  # Less than or equal

print("\n--- ETL Decision Example ---")
# This is like your weather ETL making decisions
api_response_code = 200
data_temperature = 35.5

print(f"API response code: {api_response_code}")
print(f"Temperature from API: {data_temperature}")

if api_response_code == 200:
    print("✅ API call successful!")
    
    if data_temperature > 30:
        print("🚨 HEAT ALERT: Temperature is very high!")
        print("📧 Sending alert email...")
    else:
        print("📊 Normal temperature, logging data...")
        
else:
    print("❌ API call failed - no data to process")

print("🏁 Weather monitoring complete")

print("\n" + "="*40)
print("LESSON 7: LOOPS - The Heart of Your Scheduler!")

# FOR LOOP - "Do this X times" or "Do this for each item"
print("--- for Loop Examples ---")

print("1. Simple counting:")
for i in range(5):  # range(5) = [0, 1, 2, 3, 4]
    print(f"Loop iteration {i}")

print("\n2. Processing a list of cities:")
cities = ["Tel Aviv", "Jerusalem", "Haifa", "Eilat"]
for city in cities:
    print(f"Checking weather for {city}")

print("\n3. Temperature readings over time:")
temperatures = [25.5, 27.2, 29.1, 26.8]
for temp in temperatures:
    if temp > 27:
        print(f"🔥 High temperature: {temp}°C")
    else:
        print(f"😊 Normal temperature: {temp}°C")

print("\n--- WHILE Loop Examples ---")
# WHILE LOOP - "Keep doing this WHILE condition is true"

print("1. Countdown:")
count = 5
while count > 0:
    print(f"Countdown: {count}")
    count = count - 1  # This is CRITICAL - change the condition!
print("🚀 Blast off!")

print("\n2. Wait for good weather:")
weather_status = "Rainy"
attempts = 0
while weather_status == "Rainy" and attempts < 3:
    attempts = attempts + 1
    print(f"Attempt {attempts}: Still {weather_status}, waiting...")
    # In real code, you'd check weather API here
    if attempts == 2:
        weather_status = "Sunny"  # Simulate weather change
print(f"Final weather: {weather_status}")

print("\n--- SCHEDULER LOOP EXPLAINED ---")
print("This is EXACTLY what your scheduler does:")

# Simplified version of your scheduler loop
import time
from datetime import datetime

check_count = 0
max_checks = 5  # We'll only do 5 checks for demo

print("Starting mini-scheduler...")
while check_count < max_checks:
    check_count = check_count + 1
    current_time = datetime.now()
    
    print(f"Check #{check_count} at {current_time.strftime('%H:%M:%S')}")
    
    # This is like schedule.run_pending()
    if current_time.second % 10 == 0:  # Every 10 seconds
        print("🎯 TIME TO RUN JOB!")
    else:
        print("⏰ Not time yet, waiting...")
    
    print("Sleeping for 1 second...")
    time.sleep(1)  # Wait 1 second
    print()

print("🏁 Mini-scheduler finished!")

print("\n--- Key Concepts You Now Understand ---")
print("✅ for loop: 'Do this for each item in a list'")
print("✅ while loop: 'Keep doing this while condition is true'")
print("✅ Loop + if: 'Check something each time through the loop'")
print("✅ Loop + sleep: 'Wait between each check'")
print("✅ Your scheduler: 'while True: check if time to run, sleep'")

print("\n🎉 YOU NOW UNDERSTAND YOUR SCHEDULER CODE!") 