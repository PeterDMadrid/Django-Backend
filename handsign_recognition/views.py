import os
import csv
import copy
import itertools
import numpy as np
import tensorflow as tf
import cv2 as cv
import mediapipe as mp

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage

class KeyPointClassifier:
    def __init__(self):
        # Adjust the path to match your Django project structure
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, 'models', 'keypoint_classifier.tflite')
        
        try:
            self.interpreter = tf.lite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    def __call__(self, landmark_list):
        try:
            # Ensure the input is a numpy array with correct shape and type
            input_data = np.array([landmark_list], dtype=np.float32)
            
            # Set the tensor to the input data
            input_details_tensor_index = self.input_details[0]['index']
            self.interpreter.set_tensor(input_details_tensor_index, input_data)
            
            # Run inference
            self.interpreter.invoke()
            
            # Get the output tensor
            output_details_tensor_index = self.output_details[0]['index']
            result = self.interpreter.get_tensor(output_details_tensor_index)
            
            # Get the index of the highest probability
            result_index = np.argmax(np.squeeze(result))
            confidence = np.max(np.squeeze(result))
            
            return result_index, confidence
        
        except Exception as e:
            print(f"Error during prediction: {e}")
            return None, 0.0

# MediaPipe Hands setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# Initialize classifier
keypoint_classifier = KeyPointClassifier()

# Load labels
def load_labels():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        label_path = os.path.join(base_dir, 'models', 'keypoint_classifier_label.csv')
        with open(label_path, encoding='utf-8-sig') as f:
            keypoint_classifier_labels = csv.reader(f)
            return [row[0] for row in keypoint_classifier_labels]
    except FileNotFoundError:
        print("Label file not found!")
        return ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']

keypoint_classifier_labels = load_labels()

def calc_bounding_rect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]
    landmark_array = np.empty((0, 2), int)

    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        landmark_point = [np.array((landmark_x, landmark_y))]
        landmark_array = np.append(landmark_array, landmark_point, axis=0)

    x, y, w, h = cv.boundingRect(landmark_array)
    return [x, y, x + w, y + h]

def calc_landmark_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]
    landmark_point = []

    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        landmark_point.append([landmark_x, landmark_y])

    return landmark_point

def pre_process_landmark(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)

    # Convert to relative coordinates
    base_x, base_y = temp_landmark_list[0][0], temp_landmark_list[0][1]
    for index, point in enumerate(temp_landmark_list):
        temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
        temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

    # Convert to a one-dimensional list
    temp_landmark_list = list(itertools.chain.from_iterable(temp_landmark_list))

    # Normalization
    max_value = max(list(map(abs, temp_landmark_list)))
    def normalize_(n):
        return n / max_value if max_value != 0 else 0
        
    temp_landmark_list = list(map(normalize_, temp_landmark_list))
    return temp_landmark_list

@csrf_exempt
def predict(request):
    if request.method != 'POST' or not request.FILES.get('image'):
        return JsonResponse({'error': 'Invalid request'}, status=400)

    try:
        # Get and save the image temporarily
        image_file = request.FILES['image']
        image_path = default_storage.save('temp_hand.jpg', image_file)
        
        # Read and process image
        image = cv.imread(default_storage.path(image_path))
        if image is None:
            raise ValueError("Failed to read image")
            
        image = cv.flip(image, 1)  # Mirror display
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        
        if not results.multi_hand_landmarks:
            return JsonResponse({'error': 'No hand detected'}, status=400)
            
        # Process landmarks
        hand_landmarks = results.multi_hand_landmarks[0]
        handedness = results.multi_handedness[0].classification[0].label
        
        # Calculate landmark coordinates
        landmark_list = calc_landmark_list(image, hand_landmarks)
        
        # Process landmarks for classification
        processed_landmark_list = pre_process_landmark(landmark_list)
        
        # Get prediction and confidence
        hand_sign_id, confidence = keypoint_classifier(processed_landmark_list)
        
        # Calculate bounding box
        brect = calc_bounding_rect(image, hand_landmarks)
        
        # Debugging prints
        print(f"Processed Landmarks: {processed_landmark_list}")
        print(f"Hand Sign ID: {hand_sign_id}")
        print(f"Confidence: {confidence}")
        
        response_data = {
            'prediction': int(hand_sign_id) if hand_sign_id is not None else -1,
            'label': keypoint_classifier_labels[hand_sign_id] 
                    if hand_sign_id is not None and 0 <= hand_sign_id < len(keypoint_classifier_labels) 
                    else 'Unknown',
            'handedness': handedness,
            'bounding_box': brect,
            'confidence': float(confidence)
        }
        
    except Exception as e:
        print(f"Prediction Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
        
    finally:
        # Clean up
        try:
            default_storage.delete(image_path)
        except:
            pass
            
    return JsonResponse(response_data)
