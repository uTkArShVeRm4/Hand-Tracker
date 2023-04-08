import uuid
from pathlib import Path
import requests
import av
import cv2
import streamlit as st
from aiortc.contrib.media import MediaRecorder
from streamlit_webrtc import WebRtcMode, webrtc_streamer


url = 'https://b7cf-150-129-168-166.ngrok-free.app/upload'


first_threshold = st.slider("First Threshold", min_value = 0, max_value = 255, step = 1)
second_threshold = st.slider("Second Threshold", min_value = 0, max_value = 255, step = 1)

canny = st.checkbox("Enable Canny Filter")

def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
    img = frame.to_ndarray(format="bgr24")
    # perform edge detection
    if canny:
        img = cv2.cvtColor(cv2.Canny(img, first_threshold, second_threshold), cv2.COLOR_GRAY2BGR)

    return av.VideoFrame.from_ndarray(img, format="bgr24")


RECORD_DIR = Path("./records")
RECORD_DIR.mkdir(exist_ok=True)


def app():
    if "prefix" not in st.session_state:
        st.session_state["prefix"] = str(uuid.uuid4())
    prefix = st.session_state["prefix"]
    in_file = RECORD_DIR / f"{prefix}_input.mp4"

    def in_recorder_factory() -> MediaRecorder:
        return MediaRecorder(
            str(in_file), format="mp4"
        )  # HLS does not work. See https://github.com/aiortc/aiortc/issues/331

    webrtc_streamer(
        key="record",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={
            "video": {
            "width": {"min": 800, "ideal": 1280}
        },
            "audio": True,
        },
        video_frame_callback=video_frame_callback,
        in_recorder_factory=in_recorder_factory
    )

    if in_file.exists():
        if st.button("Click me after you are done"):    
            st.write("You are poggies fr fr no cap")
            with in_file.open("rb") as f:
                # st.download_button(
                #     "Download the recorded video without video filter", f, "input.mp4"
                # )
                response = requests.post(url, files={'file': f})
    # if out_file.exists():
    #     with out_file.open("rb") as f:
    #         st.download_button(
    #             "Download the recorded video with video filter", f, "output.mp4"
    #         )
    #         response = requests.post(url, files={'file': f})


if __name__ == "__main__":
    app()