import cv2


class VehicleDetector:

    def __init__(self):
        # Load YOLOv4 object detection model
        net = cv2.dnn.readNet(
            "yolov4.weights",
            "yolov4.cfg"
        )
        self.model = cv2.dnn_DetectionModel(net)
        self.model.setInputParams(size=(832, 832), scale=1 / 255)

        # Define classes to detect (classes containing vehicles only)
        self.classes_allowed = [2, 3, 5, 6, 7]

    def detect_vehicles(self, img):
        # Detect objects in the input image
        vehicles_boxes = []
        class_ids, scores, boxes = self.model.detect(img, nmsThreshold=0.4)
        for class_id, score, box in zip(class_ids, scores, boxes):
            if score < 0.5:
                # Skip detection with low confidence
                continue

            if class_id in self.classes_allowed:
                # Add bounding box of vehicle to the list of detected vehicles
                vehicles_boxes.append(box)

        return vehicles_boxes
