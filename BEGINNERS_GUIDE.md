# Observer: Beginner's Setup Guide 🧩

Hi there. If you're a parent, therapist, or educator who wants to use Observer but has never used a "terminal" or "command line" before, this guide is for you. We’re going to take this one step at a time.

### What you will need:
- A computer (Laptop or Desktop) with a webcam.
- About 15-20 minutes of time.
- An internet connection (just for the initial setup).

---

## Step 1: Install the "Engine" (Python)

Observer is written in a language called **Python**. You need to install it so your computer knows how to read the code.

1. Go to [Python.org Downloads](https://www.python.org/downloads/).
2. Click the big button that says **"Download Python 3.xx.x"**.
3. **Important for Windows Users:** When the installer starts, make sure you check the box that says **"Add Python to PATH"** at the bottom. Then click "Install Now."

---

## Step 2: Install the "AI Library" (Ollama)

Observer uses "Local AI," which means the brain of the system runs right on your computer. We use a tool called **Ollama** to manage those brains.

1. Go to [Ollama.com](https://ollama.com/) and click **Download**.
2. Run the installer like any other app.
3. Once it's installed, you won't see a window pop up, but you'll see a small llama icon in your taskbar (near the clock).

---

## Step 3: Download the Observer Code

1. At the top of this GitHub page, click the green button that says **"<> Code"**.
2. Click **"Download ZIP"**.
3. Find that ZIP file in your Downloads folder, right-click it, and select **"Extract All"** (or "Unzip"). 
4. Move the folder to somewhere easy to find, like your Desktop.

---

## Step 4: Open the Command Line

Now we need to talk to the computer directly. 

- **On Windows:** Press the `Windows Key`, type `cmd`, and press Enter.
- **On Mac:** Press `Command + Space`, type `Terminal`, and press Enter.

You should see a black window with some text. This is where we will type our commands.

---

## Step 5: Navigate to the Folder

We need to tell the black window to "look" inside the Observer folder you just unzipped.

1. Type `cd ` (make sure there is a space after `cd`).
2. Drag the Observer folder from your Desktop right into the black window. It will automatically type the path for you.
3. Press **Enter**.

---

## Step 6: Install the Requirements

Copy and paste the following line into the black window and press **Enter**:

```bash
pip install -r requirements.txt
```

*Wait for it to finish. You’ll see a bunch of bars filling up. This is installing the specific tools Observer needs to "see" and "hear."*

---

## Step 7: Download the AI "Brains"

Observer needs three specific models to work. Copy and paste these three lines into the black window, one at a time, pressing Enter after each one:

```bash
ollama pull moondream:latest
ollama pull qwen3-vl:8b
ollama pull rnj-1:8b
```

*Note: The first one is small and fast. The second two are larger and might take a few minutes to download depending on your internet.*

---

## Step 8: Run Observer!

You are ready. Type this into the black window and press **Enter**:

```bash
python main.py
```

### What happens next?
1. Your webcam light should turn on. 
2. The window will say something like `Uvicorn running on http://127.0.0.1:8001`.
3. Open your web browser (Chrome or Safari) and go to this address:
   `http://localhost:8001/?token=test_token`

---

## Troubleshooting Tips 💡

- **"Command not found"**: If you get this when typing `python`, try typing `python3` instead.
- **Webcam not working**: Make sure no other apps (like Zoom or Teams) are using your camera.
- **It's slow**: The first time the AI "thinks" about a video, it might take a few minutes. This is normal for home computers!

**Need more help?** If this is still overwhelming, please see the **Specialist Support** section in the main README. We are happy to help you get this running for your family.
