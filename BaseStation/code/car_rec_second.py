from torchvision.models.detection import RetinaNet_ResNet50_FPN_V2_Weights
from torchvision.models.detection import retinanet_resnet50_fpn_v2

IMG_DIR = "Basestation_Images\\*.jpg"


class VehicleCounting2:

    @staticmethod
    def vehicle_count_2(images_details, img_number):
        # Dictionary to store vehicle counts for each image
        vehicle_count_dict = {}
        counter = 0

        for img in images_details:
            # Determine image name
            if not img_number:
                img_name = f"pic{counter}"
            else:
                img_name = f"pic{img_number + counter}"

            # Load pre-trained RetinaNet model
            weights = RetinaNet_ResNet50_FPN_V2_Weights.DEFAULT
            model = retinanet_resnet50_fpn_v2(weights=weights, score_thresh=0.35)
            # Put the model in inference mode
            model.eval()

            # Preprocess image and perform prediction

            # Get the transforms for the model's weights
            preprocess = weights.transforms()
            # Preprocess the image using the transforms from our weights, create a batch and run inference
            batch = [preprocess(img)]
            prediction = model(batch)[0]

            # Extract predicted labels and count vehicles
            labels = [weights.meta["categories"][i] for i in prediction["labels"]]
            # Extract the labels with respect to the metadata from the weights
            vehicle_count = len([i for i in labels if i == "car"])

            # Update total count for current image
            vehicle_count_dict[img_name] = vehicle_count
            counter += 1

        return vehicle_count_dict
