import random
import time
import json
import threading
from datetime import datetime
import socketio
from huskylib import HuskyLensLibrary

# HuskyLens initialization
hl = HuskyLensLibrary("SERIAL", "/dev/ttyUSB0", 3000000)

# Initialize Socket.IO server
sio = socketio.AsyncServer(async_mode='aiohttp')
app = socketio.ASGIApp(sio, static_files={
    '/': './public/'  # Ensure you have a public directory for your client HTML file
})

# Define a function to listen and emit data
async def listen_and_emit():
    while True:
        try:
            response = hl.requestAll() 
            if response:
                current_time = datetime.now().strftime('%H:%H:%S:%f')[:-4]
                data = {'time': current_time, 'ID': response[0].ID}
                await sio.emit('data', data)
            await sio.sleep(0.1) 
        except Exception as e:
            print(f"Error in reading response: {e}")
            break

# Run the listening and emitting in a separate thread
listener_thread = threading.Thread(target=lambda: sio.start_background_task(listen_and_emit), daemon=True)
listener_thread.start()

# Start the server
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
