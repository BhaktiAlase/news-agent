# news-agent

Lightweight AI-driven news briefing that fetches headlines, summarizes them with an LLM and sends a WhatsApp message via Twilio. Configuration is stored in a local `.env` file (see `.env.example`).

## Getting started

1. **Clone the repository**
   ```bash
   git clone https://github.com/BhaktiAlase/news-agent.git
   cd news-agent
   ```
2. **Install dependencies**
   ```bash
   python -m pip install -r requirements.txt
   ```
3. **Create your environment file**
   ```bash
   cp .env.example .env
   # edit .env and fill in your own API keys, tokens, WhatsApp numbers, etc.
   ```
4. **Run a quick test**
   ```bash
   python main.py --once --dry-run
   ```

## Running continuously (always-on)

The agent itself contains a scheduler (`schedule` library) and will wake up every day at the time defined by `SCHEDULE_TIME`/`TIMEZONE` in `.env`. To keep the process alive, you simply need to run `python main.py` inside some long‑lived environment. Options include:

- **Local machine / development**
  - Start it in a terminal and leave it open; `Ctrl+C` stops the agent.
  - On Windows you can create a **Task Scheduler** task that runs at logon or system start and keeps the process running.
  - On macOS/Linux use `nohup`, `screen`, `tmux`, or a `systemd` service:
    ```ini
    # /etc/systemd/system/news-agent.service
    [Unit]
    Description=AI News Agent

    [Service]
    WorkingDirectory=/path/to/news-agent
    ExecStart=/usr/bin/python3 main.py
    Restart=always
    User=youruser

    [Install]
    WantedBy=multi-user.target
    ```

- **Container / cloud**
  - Build a Docker image and use a restart policy (`--restart unless-stopped`).
  - Deploy on a small VM or serverless container; the container just runs `python main.py` indefinitely.

- **CI platforms / platforms with jobs**
  - Use GitHub Actions `schedule` trigger to run `python main.py --once` daily.
  - Use Heroku/Render with a worker dyno running the script.

Whichever method you choose, the agent will log each run under `logs/` and automatically send WhatsApp messages at the configured time.

## Command-line options

Run `python main.py --help` for details (one‑shot mode, dry‑run, overrides for count, country, category, etc.).

---

*Note*: keep `.env` private; it is ignored by git. Only commit `.env.example` with placeholders.
