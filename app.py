import time
import numpy as np
import pandas as pd
import edgeiq
"""
Use object detection to detect objects in the frame in realtime. The
types of objects detected can be changed by selecting different models.

To change the computer vision model, follow this guide:
https://alwaysai.co/docs/application_development/changing_the_model.html

To change the engine and accelerator, follow this guide:
https://alwaysai.co/docs/application_development/changing_the_engine_and_accelerator.html

To install app dependencies in the runtime container, list them in the
requirements.txt file.
"""


def main():
    obj_detect = edgeiq.ObjectDetection("alwaysai/ssd_mobilenet_v2_coco_2018_03_29")
    obj_detect.load(engine=edgeiq.Engine.DNN_OPENVINO)

    print("Loaded model:\n{}\n".format(obj_detect.model_id))
    print("Engine: {}".format(obj_detect.engine))
    print("Accelerator: {}\n".format(obj_detect.accelerator))
    print("Labels:\n{}\n".format(obj_detect.labels))

    seconds = int (0)
    minutes = int (0)
    hours = int (0)
    timer = int
    
    df = pd.DataFrame(
        [['alwaysAI_MAU',0,0,0]],
        index = [0],
        columns = ['Session', 'Hours', 'Minutes', 'Seconds'])
    
    fps = edgeiq.FPS()

    try:
        with edgeiq.WebcamVideoStream(cam=0) as video_stream, \
                edgeiq.Streamer() as streamer:
            # Allow Webcam to warm up
            time.sleep(2.0)
            fps.start()

            # loop detection
            while True:
                frame = video_stream.read()
                results = obj_detect.detect_objects(frame, confidence_level=.5)
                frame = edgeiq.markup_image(
                        frame, results.predictions, colors=obj_detect.colors)

                # Generate text to display on streamer
                text = ["Model: {}".format(obj_detect.model_id)]
                text.append(
                        "Inference time: {:1.3f} s".format(results.duration)) 

                text.append("Timer: ")
                text.append(timer)
                
                text.append("Objects:")

                for prediction in results.predictions:
                    text.append("{}: {:2.2f}%".format(
                        prediction.label, prediction.confidence * 100))

                    if prediction.label == 'cell phone ':
                        seconds = seconds + 1
                        if seconds > 59:
                            seconds = 0
                            minutes = minutes + 1
                        if minutes > 59:
                            minutes = 0
                            hours = hours + 1
                        time.sleep(1)    
                        timer = hours , minutes , seconds

                        df.at[0, 'Hours'] = hours
                        df.at[0, 'Minutes'] = minutes
                        df.at[0, 'Seconds'] = seconds
                        print(df)

                streamer.send_data(frame, text)
                fps.update()

                if streamer.check_exit():
                    break

    finally:
        fps.stop()
        print("elapsed time: {:.2f}".format(fps.get_elapsed_seconds()))
        print("approx. FPS: {:.2f}".format(fps.compute_fps()))

        print("Program Ending")

if __name__ == "__main__":
    main()
