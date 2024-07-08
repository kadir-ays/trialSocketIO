import threading
import asyncio
from datetime import datetime
import socketio
from aiohttp import web
from huskylib import HuskyLensLibrary

# Initialize HuskyLens library for SERIAL communication on /dev/ttyUSB0 at 3000000 baudrate
hl = HuskyLensLibrary("SERIAL", "/dev/ttyUSB0", 3000000)

# Initialize Socket.IO server with CORS policy
sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

# Define function to continuously read from HuskyLens and emit data via Socket.IO
async def listen_and_emit():
    while True:
        try:
            response = hl.requestAll()
            if response:
                current_time = datetime.now().strftime('%H:%M:%S.%f')[:-4]
                data = {'time': current_time, 'ID': response[0].ID}  # Assuming response[0] has ID attribute
                print(data)
                await sio.emit('data', data)
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Error in reading response: {e}")
            await asyncio.sleep(1)  # Wait and retry on error

# Function to start the listener in a new thread with its own event loop
def start_listener():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(listen_and_emit())

# Start the listener in a separate thread
listener_thread = threading.Thread(target=start_listener, daemon=True)
listener_thread.start()

# Define an HTTP handler for the aiohttp web application
async def index(request):
    return web.FileResponse('./public/index.html')  # Adjust path as per your actual directory structure

# Add a route for the index page
app.router.add_get('/', index)

# Run the aiohttp web application
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)
