Explanation of code organization:
The first section contains methods used to get features.
The next section loads a pre-trained classifier I checked in (using this exact code) and uses it to generate predictions for a set of images in a given folder.
The next section loads pre-generated features, since they're fairly slow to generate, and trains a classifier. Contains code to show accuracy, important features, ect.
The final section will actually retrieve the features from the given training data. Its fairly slow. 

Explanation of features:
I broke features into three categories: color-related, shape-related, and texture-related.
Color related features are the mean of the rgb or hsv channels for the entire image, or for rgb the ratio of the mean of the 'background' versus the 'center' defined by a square region in the center of the image.
Shape features use a variety of different skimage functions that give information about keypoints, shapes, edges, and the like to generate info about the image, and reports them all relative to image size.
Texture features use two methods to get information about features that I think describe textural qualities of the image. First, it uses the histogram of oriented gratings to find information about orientations in blocks of the image. From these, it gets information about the variance, strength, and relative consistency of orientations and the like. Texture features also use the grey level co-occurence matrix properties algorithm from skimage. This describes the way that grey pixels of the same intensity co-occur at a given offsets. This is also thought to describe some textural properties.


Question answers/commentary on accuracy, important features:
My estimated mean accuracy was 33%. If you take chance to be always guessing the most commonly occuring class, airplanes, that gives about 13% accuracy. Thus, I'm a lot more accurate than random guessing.
The most important features vary slightly from fit to fit, but generally are the glcm dissimilarity, the ratio of mean green channel values in the surround vs the center, and the ratio of blue channel values in the surround vs the center.
