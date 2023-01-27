from torchvision.models.detection import retinanet_resnet50_fpn_v2, RetinaNet_ResNet50_FPN_V2_Weights

IMG_DIR = "C:\\Users\\user\\PycharmProjects\\A_D_E_Origin\\Microservices\\BaseStation\\Basestation_Images\\*.jpg"


class VehicleCounting2:

    @staticmethod
    def vehicle_count_2(images_details, img_number):
        vehicle_count_dict = {}
        counter = 0

        for img in images_details:

            if not img_number:
                img_name = f"pic{counter}"
            else:
                img_name = f"pic{img_number + counter}"

            weights = RetinaNet_ResNet50_FPN_V2_Weights.DEFAULT
            model = retinanet_resnet50_fpn_v2(weights=weights, score_thresh=0.35)
            model.eval()

            preprocess = weights.transforms()
            batch = [preprocess(img)]
            prediction = model(batch)[0]

            labels = [weights.meta["categories"][i] for i in prediction["labels"]]
            vehicle_count = len([i for i in labels if i == "car"])
            vehicle_count_dict[img_name] = vehicle_count
            counter += 1

            # box = draw_bounding_boxes(img, boxes=prediction["boxes"],
            #                           labels=labels,
            #                           colors="cyan",
            #                           width=2)
            #
            # im = to_pil_image(box.detach())
            #
            # fig, ax = plt.subplots(figsize=(16, 12))
            # ax.imshow(im)
            # plt.show()

        return vehicle_count_dict
