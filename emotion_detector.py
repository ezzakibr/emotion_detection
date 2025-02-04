import cv2
import numpy as np
import traceback
from kafka import KafkaProducer
import json
import datetime

# Define emotions and setup Kafka producer
EMOTIONS = ['Neutral', 'Happy', 'Sad']
FONT = cv2.FONT_HERSHEY_SIMPLEX

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

def detect_emotion(net, img, x1, y1, x2, y2):
    try:
        padding = 10
        h, w, _ = img.shape
        x1, y1 = max(0, x1 - padding), max(0, y1 - padding)
        x2, y2 = min(w, x2 + padding), min(h, y2 + padding)

        face = img[y1:y2, x1:x2]
        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        resized_face = cv2.resize(gray, (64, 64))
        processed_face = resized_face.reshape(1, 1, 64, 64).astype(np.float32)

        net.setInput(processed_face)
        output = net.forward()

        expanded = np.exp(output - np.max(output))
        probabilities = expanded / expanded.sum()
        prob = np.squeeze(probabilities)

        emotion_index = prob.argmax()
        if emotion_index >= len(EMOTIONS):
            return None
            
        if prob[emotion_index] > 0.4 and EMOTIONS[emotion_index] == "Sad":
            predicted_emotion = "Sad"
        elif prob[emotion_index] > 0.5:
            predicted_emotion = EMOTIONS[emotion_index]
        else:
            predicted_emotion = "Neutral"

        cv2.putText(img, predicted_emotion, (x1, y1 - 10), FONT, 0.8, (0, 255, 0), 2)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        return predicted_emotion

    except Exception as e:
        print("Error in emotion detection:", e)
        return None

def main():
    model_path = './emotion-ferplus-8.onnx'
    net = cv2.dnn.readNetFromONNX(model_path)

    cascade_path = "./haarcascade_frontalface_default.xml"
    fd = cv2.CascadeClassifier(cascade_path)

    if fd.empty():
        raise ValueError("Error: Unable to load XML file at {}".format(cascade_path))

    cap = cv2.VideoCapture(0)  # Using default webcam

    if not cap.isOpened():
        print("Error: Unable to open webcam.")
        return

    print("Webcam ready.")

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error capturing image.")
                break

            frame = cv2.resize(frame, (480, 360))
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = fd.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            for (x, y, w, h) in faces:
                emotion = detect_emotion(net, frame, x, y, x+w, y+h)
                
                if emotion:
                    face_data = {
                        'timestamp': datetime.datetime.now().isoformat(),
                        'bbox_x': int(x),
                        'bbox_y': int(y),
                        'bbox_width': int(w),
                        'bbox_height': int(h),
                        'emotion': emotion
                    }
                    
                    try:
                        producer.send('face-emotions', face_data)
                        producer.flush()
                    except Exception as e:
                        print(f"Error sending to Kafka: {e}")

            cv2.imshow("Emotion Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Process interrupted by user.")
    except Exception as e:
        print(f"Error in main loop: {e}")
        traceback.print_exc()
    finally:
        cap.release()
        cv2.destroyAllWindows()
        producer.close()

if __name__ == "__main__":
    main()