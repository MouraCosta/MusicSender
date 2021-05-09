import setuptools

setuptools.setup(name="music_sender", 
    packages=["music_sender"],
    version="1.0",
    author="moura",
    author_email="moura3950@gmail.com",
    description="A little app to send musics dinamically.",
    entry_points= {
        "console_scripts": [
            "ms_server = music_sender.server:main",
            "ms_client = music_sender.client:main"
        ]
    }
)
