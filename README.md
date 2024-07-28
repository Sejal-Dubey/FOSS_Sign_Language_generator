# FOSS_Sign_Language_generator
# Sign Language Helper

## Introduction

Sign Language Helper is a web application designed to assist in learning and understanding sign language. The application converts videos into sign language and provides visual representations of the signs.

## Features

- Upload video and convert it to sign language.
- Display generated images of sign language for each letter.
- Download the processed video with captions.

## Installation

To run this project locally, follow these steps:

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/your-repository-name.git
    cd your-repository-name
    ```

2. Set up a virtual environment and activate it:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Apply migrations:

    ```bash
    python manage.py migrate
    ```

5. Run the development server:

    ```bash
    python manage.py runserver
    ```

## Usage

1. Open your web browser and go to `http://127.0.0.1:8000/`.
2. Upload a video file.
3. Wait for the processing to complete.
4. View and download the processed video.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m "Add new feature"`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a Pull Request.

## License

This project is licensed under the MIT License.

## Video Demo

[Link to video demo](https://your-demo-video-link)
