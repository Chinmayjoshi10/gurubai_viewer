# GurbaniViewer

A fullscreen Gurbani viewer application for Raspberry Pi that displays Sikh scriptures with Gurmukhi, transliteration, and English translation.

## Features

- Fullscreen display optimized for Raspberry Pi
- Auto-scrolling every 5 seconds
- Pause/Resume functionality
- Previous/Next navigation
- Clean, modern interface
- Systemd service for autostart

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/GurbaniViewer.git
   cd GurbaniViewer
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Activate the virtual environment:
   ```bash
source venv/bin/activate
   ```

2. Run the application:
```bash
python src/main.py
```

## Building the Application

1. Make sure you're in the project directory and virtual environment is activated:
```bash
source venv/bin/activate
```

2. Run the build script:
```bash
bash deploy/build.sh
```

The executable will be created in the `dist` directory.

## Setting up as a Service

1. Copy the service file:
   ```bash
   sudo cp deploy/gurbani-viewer.service /etc/systemd/system/
   ```

2. Reload systemd:
   ```bash
   sudo systemctl daemon-reload
```

3. Enable and start the service:
```bash
   sudo systemctl enable gurbani-viewer.service
   sudo systemctl start gurbani-viewer.service
   ```

4. Check the status:
   ```bash
   sudo systemctl status gurbani-viewer.service
   ```

## Logs

- Application logs: `/var/log/gurbani-viewer.log`
- Error logs: `/var/log/gurbani-viewer-error.log`

## Development

To run tests:
```bash
pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 