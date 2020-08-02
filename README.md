# Hayato Bot
![Python application](https://github.com/deadshot465/hayato/workflows/Python%20application/badge.svg)

Hayato bot is an experimental bot written in [Python](https://www.python.org/) with the awesome [discord.py](https://github.com/Rapptz/discord.py). It's inspired by the anime 新幹線変形ロボ シンカリオン (Shinkansen Henkei Robo Shinkalion, a.k.a. Shinkalion). You can find more information about Shinkalion [here](https://www.shinkalion.com/).

## Contents
- [Project Setup](#project-setup)
  - [Bot application](#bot-application)
  - [Why Python](#why-python)
  - [Setup steps](#setup-steps)
- [Disclaimer](#disclaimer)

## Project Setup
Hayato is written in Python. As the best practice, Hayato utilizes Python's virtual environment to install dependencies and packages. As a result, users have to create a virtual environment for the code, since the repository doesn't contain the virtual environment and required packages.

### Bot application
A Discord bot is meant to provide interactive experiences for members in a guild (a.k.a. server). In Hayato's case, Hayato can provide some useful functionalities, and specifically information on train vehicles and metro lines, particularly those in Japan.

### Why Python
The choice to make use of Python instead of other languages is simple: simplicity. Python is very good for programming beginners and prototyping. Although it might be the fastest and the most performant programming language, the nature of it being a interpreted language make it fast to execute codes and see the results immediately, since it doesn't require compilation.

### Setup steps
As Hayato uses virtual environment in Python, users have to first clone the repository, creating a virtual environment, and install required dependencies. The detailed instructions are as following:
1. If you don't have Python installed, first get Python from the [official website](https://www.python.org/) and choose applicable installation for your operating system. If you are on Windows, **make sure to check the option to add Python executable to your PATH.** 64 bit version is recommended.
2. In command line (PowerShell on Windows, zsh/bash on macOS and UNIX-like operating systems), type in the following command to check if Python is successfully installed and the version is the latest version (3.8.4 when this README.md is written.)<br />
    On Windows:
    ```bash
    py -3 -V
    ```
    On macOS/UNIX-like:
    ```bash
    python -V
    -- OR --
    python3.8 -V
    ```
3. Supposed you don't have a dedicated virtual environment folder yet, you can make one using this command:
    ```bash
    mkdir .virtualenvs
    ```
4. Inside the .virtualenvs folder, clone the repository:
    ```bash
    git clone https://github.com/deadshot465/hayato.git
    ```
5. Create a new virtual environment inside the `hayato` folder.<br />
    On Windows:
    ```bash
    py -3 -m venv hayato
    ```
    On macOS/UNIX-like:
    ```bash
    python -m venv hayato
    -- OR --
    python3.8 -m venv hayato
    ```
6. Activate the virtual environment.<br />
    On Windows:
    ```bash
    cd hayato
    ./Scripts/activate
    ```
    On macOS/UNIX-like:
    ```bash
    cd hayato
    source ./bin/activate
    ```
7. Once you see there is a `(hayato)` prefix in command line, you can start installing required packages:
    ```bash
    pip install discord.py[voice]
    ```
8. Once discord.py is installed, run the following command to get Hayato online:
    ```bash
    python main.py
    ```
## Disclaimer
Hayato is a bot inspired by Shinkalion. All rights to the character and the story, and all images of trains and vehicles belong to associated parties.