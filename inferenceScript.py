from inference_sdk import InferenceHTTPClient
import supervision as sv
import cv2





CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="Your_API_Key"
)

result = CLIENT.infer('image.png', model_id="cmpe258-finalversion/1")
print(result)


labels = [item["class"] for item in result["predictions"]]

print(labels)

detections = sv.Detections.from_inference(result)
label_annotator = sv.LabelAnnotator()
bounding_box_annotator = sv.BoxAnnotator()


image = cv2.imread("image.png")

annotated_image = bounding_box_annotator.annotate(
    scene=image, detections=detections)
annotated_image = label_annotator.annotate(
    scene=annotated_image, detections=detections, labels=labels)

#matplot shit
newimg = sv.plot_image(image=annotated_image, size=(16, 16))


#saving the image itself using opencv
cv2.imwrite("Annotated.png", annotated_image)


